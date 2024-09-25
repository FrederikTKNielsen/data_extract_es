import time
import json
import pandas as pd
import os
import logging

log_dir = '/app/logs'
log_file = os.path.join(log_dir, 'address_large_buildings_energy_labels_query.log')

if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    # Load Elasticsearch output from file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Check if query timed out and log a warning
    if data.get('timed_out'):
        logging.warning("The query timed out. Partial results may be present.")
    
    total_hits = data['hits']['total']['value']
    logging.info(f"Total large buildings with energy labels: {total_hits}")

    results = []
    
    # If total_hits is zero, explicitly log that no data matches the criteria
    if total_hits == 0:
        logging.info("No data matches the criteria. Empty results will be saved.")
        return pd.DataFrame()  # Return an empty DataFrame
    
    # Process the hits and extract the address, building area, and energy label
    for hit in data['hits']['hits']:
        source = hit['_source']
        
        address = source.get('dar_address.address_designation', 'N/A')
        building_area = source.get('bbr_building.byg038_total_building_area', 'N/A')
        energy_label = source.get('emoweb_energy_label.current_energy_label', 'N/A')
        
        # Append to results
        results.append({
            'Address': address,
            'Building Area (m²)': building_area,
            'Energy Label': energy_label
        })

    # Convert results to a Pandas DataFrame
    return pd.DataFrame(results)

def retry_query(file_path, max_retries=3, delay=10):
    """Retry logic for parsing Elasticsearch query."""
    for attempt in range(max_retries):
        try:
            # Attempt to parse the query output
            return parse_elasticsearch_output(file_path)
        except Exception as e:
            logging.error(f"Query failed. Retry attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt + 1 == max_retries:
                raise
            time.sleep(delay)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'address_large_buildings_energy_labels_query.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'address_large_buildings_energy_labels_query.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            logging.error(f"Input file not found at {file_path}")
            raise FileNotFoundError(f"Input file not found at {file_path}")

        # Retry logic in case of query failure
        df = retry_query(file_path)
        
        if df.empty:
            logging.info(f"Data processed. No matches found, an empty report will be generated.")
        else:
            logging.info(f"Data processed. Shape: {df.shape}")

        # Save results to Excel (even if empty)
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Large Buildings Energy Labels', index=False)

        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")
