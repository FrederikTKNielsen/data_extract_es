import json
import pandas as pd
import os
import logging

logging.basicConfig(filename='/app/logs/construction_years.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = []
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        
        for year in municipality['construction_years']['buckets']:
            construction_year = year['key']
            count = year['doc_count']
            
            results.append({
                'municipality_code': municipality_code,
                'construction_year': construction_year,
                'count': count
            })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'construction_years.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'construction_years.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            logging.error(f"Input file not found at {file_path}")
            logging.info(f"Contents of /app/data: {os.listdir('/app/data')}")
            raise FileNotFoundError(f"Input file not found at {file_path}")

        df = parse_elasticsearch_output(file_path)
        
        logging.info(f"Data processed. Shape: {df.shape}")
        logging.info(f"Top 5 rows of data:\n{df.head().to_string()}")

        # Calculate summary statistics
        total_buildings = df['count'].sum()
        avg_buildings_per_year = df.groupby('construction_year')['count'].mean()
        max_buildings = df.groupby('construction_year')['count'].max()
        min_buildings = df.groupby('construction_year')['count'].min()
        median_year = df.groupby('construction_year')['count'].sum().sort_values(ascending=False).index[0]

        logging.info(f"Summary statistics calculated: Total={total_buildings}, Avg per year={avg_buildings_per_year.mean():.2f}, Max={max_buildings.max()}, Min={min_buildings.min()}, Median Year={median_year}")

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Municipality Data', index=False)
            
            # Create a summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Units', 'Median Construction Year', 'Avg Units per Year', 'Max Units in a Year', 'Min Units in a Year'],
                'Value': [total_buildings, median_year, avg_buildings_per_year.mean(), max_buildings.max(), min_buildings.min()]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")