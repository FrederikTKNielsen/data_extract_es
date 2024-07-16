import json
import pandas as pd
import os
import logging

logging.basicConfig(filename='/app/logs/buildings_1000.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    total_hits = data['hits']['total']['value']
    logging.info(f"Total buildings from year 1000 with energy labels: {total_hits}")

    results = []
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        for label in municipality['energy_label']['buckets']:
            results.append({
                'municipality_code': municipality_code,
                'energy_label': label['key'],
                'count': label['doc_count']
            })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'buildings_1000.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'buildings_1000.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found at {file_path}")

        df = parse_elasticsearch_output(file_path)
        logging.info(f"Data processed. Shape: {df.shape}")

        # Calculate summary statistics
        total_buildings = df['count'].sum()
        buildings_by_municipality = df.groupby('municipality_code')['count'].sum().sort_values(ascending=False)
        buildings_by_label = df.groupby('energy_label')['count'].sum().sort_values(ascending=False)

        # Prepare summary data
        summary_data = [
            {'Metric': 'Total buildings from year 1000 with energy labels', 'Value': total_buildings},
            {'Metric': 'Number of municipalities', 'Value': len(buildings_by_municipality)}
        ]
        summary_data.extend({'Metric': f'Municipality {code}', 'Value': count} for code, count in buildings_by_municipality.items())
        summary_data.extend({'Metric': f'Energy Label {label}', 'Value': count} for label, count in buildings_by_label.items())

        summary_df = pd.DataFrame(summary_data)

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detailed Data', index=False)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")