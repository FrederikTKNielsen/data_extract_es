import json
import pandas as pd
from collections import defaultdict
import os

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    total_hits = data['hits']['total']['value']
    print(f"Total hits from Elasticsearch: {total_hits}")

    results = []
    total_processed = 0

    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        municipality_count = municipality['doc_count']
        total_processed += municipality_count

        for installation in municipality['heatingInstallations']['buckets']:
            installation_code = installation['key']
            installation_count = installation['doc_count']

            supplementary_count = 0
            for medium in installation['supplementary_heating']['buckets']:
                medium_code = medium['key']
                count = medium['doc_count']
                supplementary_count += count
                results.append({
                    'municipality_code': municipality_code,
                    'installation_code': installation_code,
                    'medium_code': medium_code,
                    'count': count
                })

            # Add a row for buildings without supplementary heating
            if supplementary_count < installation_count:
                results.append({
                    'municipality_code': municipality_code,
                    'installation_code': installation_code,
                    'medium_code': 'No supplementary',
                    'count': installation_count - supplementary_count
                })

    print(f"Total processed: {total_processed}")
    return pd.DataFrame(results)


if __name__ == "__main__":
    input_file = os.environ.get('INPUT_FILE', 'supplementary_heating.txt')
    output_file = os.environ.get('OUTPUT_FILE', 'supplementary_heating.xlsx')

    file_path = f"/app/data/{input_file}"
    
    if not os.path.exists(file_path):
        print(f"Error: Input file not found at {file_path}")
        print("Contents of /app/data:")
        print(os.listdir("/app/data"))
        exit(1)

    df = parse_elasticsearch_output(file_path)
    print(df)

    # Calculate summary statistics
    total_supplementary = df['count'].sum()
    supplementary_by_type = df.groupby('medium_code')['count'].sum().sort_values(ascending=False)
    top_5_combinations = df.groupby(['installation_code', 'medium_code'])['count'].sum().sort_values(ascending=False).head()
    municipalities_with_most = df.groupby('municipality_code')['count'].sum().sort_values(ascending=False).head()

    # Save to Excel
    output_path = f"/app/output/{output_file}"
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Detailed Data', index=False)
        
        # Create a summary sheet
        summary_df = pd.DataFrame({
            'Metric': ['Total Supplementary Heating'] + 
                      [f'Supplementary Type {code}' for code in supplementary_by_type.index] +
                      [f'Top Combination {i+1}' for i in range(5)],
            'Value': [total_supplementary] + 
                     supplementary_by_type.tolist() +
                     [f"{combo[0]},{combo[1]}: {count}" for combo, count in top_5_combinations.items()]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

    print(f"Results saved to {output_path}")

