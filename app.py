from flask import Flask, render_template, jsonify, send_file, request
import subprocess
import os
import datetime
import zipfile
import io

app = Flask(__name__)

SCRIPTS = [
    'request_data.py',
    'brændeovn.py',
    'building_area.py',
    'construction_years.py',
    'energy_label_age.py',
    'energy_labels_year_of_contruction.py',
    'energy_labels.py',
    'heating_matrix.py',
    'supplementary_heating.py',
    'unit_usage_140_vs_energy_label_validity.py',
    'units_usage_energy_label_validity.py'
]

SCRIPT_DESCRIPTIONS = {
"request_data.py": "Fetches the latest data from Elasticsearch",
"brændeovn.py": "Analyzes wood stove data",
"building_area.py": "Processes building area information",
"construction_years.py": "Analyzes building construction years",
"energy_label_age.py": "Examines the age of energy labels",
"energy_labels_year_of_contruction.py": "Correlates energy labels with construction years",
"energy_labels.py": "Provides an overview of energy label distribution",
"heating_matrix.py": "Analyzes heating installation types and mediums",
"supplementary_heating.py": "Examines supplementary heating systems",
"unit_usage_140_vs_energy_label_validity.py": "Analyzes energy label validity for specific unit usage",
"units_usage_energy_label_validity.py": "Examines energy label validity across different unit usages",
"Download All Results" : "Downloads all .py except calling the request_data.py",
"Run All Scripts" : "Runs every with request_data.py running as the first for getting data"
}

last_run_times = {}

@app.route('/')
def index():
    return render_template('index.html', scripts=SCRIPTS, descriptions=SCRIPT_DESCRIPTIONS, last_run_times=last_run_times)

@app.route('/run/<script_name>')
def run_script(script_name):
    if script_name not in SCRIPTS and script_name != 'all':
        return jsonify({'error': 'Invalid script name'}), 400
    
    try:
        if script_name == 'all':
            subprocess.run(['python', 'request_data.py'], check=True)
            last_run_times['request_data.py'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for script in SCRIPTS[1:]:
                subprocess.run(['python', script], check=True)
                last_run_times[script] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            subprocess.run(['python', script_name], check=True)
            last_run_times[script_name] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return jsonify({'message': f'Script {script_name} executed successfully'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Script {script_name} failed: {str(e)}'}), 500

@app.route('/download/<script_name>')
def download_file(script_name):
    file_name = f"{script_name.replace('.py', '')}.xlsx"
    file_path = os.path.join('output', file_name)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/download_all')
def download_all():
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for root, dirs, files in os.walk('output'):
            for file in files:
                zf.write(os.path.join(root, file), file)
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='all_results.zip'
    )

@app.route('/log/<script_name>')
def get_log(script_name):
    log_file = f"logs/{script_name}.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            return file.read()
    else:
        return "No log available", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)