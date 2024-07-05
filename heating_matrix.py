import json
import pandas as pd
from collections import defaultdict
import os

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = []
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        
        for installation in municipality['heatingInstallations']['buckets']:
            installation_code = installation['key']
            
            medium_counts = defaultdict(int)
            for medium in installation['heatingMediums']['buckets']:
                medium_code = medium['key']
                count = medium['doc_count']
                medium_counts[medium_code] = count
            
            # If there are no heating mediums, we still want to count the installations
            if not medium_counts:
                medium_counts[''] = installation['doc_count']
            
            for medium_code, count in medium_counts.items():
                results.append({
                    'municipality_code': municipality_code,
                    'installation_code': installation_code,
                    'medium_code': medium_code,
                    'count': count
                })
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    input_file = os.environ.get('INPUT_FILE', 'heating_matrix.txt')
    output_file = os.environ.get('OUTPUT_FILE', 'heating_matrix.xlsx')

    file_path = f"/app/data/{input_file}"
    
    if not os.path.exists(file_path):
        print(f"Error: Input file not found at {file_path}")
        print("Contents of /app/data:")
        print(os.listdir("/app/data"))
        exit(1)

    df = parse_elasticsearch_output(file_path)
    print(df)

    # Calculate summary statistics
    total_installations = df['count'].sum()
    installations_by_type = df.groupby('installation_code')['count'].sum().sort_values(ascending=False)
    mediums_by_type = df.groupby('medium_code')['count'].sum().sort_values(ascending=False)
    top_5_combinations = df.groupby(['installation_code', 'medium_code'])['count'].sum().sort_values(ascending=False).head()

    # Save to Excel
    output_path = f"/app/output/{output_file}"
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Detailed Data', index=False)
        
        # Create a summary sheet
        summary_df = pd.DataFrame({
            'Metric': ['Total Installations'] + 
                      [f'Installation Type {code}' for code in installations_by_type.index] +
                      [f'Medium Type {code}' for code in mediums_by_type.index] +
                      [f'Top Combination {i+1}' for i in range(5)],
            'Value': [total_installations] + 
                     installations_by_type.tolist() +
                     mediums_by_type.tolist() +
                     [f"{combo[0]},{combo[1]}: {count}" for combo, count in top_5_combinations.items()]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

    print(f"Results saved to {output_path}")