import json
import pandas as pd
import os
import sys
import logging

logging.basicConfig(filename='/app/logs/address_unit_areass_query.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    # Load the Elasticsearch JSON output from the file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Check for errors in the Elasticsearch query response
    if 'error' in data:
        logging.error("Elasticsearch query failed. Error details:")
        logging.error(json.dumps(data['error'], indent=2))
        return None
    
    results = []
    
    # Process each result from the Elasticsearch output
    for hit in data['hits']['hits']:
        source = hit['_source']
        
        # Extract the address, unit usage, and unit area
        address = source.get('dar_address.address_designation', 'N/A')
        unit_usage = source.get('bbr_unit.enh020_units_usage', 'N/A')
        unit_area = source.get('bbr_unit.enh026_unit_total_area', 'N/A')
        
        # Append the results
        results.append({
            'Address': address,
            'Unit Usage': unit_usage,
            'Unit Area': unit_area
        })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'address_unit_areass_query.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'address_unit_areass_query.xlsx')

        # Construct the file path for the input file
        file_path = f"/app/data/{input_file}"
        
        # Check if the input file exists
        if not os.path.exists(file_path):
            logging.error(f"Input file not found at {file_path}")
            logging.info(f"Contents of /app/data: {os.listdir('/app/data')}")
            raise FileNotFoundError(f"Input file not found at {file_path}")

        # Parse the Elasticsearch output
        df = parse_elasticsearch_output(file_path)
        
        # If the DataFrame is None (error case), stop execution
        if df is None:
            logging.error("Cannot proceed due to Elasticsearch query error.")
            sys.exit(1)

        logging.info(f"Data processed. Shape: {df.shape}")
        logging.info(f"Top 5 rows of data:\n{df.head().to_string()}")

        # Save the results to an Excel file
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Addresses', index=False)

        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")
