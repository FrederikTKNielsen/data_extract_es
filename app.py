from flask import Flask, render_template, jsonify, send_file, abort, request
import subprocess
import os
import traceback
import logging
import json
import io
import zipfile

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

SCRIPTS = [
    'request_data.py',
    'brændeovn_pejs.py',
    'address_brændeovn_pejs_query.py',
    'building_area.py',
    'address_building_area_query.py',
    'building_area_small.py',
    'address_building_area_small_query.py',
    'unit_areas.py',
    'address_unit_areass_query.py',
    'construction_years.py',
    'address_construction_years_query.py',
    'year_extension_vs_construction.py',
    'address_year_extension_vs_construction_query.py',
    'energy_label_age.py',
    'address_energy_label_age_query.py',
    'energy_labels_year_of_construction.py',
    'address_energy_labels_year_of_construction_query.py',
    'energy_labels.py',
    'address_energy_labels_query.py',
    'heating_matrix.py',
    'address_heating_matrix_query.py',
    'supplementary_heating.py',
    'address_supplementary_heating_query.py',
    'unit_usage_140_vs_energy_label_validity.py',
    'address_unit_usage_140_vs_energy_label_validity_query.py',
    'units_usage_energy_label_validity.py',
    'address_units_usage_energy_label_validity_query.py',
    'units_usage_all_energy_label_validity.py',
    'address_units_all_usage_energy_label_validity_query.py',
    'null_heating_installation.py',
    'address_null_heating_installation_query.py',
    '9_heating_installation_null_mediums.py',
    'address_9_heating_installation_null_mediums_query.py',
    'buildings_1000.py',
    'address_buildings_1000_query.py',
    'large_buildings_energy_labels.py',
    'address_large_buildings_energy_labels_query.py',
]

# Map scripts to their required query files
SCRIPT_QUERIES = {
    'unit_areas.py': ['unit_areas_below_900.json', 'unit_areas_above_900.json'],
    # Add other scripts here if they have special query requirements
    # For all other scripts, we'll assume they use a single query file with the same name
}

SCRIPT_DESCRIPTIONS = {
    "request_data.py": "Fetches the latest data from Elasticsearch",
    "brændeovn_pejs.py": "Analyzes wood stove data",
    "address_brændeovn_pejs_query.py": "Processes wood stove data address information",
    "building_area.py": "Processes building area information",
    "address_building_area_query.py": "Processes building area address information",
    "building_area_small.py": "Processes small building area information",
    "address_building_area_small_query.py": "Processes small building area address information",
    "unit_areas.py": "Processes unit area information",
    "address_unit_areass_query.py": "Processes unit area address information",
    "construction_years.py": "Analyzes building construction years",
    "address_construction_years_query.py": "Processes construction year address information",
    "year_extension_vs_construction.py": "Analyzes year of extension vs construction of year",
    "address_year_extension_vs_construction_query.py": "Processes year of extension vs construction of year address information",
    "energy_label_age.py": "Examines the age of energy labels",
    "address_energy_label_age_query.py": "Processes energy label age address information",
    "energy_labels_year_of_construction.py": "Correlates energy labels with construction years",
    "address_energy_labels_year_of_construction_query.py": "Processes energy labels year of construction address information",
    "energy_labels.py": "Provides an overview of energy label distribution",
    "address_energy_labels_query.py": "Processes energy label distribution address information",
    "heating_matrix.py": "Analyzes heating installation types and mediums",
    "address_heating_matrix_query.py": "Processes heating matrix address information",
    "supplementary_heating.py": "Examines supplementary heating systems",
    "address_supplementary_heating_query.py": "Processes supplementary heating address information",
    "unit_usage_140_vs_energy_label_validity.py": "Analyzes energy label validity for specific unit usage [140]",
    "address_unit_usage_140_vs_energy_label_validity_query.py": "Processes unit usage 140 vs energy label validity address information",
    "units_usage_energy_label_validity.py": "Examines energy label validity across different unit usages [120, 121, 122, 130, 131, 132]",
    "address_units_usage_energy_label_validity_query.py": "Processes units usage energy label validity address information",
    "units_usage_all_energy_label_validity.py": "Examines energy label validity across all unit usages",
    "address_units_all_usage_energy_label_validity_query.py": "Processes all units usage energy label validity address information",
    "null_heating_installation.py": "Analyzes mediums with no heating installation types",
    "address_null_heating_installation_query.py": "Processes null heating installation address information",
    "9_heating_installation_null_mediums.py": "Analyzes where no mediums or heating installation types are",
    "address_9_heating_installation_null_mediums_query.py": "Processes the data where no mediums or heating installation types exist, including address information",
    "buildings_1000.py": "Analyzes building energy label where construction year = 1000",
    "address_buildings_1000_query.py": "Processes buildings with construction year 1000 address information",
    "large_buildings_energy_labels.py": "Analyzes energy labels for large buildings (1000+ m²), excluding private unit usage codes",
    "address_large_buildings_energy_labels_query.py": "Processes large buildings energy label data with address information",
    "Download All Results": "Downloads all .py scripts, excluding request_data.py",
    "Run All Scripts": "Runs all scripts, starting with request_data.py for initial data retrieval"
}

last_run_times = []

@app.route('/')
def index():
    query_files = [f for f in os.listdir('query') if f.endswith('.json')]
    return render_template('index.html', scripts=SCRIPTS, descriptions=SCRIPT_DESCRIPTIONS, last_run_times=last_run_times, query_files=query_files)

@app.route('/download_query/<script_name>')
def download_query(script_name):
    # Extract the base script name without extension
    base_script_name = os.path.splitext(script_name)[0]
    
    # Check if the script has multiple query files
    if script_name in SCRIPT_QUERIES:
        query_files = SCRIPT_QUERIES[script_name]
        file_paths = [os.path.join('query', qf) for qf in query_files]
        
        # Check if all query files exist
        for fp in file_paths:
            if not os.path.exists(fp):
                return jsonify({'error': f'Query file {fp} not found'}), 404
        
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for fp in file_paths:
                zip_file.write(fp, arcname=os.path.basename(fp))
        zip_buffer.seek(0)
        zip_filename = f"{base_script_name}_queries.zip"
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename  # For Flask >=2.0
        )
    else:
        # Default case: one query file with the same name as the script
        query_file_name = f"{base_script_name}.json"
        file_path = os.path.join('query', query_file_name)
        if os.path.exists(file_path):
            try:
                return send_file(
                    file_path,
                    mimetype='application/json',
                    as_attachment=True,
                    download_name=query_file_name  # For Flask >=2.0
                )
            except Exception as e:
                app.logger.error(f"Error sending file {file_path}: {str(e)}")
                return jsonify({'error': f'Error sending file: {str(e)}'}), 500
        else:
            return jsonify({'error': 'File not found'}), 404

@app.route('/run_analysis/<script_name>')
def run_analysis(script_name):
    if script_name not in SCRIPTS:
        return jsonify({'error': 'Invalid script name'}), 400

    try:
        # Extract the base script name without extension
        base_script_name = os.path.splitext(script_name)[0]

        # Determine the required data files and query files
        data_files = []
        query_files = []

        # Check if the script requires special query files
        if script_name in SCRIPT_QUERIES:
            # For scripts with multiple query files
            query_files = SCRIPT_QUERIES[script_name]
            for query_file in query_files:
                data_file = os.path.join('data', os.path.splitext(query_file)[0] + '.txt')
                data_files.append(data_file)
        else:
            # Default case: one query file and one data file
            query_file = f"{base_script_name}.json"
            data_file = os.path.join('data', f"{base_script_name}.txt")
            query_files = [query_file]
            data_files = [data_file]

        # Check if all required data files exist
        missing_data_files = [df for df in data_files if not os.path.exists(df)]
        if missing_data_files:
            # Run the corresponding queries for missing data files
            for qf in query_files:
                query_file_path = os.path.join('query', qf)
                if not os.path.exists(query_file_path):
                    return jsonify({'error': f'Query file {query_file_path} not found'}), 404

                result = subprocess.run(['python', 'request_data.py', '--query-file', query_file_path], capture_output=True, text=True)
                if result.returncode != 0:
                    error_msg = f"Request data failed with error:\n{result.stderr}"
                    app.logger.error(error_msg)
                    return jsonify({'error': error_msg}), 500

        # Run the script
        result = subprocess.run(['python', script_name], capture_output=True, text=True)

        if result.returncode != 0:
            error_msg = f"Script {script_name} failed with error:\n{result.stderr}"
            app.logger.error(error_msg)
            return jsonify({'error': error_msg}), 500

        return jsonify({'message': f'Analysis {script_name} executed successfully'}), 200

    except Exception as e:
        error_msg = f"Error running analysis {script_name}: {str(e)}\n{traceback.format_exc()}"
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 500
    
@app.route('/run_query/<query_name>')
def run_query(query_name):
    try:
        query_file = os.path.join('query', query_name)
        if not os.path.exists(query_file):
            return jsonify({'error': f'Query file {query_name} not found'}), 404

        result = subprocess.run(['python', 'request_data.py', '--query-file', query_file], capture_output=True, text=True)

        if result.returncode != 0:
            error_msg = f"Request data failed with error:\n{result.stderr}"
            app.logger.error(error_msg)
            return jsonify({'error': error_msg}), 500

        output_file = os.path.splitext(query_name)[0] + '.txt'
        return jsonify({'message': f'Query {query_name} executed successfully', 'output_file': output_file}), 200

    except Exception as e:
        error_msg = f"Error running query {query_name}: {str(e)}\n{traceback.format_exc()}"
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/run_custom_query', methods=['POST'])
def run_custom_query():
    try:
        custom_query = request.json.get('custom_query')
        if not custom_query:
            return jsonify({'error': 'No custom query provided'}), 400

        # Ensure custom_query is valid JSON
        try:
            json_query = json.loads(custom_query)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

        result = subprocess.run(['python', 'request_data.py', '--custom-query', json.dumps(json_query)], capture_output=True, text=True)

        if result.returncode != 0:
            error_msg = f"Request data failed with error:\n{result.stderr}"
            app.logger.error(error_msg)
            return jsonify({'error': error_msg}), 500

        # Find the latest custom_query output file
        data_files = [f for f in os.listdir('data') if f.startswith('custom_query_') and f.endswith('.txt')]
        if data_files:
            latest_file = max(data_files, key=lambda x: os.path.getctime(os.path.join('data', x)))
        else:
            latest_file = None

        return jsonify({'message': 'Custom query executed successfully', 'output_file': latest_file}), 200

    except Exception as e:
        error_msg = f"Error running custom query: {str(e)}\n{traceback.format_exc()}"
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/download_query_result/<filename>')
def download_query_result(filename):
    file_path = os.path.join('data', filename)
    if os.path.exists(file_path):
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            app.logger.error(f"Error sending file {file_path}: {str(e)}")
            return jsonify({'error': f'Error sending file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'File not found'}), 404
    
@app.route('/download_output/<filename>')
def download_output(filename):
    file_path = os.path.join('output', filename)
    if os.path.exists(file_path):
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            app.logger.error(f"Error sending file {file_path}: {str(e)}")
            return jsonify({'error': f'Error sending file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'File not found'}), 404
    
@app.route('/run/<script_name>')
def run_script(script_name):
    if script_name not in SCRIPTS and script_name != 'all':
        return jsonify({'error': 'Invalid script name'}), 400
    
    try:
        if script_name == 'all':
            results = []
            app.logger.info("Running all scripts...")
            for script in SCRIPTS:
                app.logger.info(f"Running script: {script}")
                result = subprocess.run(['python', script], capture_output=True, text=True)

                if result.returncode != 0:
                    error_msg = f"Script {script} failed with error:\n{result.stderr}"
                    app.logger.error(error_msg)
                    results.append({'script': script, 'status': 'failed', 'error': result.stderr.strip()})
                else:
                    app.logger.info(f"Script {script} completed successfully.")
                    results.append({'script': script, 'status': 'success'})

            app.logger.info("All scripts have been executed.")
            return jsonify({'message': 'All scripts executed click Download All Results', 'results': results})
        else:
            app.logger.info(f"Running individual script: {script_name}")
            result = subprocess.run(['python', script_name], capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"Script {script_name} failed with error:\n{result.stderr}"
                app.logger.error(error_msg)
                return jsonify({'error': error_msg}), 500
            
            if script_name == 'request_data.py':
                return jsonify({'message': f'Script {script_name} executed successfully. No output file generated.'}), 200
            
            output_file = f"{script_name[:-3]}.xlsx"
            output_path = os.path.join('/app/output', output_file)
            if os.path.exists(output_path):
                app.logger.info(f"Script {script_name} executed successfully. Output file created.")
                return jsonify({'message': f'Script {script_name} executed successfully'})
            else:
                app.logger.warning(f"Script {script_name} executed, but no output file was created.")
                return jsonify({'warning': f'Script {script_name} executed, but no output file was created'}), 200

    except Exception as e:
        error_msg = f"Error running {script_name}: {str(e)}\n{traceback.format_exc()}"
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 500


@app.route('/download/<script_name>')
def download_file(script_name):
    app.logger.info(f"Download requested for script: {script_name}")
    
    if script_name == 'request_data.py':
        return jsonify({'message': 'No file to download for request_data.py'}), 200
    
    if script_name.endswith('.py'):
        file_name = f"{script_name[:-3]}.xlsx"
        file_path = os.path.join('/app/output', file_name)
    elif script_name.endswith('.log'):
        file_path = os.path.join('/app/logs', script_name)
    else:
        app.logger.error(f"Invalid file type requested: {script_name}")
        return jsonify({'error': 'Invalid file type'}), 400

    app.logger.info(f"Looking for file at: {file_path}")

    if os.path.exists(file_path):
        try:
            app.logger.info(f"File found. Attempting to send: {file_path}")
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            app.logger.error(f"Error sending file {file_path}: {str(e)}")
            return jsonify({'error': f'Error sending file: {str(e)}'}), 500
    else:
        app.logger.warning(f"File not found: {file_path}")
        # List contents of output directory
        output_dir = '/app/output'
        app.logger.info(f"Contents of {output_dir}:")
        for file in os.listdir(output_dir):
            app.logger.info(f"- {file}")
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
    if script_name == 'all':
        return "You can now use Download All Results. Logs for individual scripts are available in their respective log files.", 200

    if script_name == 'request_data.py':
        return jsonify({'message': 'No log file for request_data.py'}), 200

    # Extract the base script name without extension
    base_script_name = os.path.splitext(script_name)[0]
    log_file = f"{base_script_name}.log"
    log_path = os.path.join('logs', log_file)
    if os.path.exists(log_path):
        with open(log_path, 'r') as file:
            return file.read(), 200
    else:
        return "No log available", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)