import json
import pandas as pd
import os
import logging

log_dir = '/app/logs'
log_file = os.path.join(log_dir, '9_heating_installation_null_mediums.log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    total_hits = data['hits']['total']['value']
    logging.info(f"Total buildings with heating installation 9 and null heating medium: {total_hits}")

    results = []
    
    # Loop through municipality buckets
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        municipality_count = municipality['doc_count']

        units_usage_total = sum(usage['doc_count'] for usage in municipality['units_usage']['buckets'])
        
        if municipality_count > units_usage_total:
            results.append({
                'municipality_code': municipality_code,
                'unit_usage': 'No specific usage',
                'heating_medium': 'No medium',
                'count': municipality_count - units_usage_total
            })

        # Loop through unit usage buckets inside the municipality
        for usage in municipality['units_usage']['buckets']:
            usage_code = usage['key']
            usage_count = usage['doc_count']
            
            results.append({
                'municipality_code': municipality_code,
                'unit_usage': usage_code,
                'heating_medium': 'No medium',
                'count': usage_count
            })

    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', '9_heating_installation_null_mediums.txt')
        output_file = os.environ.get('OUTPUT_FILE', '9_heating_installation_null_mediums.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found at {file_path}")

        df = parse_elasticsearch_output(file_path)
        logging.info(f"Data processed. Shape: {df.shape}")

        # Calculate summary statistics
        total_buildings = df['count'].sum()
        buildings_by_usage = df.groupby('unit_usage')['count'].sum().sort_values(ascending=False)
        buildings_by_municipality = df.groupby('municipality_code')['count'].sum().sort_values(ascending=False)

        # Prepare summary data
        summary_data = [
            {'Metric': 'Total units with Null Heating Medium', 'Value': total_buildings}
        ]
        summary_data.extend({'Metric': f'Unit Usage {code}', 'Value': count} for code, count in buildings_by_usage.items())
        summary_data.extend({'Metric': f'Municipality {code}', 'Value': count} for code, count in buildings_by_municipality.items())

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