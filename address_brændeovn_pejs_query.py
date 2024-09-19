import json
import pandas as pd
import os
import logging

logging.basicConfig(filename='/app/logs/address_brændeovn_pejs_query.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    # Load the Elasticsearch JSON output from the file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = []
    
    total_hits = data['hits']['total']['value']
    logging.info(f"Total hits: {total_hits}")
    
    # Process each result from the Elasticsearch output
    for hit in data['hits']['hits']:
        source = hit['_source']
        
        # Extract the address, unit usage, and unit area
        address = source.get('dar_address.address_designation', 'N/A')
        unit_usage = source.get('bbr_unit.enh020_units_usage', 'N/A')
        Sup_heating = source.get('bbr_building.byg058_supplementary_heating', 'N/A')
        
        # Append the results
        results.append({
            'Address': address,
            'Unit Usage': unit_usage,
            'Sup heating': Sup_heating
        })
    
    return pd.DataFrame(results)
    
    # Add percentage of total hits
    df['Percentage of Total'] = (1 / total_hits) * 100
    
    return df

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'address_brændeovn_pejs_query.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'address_brændeovn_pejs_query.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            logging.error(f"Input file not found at {file_path}")
            logging.info(f"Contents of /app/data: {os.listdir('/app/data')}")
            raise FileNotFoundError(f"Input file not found at {file_path}")

        # Parse the Elasticsearch output
        df = parse_elasticsearch_output(file_path)
        logging.info(f"Data processed. Shape: {df.shape}")
        
        # Sort by address (optional, can sort by other columns if needed)
        df = df.sort_values('Address')
        
        logging.info(f"Data sorted. Top 5 rows:\n{df.head().to_string()}")

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Address Data', index=False)
        
        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")
