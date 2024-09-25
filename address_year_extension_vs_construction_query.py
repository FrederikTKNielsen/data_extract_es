import json
import pandas as pd
import os
import logging

log_dir = '/app/logs'
log_file = os.path.join(log_dir, 'address_year_extension_vs_construction_query.log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    total_hits = data['hits']['total']['value']
    logging.info(f"Total buildings with extension year < construction year: {total_hits}")

    results = []
    
    # Process each result (each hit)
    for hit in data['hits']['hits']:
        source = hit['_source']
        
        # Extract the year of extension, year of construction, and address
        extension_year = source.get('bbr_building.byg027_year_of_extension', 'N/A')
        construction_year = source.get('bbr_building.byg026_year_of_construction', 'N/A')
        address = source.get('dar_address.address_designation', 'N/A')
        
        # Add to results list
        results.append({
            'Address': address,
            'Year of Extension': extension_year,
            'Year of Construction': construction_year
        })
    
    # Convert results to a Pandas DataFrame
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'address_year_extension_vs_construction_query.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'address_year_extension_vs_construction_query.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            logging.error(f"Input file not found at {file_path}")
            raise FileNotFoundError(f"Input file not found at {file_path}")

        # Parse the Elasticsearch output
        df = parse_elasticsearch_output(file_path)
        
        if df.empty:
            logging.info(f"Data processed. No matches found, an empty report will be generated.")
        else:
            logging.info(f"Data processed. Shape: {df.shape}")

        # Save results to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Year Comparison Data', index=False)
        
        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")