import json
import pandas as pd
import os
import logging

logging.basicConfig(filename='/app/logs/large_buildings_energy_labels.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

EXCLUDED_USAGE_CODES = [110, 120, 121, 122, 130, 131, 132, 140, 150, 160, 190, 510, 90]

def parse_elasticsearch_output(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    total_hits = data['hits']['total']['value']
    logging.info(f"Total large buildings (1000+ m²) with energy labels, excluding certain usage codes: {total_hits}")

    results = []
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        for usage in municipality['unit_usage']['buckets']:
            unit_usage = usage['key']
            for label in usage['energy_label']['buckets']:
                results.append({
                    'municipality_code': municipality_code,
                    'unit_usage': unit_usage,
                    'energy_label': label['key'],
                    'count': label['doc_count']
                })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'large_buildings_energy_labels.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'large_buildings_energy_labels.xlsx')

        file_path = f"/app/data/{input_file}"
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found at {file_path}")

        df = parse_elasticsearch_output(file_path)
        logging.info(f"Data processed. Shape: {df.shape}")

        # Calculate summary statistics
        total_buildings = df['count'].sum()
        buildings_by_municipality = df.groupby('municipality_code')['count'].sum().sort_values(ascending=False)
        buildings_by_usage = df.groupby('unit_usage')['count'].sum().sort_values(ascending=False)
        buildings_by_label = df.groupby('energy_label')['count'].sum().sort_values(ascending=False)
        top_combinations = df.groupby(['municipality_code', 'unit_usage', 'energy_label'])['count'].sum().sort_values(ascending=False).head(10)

        # Prepare summary data
        summary_data = [
            {'Metric': 'Total large buildings with energy labels', 'Value': total_buildings},
            {'Metric': 'Number of municipalities', 'Value': len(buildings_by_municipality)},
            {'Metric': 'Number of unit usage types', 'Value': len(buildings_by_usage)},
            {'Metric': 'Number of energy label types', 'Value': len(buildings_by_label)}
        ]
        summary_data.extend({'Metric': f'Top Municipality {code}', 'Value': count} for code, count in buildings_by_municipality.head().items())
        summary_data.extend({'Metric': f'Top Unit Usage {usage}', 'Value': count} for usage, count in buildings_by_usage.head().items())
        summary_data.extend({'Metric': f'Energy Label {label}', 'Value': count} for label, count in buildings_by_label.items())
        summary_data.extend({'Metric': f'Top Combination {i+1}', 'Value': f"{mun}, {usage}, {label}: {count}"} for i, ((mun, usage, label), count) in enumerate(top_combinations.items()))

        summary_df = pd.DataFrame(summary_data)

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detailed Data', index=False)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")
    logging.info(f"Note: This analysis excludes unit usage codes {EXCLUDED_USAGE_CODES} and only includes buildings 1000 m² or larger.")