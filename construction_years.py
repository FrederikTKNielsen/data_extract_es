import json
import pandas as pd
import os

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
    input_file = os.environ.get('INPUT_FILE', 'parse_elasticsearch.txt')
    output_file = os.environ.get('OUTPUT_FILE', 'parse_elasticsearch.xlsx')

    file_path = f"/app/data/{input_file}"
    
    if not os.path.exists(file_path):
        print(f"Error: Input file not found at {file_path}")
        print("Contents of /app/data:")
        print(os.listdir("/app/data"))
        exit(1)

    df = parse_elasticsearch_output(file_path)
    
    print(df)

    # Calculate summary statistics
    total_buildings = df['count'].sum()
    avg_buildings_per_year = df.groupby('construction_year')['count'].mean()
    max_buildings = df.groupby('construction_year')['count'].max()
    min_buildings = df.groupby('construction_year')['count'].min()
    median_year = df.groupby('construction_year')['count'].sum().sort_values(ascending=False).index[0]

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

    print(f"Results saved to {output_path}")