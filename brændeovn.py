import json
import pandas as pd
import os
import logging

logging.basicConfig(filename='/app/logs/brændeovn.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = []
    
    total_hits = data['hits']['total']['value']
    logging.info(f"Total hits: {total_hits}")
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        count = municipality['doc_count']
        
        results.append({
            'municipality_code': municipality_code,
            'count': count
        })
    
    df = pd.DataFrame(results)
    
    # Calculate the percentage
    df['percentage_of_all_brændovn'] = (df['count'] / total_hits) * 100
    
    return df

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'brændeovn.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'brændeovn.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            logging.error(f"Input file not found at {file_path}")
            logging.info(f"Contents of /app/data: {os.listdir('/app/data')}")
            raise FileNotFoundError(f"Input file not found at {file_path}")

        df = parse_elasticsearch_output(file_path)
        logging.info(f"Data processed. Shape: {df.shape}")
        
        # Sort by count in descending order
        df = df.sort_values('count', ascending=False)
        
        logging.info(f"Data sorted. Top 5 rows:\n{df.head().to_string()}")

        # Calculate summary statistics
        total_brændovn = df['count'].sum()
        avg_brændovn_per_municipality = df['count'].mean()
        max_brændovn = df['count'].max()
        min_brændovn = df['count'].min()

        logging.info(f"Summary statistics calculated: Total={total_brændovn}, Avg={avg_brændovn_per_municipality:.2f}, Max={max_brændovn}, Min={min_brændovn}")

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Municipality Data', index=False)
            
            # Create a summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Brændovn', 'Avg Brændovn per Municipality', 'Max Brændovn in a Municipality', 'Min Brændovn in a Municipality'],
                'Value': [total_brændovn, avg_brændovn_per_municipality, max_brændovn, min_brændovn]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")