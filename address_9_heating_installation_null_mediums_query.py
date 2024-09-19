import json
import pandas as pd
import os
import logging

log_dir = '/app/logs'
log_file = os.path.join(log_dir, 'address_9_heating_installation_null_mediums_query.log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    total_hits = data['hits']['total']['value']
    logging.info(f"Total addresses returned: {total_hits}")

    results = []
    
    # Process each result (each hit)
    for hit in data['hits']['hits']:
        source = hit['_source']
        
        # Extract address, unit usage, and supplementary heating
        address = source.get('dar_address.address_designation', 'N/A')
        unit_usage = source.get('bbr_unit.enh020_units_usage', 'N/A')
        supplementary_heating = source.get('bbr_building.byg058_supplementary_heating', 'N/A')
        
        # Add to results list
        results.append({
            'Address': address,
            'Unit Usage': unit_usage,
            'Supplementary Heating': supplementary_heating
        })
    
    # Convert results to a Pandas DataFrame
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'address_9_heating_installation_null_mediums_query.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'address_9_heating_installation_null_mediums_query.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            logging.error(f"Input file not found at {file_path}")
            raise FileNotFoundError(f"Input file not found at {file_path}")

        # Parse the Elasticsearch output
        df = parse_elasticsearch_output(file_path)
        logging.info(f"Data processed. Shape: {df.shape}")

        # Save results to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Address Data', index=False)
        
        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")
