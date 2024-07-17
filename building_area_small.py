import json
import pandas as pd
import numpy as np
import os
import sys
import logging

logging.basicConfig(filename='/app/logs/building_area_small.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    if 'error' in data:
        logging.error("Elasticsearch query failed. Error details:")
        logging.error(json.dumps(data['error'], indent=2))
        return None
    
    results = []
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        
        for usage in municipality['unit_usage']['buckets']:
            unit_usage = usage['key']
            
            for area_bucket in usage['building_areas']['buckets']:
                area = area_bucket['key']
                count = area_bucket['doc_count']
                
                results.append({
                    'municipality_code': municipality_code,
                    'unit_usage': unit_usage,
                    'building_area': area,
                    'count': count
                })
    
    return pd.DataFrame(results)

def create_area_ranges(df):
    bins = [0, 5] + list(range(10, 101, 5))  # Creates bins [0, 5, 10, 15, ..., 95, 100]
    labels = ['0-5'] + [f"{i+1}-{i+5}" for i in range(5, 96, 5)]  # Creates labels ["0-5", "6-10", "11-15", ..., "96-100"]
    
    df['area_range'] = pd.cut(df['building_area'], 
                              bins=bins,
                              labels=labels,
                              right=True,
                              include_lowest=True)
    return df

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'building_area_small.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'building_area_small.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            logging.error(f"Input file not found at {file_path}")
            logging.info(f"Contents of /app/data: {os.listdir('/app/data')}")
            raise FileNotFoundError(f"Input file not found at {file_path}")

        df = parse_elasticsearch_output(file_path)
        
        if df is None:
            logging.error("Cannot proceed due to Elasticsearch query error.")
            sys.exit(1)

        logging.info(f"Data processed. Shape: {df.shape}")

        # Create area ranges
        df = create_area_ranges(df)
        logging.info("Area ranges created")
        
        # Group by municipality, unit usage, and area range
        grouped_df = df.groupby(['municipality_code', 'unit_usage', 'area_range'])['count'].sum().reset_index()
        logging.info(f"Data grouped. Shape: {grouped_df.shape}")

        logging.info(f"Top 5 rows of grouped data:\n{grouped_df.head().to_string()}")

        # Calculate summary statistics
        total_buildings = grouped_df['count'].sum()
        avg_buildings_per_range = grouped_df.groupby(['unit_usage', 'area_range'])['count'].mean()
        max_buildings = grouped_df.groupby(['unit_usage', 'area_range'])['count'].max()
        min_buildings = grouped_df.groupby(['unit_usage', 'area_range'])['count'].min()

        logging.info(f"Summary statistics calculated: Total={total_buildings}, Avg per range={avg_buildings_per_range.mean():.2f}, Max={max_buildings.max()}, Min={min_buildings.min()}")

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            grouped_df.to_excel(writer, sheet_name='Detailed Data', index=False)
            
            # Create a summary sheet
            summary_stats_df = pd.DataFrame({
                'Unit Usage': avg_buildings_per_range.index.get_level_values('unit_usage'),
                'Area Range': avg_buildings_per_range.index.get_level_values('area_range'),
                'Avg Units': avg_buildings_per_range.values,
                'Max Units': max_buildings.values,
                'Min Units': min_buildings.values
            })
            # Add total row
            total_row = pd.DataFrame({'Unit Usage': ['Total'], 'Area Range': [''], 'Avg Units': [total_buildings], 'Max Units': [None], 'Min Units': [None]})
            summary_stats_df = pd.concat([summary_stats_df, total_row], ignore_index=True)
            summary_stats_df.to_excel(writer, sheet_name='Summary Statistics', index=False)

        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")