import json
import pandas as pd
import os
from datetime import datetime
import logging

logging.basicConfig(filename='/app/logs/energy_label_age.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_energy_labels(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = []
    today = datetime.now()
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        
        for label in municipality['energy_label']['buckets']:
            label_key = label['key']
            label_count = label['doc_count']
            age_buckets = label['label_age']['buckets']
            
            age_counts = {i: 0 for i in range(11)}
            
            for age_bucket in age_buckets:
                date = datetime.strptime(age_bucket['key_as_string'], "%Y-%m-%d")
                age = (today - date).days // 365
                if 0 <= age < 11:
                    age_counts[age] += age_bucket['doc_count']
            
            row = {
                'municipality_code': municipality_code,
                'energy_label': label_key,
                'label_count': label_count
            }
            row.update({f'energy_label_created_{2024-i}': age_counts[i] for i in range(11)})
            
            results.append(row)
    
    return pd.DataFrame(results)

def calculate_weighted_average_age(row):
    total_count = sum(row[f'energy_label_created_{year}'] for year in range(2014, 2025))
    if total_count == 0:
        return 0
    weighted_sum = sum((2024 - year) * row[f'energy_label_created_{year}'] for year in range(2014, 2025))
    return weighted_sum / total_count

if __name__ == "__main__":
    try:
        energy_labels_file = os.environ.get('INPUT_FILE', 'energy_label_age.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'energy_label_age.xlsx')

        energy_labels_path = f"/app/data/{energy_labels_file}"
        
        if not os.path.exists(energy_labels_path):
            logging.error(f"Energy labels file not found at {energy_labels_path}")
            raise FileNotFoundError(f"Energy labels file not found at {energy_labels_path}")

        df = parse_energy_labels(energy_labels_path)
        logging.info(f"Energy labels data processed. Shape: {df.shape}")
        
        # Calculate weighted average age for each row
        df['weighted_avg_energy_label_age'] = df.apply(calculate_weighted_average_age, axis=1)
        logging.info("Weighted average age calculated for each row")
        
        # Calculate overall weighted average age for each municipality
        municipality_avg_age = df.groupby('municipality_code').apply(
            lambda x: sum(x['weighted_avg_energy_label_age'] * x['label_count']) / x['label_count'].sum()
        ).reset_index(name='municipality_weighted_avg_energy_label_age')
        logging.info("Overall weighted average age calculated for each municipality")
        
        # Merge the municipality average age back to the main dataframe
        df = df.merge(municipality_avg_age, on='municipality_code')
        
        # Sort by municipality code and label count
        df = df.sort_values(['municipality_code', 'label_count'], ascending=[True, False])
        
        logging.info(f"Final dataframe shape: {df.shape}")
        logging.info(f"Top 5 rows of data:\n{df.head().to_string()}")

        # Calculate summary statistics
        total_labels = df['label_count'].sum()
        avg_age = (df['weighted_avg_energy_label_age'] * df['label_count']).sum() / total_labels
        newest_label_age = df['weighted_avg_energy_label_age'].min()
        oldest_label_age = df['weighted_avg_energy_label_age'].max()

        logging.info(f"Summary statistics: Total Labels={total_labels}, Avg Age={avg_age:.2f}, Newest Label Age={newest_label_age:.2f}, Oldest Label Age={oldest_label_age:.2f}")

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Municipality Data', index=False)
            
            # Create a summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Energy Labels', 'Average Label Age', 'Newest Label Age', 'Oldest Label Age'],
                'Value': [total_labels, avg_age, newest_label_age, oldest_label_age]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")