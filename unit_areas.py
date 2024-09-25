import json
import pandas as pd
import os
import logging

logging.basicConfig(filename='/app/logs/unit_areas.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Running updated unit_areas.py script")

def parse_elasticsearch_output(file_path, is_above_900=False):
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
            
            # Below 900 case: iterate over the histogram buckets
            if not is_above_900:
                for area_bucket in usage['unit_areas']['buckets']:
                    min_area = area_bucket['key']
                    max_area = min_area + 20
                    count = area_bucket['doc_count']
                    
                    results.append({
                        'municipality_code': municipality_code,
                        'unit_usage': unit_usage,
                        'area_range': f"{min_area}-{max_area}",
                        'count': count
                    })
            # Above 900 case: handle large units
            else:
                if 'large_units' in usage:
                    large_units_count = usage['large_units']['doc_count']
                    results.append({
                        'municipality_code': municipality_code,
                        'unit_usage': unit_usage,
                        'area_range': "900+",
                        'count': large_units_count
                    })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        # Define file paths relative to the main directory
        below_900_file = os.environ.get('BELOW_900_FILE', 'unit_areas_below_900.txt')
        above_900_file = os.environ.get('ABOVE_900_FILE', 'unit_areas_above_900.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'unit_areas.xlsx')

        below_900_file_path = os.path.join('data', below_900_file)
        above_900_file_path = os.path.join('data', above_900_file)
        output_path = os.path.join('output', output_file)

        logging.info(f"Below 900 File: {below_900_file_path}")
        logging.info(f"Above 900 File: {above_900_file_path}")
        logging.info(f"Output File: {output_path}")

        # Parse below 900 data
        if not os.path.exists(below_900_file_path):
            logging.error(f"Below 900 input file not found at {below_900_file_path}")
            raise FileNotFoundError(f"Below 900 input file not found at {below_900_file_path}")
        
        df_below_900 = parse_elasticsearch_output(below_900_file_path)

        # Parse above 900 data
        if not os.path.exists(above_900_file_path):
            logging.error(f"Above 900 input file not found at {above_900_file_path}")
            raise FileNotFoundError(f"Above 900 input file not found at {above_900_file_path}")

        df_above_900 = parse_elasticsearch_output(above_900_file_path, is_above_900=True)

        # Combine both dataframes
        combined_df = pd.concat([df_below_900, df_above_900], ignore_index=True)

        logging.info(f"Data combined. Shape: {combined_df.shape}")
        logging.info(f"Top 5 rows of combined data:\n{combined_df.head().to_string()}")

        # Calculate summary statistics
        total_buildings = combined_df['count'].sum()
        avg_buildings_per_range = combined_df.groupby(['unit_usage', 'area_range'])['count'].mean()
        max_buildings = combined_df.groupby(['unit_usage', 'area_range'])['count'].max()
        min_buildings = combined_df.groupby(['unit_usage', 'area_range'])['count'].min()

        logging.info(f"Summary statistics calculated: Total={total_buildings}, Avg per range={avg_buildings_per_range.mean():.2f}, Max={max_buildings.max()}, Min={min_buildings.min()}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save to Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            combined_df.to_excel(writer, sheet_name='Detailed Data', index=False)
            
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
