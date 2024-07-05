import json
import pandas as pd
import os
import sys

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    if 'error' in data:
        print("Elasticsearch query failed. Error details:")
        print(json.dumps(data['error'], indent=2))
        return None
    
    results = []
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        
        for usage in municipality['unit_usage']['buckets']:
            unit_usage = usage['key']
            
            for area_bucket in usage['building_areas']['buckets']:
                min_area = area_bucket['key']
                max_area = min_area + 300  # Changed from 100 to 300
                count = area_bucket['doc_count']
                
                results.append({
                    'municipality_code': municipality_code,
                    'unit_usage': unit_usage,
                    'area_range': f"{min_area}-{max_area}",
                    'count': count
                })
            
            # Add the 900+ bucket (changed from 1000+)
            large_buildings_count = usage['large_buildings']['doc_count']
            results.append({
                'municipality_code': municipality_code,
                'unit_usage': unit_usage,
                'area_range': "900+",
                'count': large_buildings_count
            })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    input_file = os.environ.get('INPUT_FILE', 'building_area.txt')
    output_file = os.environ.get('OUTPUT_FILE', 'building_area.xlsx')

    file_path = f"/app/data/{input_file}"
    
    if not os.path.exists(file_path):
        print(f"Error: Input file not found at {file_path}")
        print("Contents of /app/data:")
        print(os.listdir("/app/data"))
        sys.exit(1)

    df = parse_elasticsearch_output(file_path)
    
    if df is None:
        print("Cannot proceed due to Elasticsearch query error.")
        sys.exit(1)

    print(df)

    # Calculate summary statistics
    total_buildings = df['count'].sum()
    avg_buildings_per_range = df.groupby(['unit_usage', 'area_range'])['count'].mean()
    max_buildings = df.groupby(['unit_usage', 'area_range'])['count'].max()
    min_buildings = df.groupby(['unit_usage', 'area_range'])['count'].min()

    # Save to Excel
    output_path = f"/app/output/{output_file}"
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Detailed Data', index=False)
        
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

    print(f"Results saved to {output_path}")