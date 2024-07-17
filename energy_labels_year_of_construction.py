import json
import pandas as pd
import os
from datetime import datetime
import logging

logging.basicConfig(filename='/app/logs/energy_labels_year_of_construction.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

ENERGY_LABEL_ORDER = ['A2020', 'A2015', 'A2010', 'B', 'C', 'D', 'E', 'F', 'G']

def parse_energy_labels(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = []
    current_year = datetime.now().year
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        
        for label in municipality['energy_label']['buckets']:
            label_key = label['key']
            
            for year_bucket in label['construction_year_histogram']['buckets']:
                construction_year_start = year_bucket['key']
                construction_year_end = construction_year_start + 9
                count = year_bucket['doc_count']
                
                # Calculate the average age of the buildings in this bucket
                avg_construction_year = construction_year_start + 5
                building_age = current_year - avg_construction_year
                
                results.append({
                    'municipality_code': municipality_code,
                    'energy_label': label_key,
                    'construction_year_range': f"{construction_year_start}-{construction_year_end}",
                    'avg_building_age': building_age,
                    'count': count
                })
    
    return pd.DataFrame(results)

def calculate_weighted_average_age(group):
    return (group['avg_building_age'] * group['count']).sum() / group['count'].sum()

def flag_anomalies(row):
    label_index = ENERGY_LABEL_ORDER.index(row['energy_label']) if row['energy_label'] in ENERGY_LABEL_ORDER else -1
    age = row['avg_building_age']
    
    if label_index < 3 and age > 100:  # High energy rating (A2020, A2015, A2010, B) for very old buildings
        return 'Potential anomaly'
    elif label_index < 5 and age > 150:  # Good energy rating (up to C) for extremely old buildings
        return 'Potential anomaly'
    else:
        return 'Normal'

if __name__ == "__main__":
    try:
        energy_labels_file = os.environ.get('INPUT_FILE', 'energy_labels_year_of_construction.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'energy_labels_year_of_construction.xlsx')

        energy_labels_path = f"/app/data/{energy_labels_file}"
        
        if not os.path.exists(energy_labels_path):
            logging.error(f"Energy labels file not found at {energy_labels_path}")
            raise FileNotFoundError(f"Energy labels file not found at {energy_labels_path}")

        df = parse_energy_labels(energy_labels_path)
        logging.info(f"Energy labels data processed. Shape: {df.shape}")
        
        # Calculate weighted average building age for each municipality and energy label
        weighted_avg_age = df.groupby(['municipality_code', 'energy_label']).apply(calculate_weighted_average_age)
        weighted_avg_age_df = weighted_avg_age.reset_index()
        weighted_avg_age_df.columns = ['municipality_code', 'energy_label', 'energy_label_weighted_avg_building_age']
        logging.info("Weighted average building age calculated for each municipality and energy label")
        
        # Merge the weighted average age back to the main dataframe
        df = df.merge(weighted_avg_age_df, on=['municipality_code', 'energy_label'])
        
        # Calculate overall weighted average building age for each municipality
        municipality_avg_age = df.groupby('municipality_code').apply(
            lambda x: (x['avg_building_age'] * x['count']).sum() / x['count'].sum()
        ).reset_index(name='municipality_weighted_avg_building_age')
        logging.info("Overall weighted average building age calculated for each municipality")
        
        # Merge the municipality average age back to the main dataframe
        df = df.merge(municipality_avg_age, on='municipality_code')
        
        # Flag potential anomalies
        df['anomaly_flag'] = df.apply(flag_anomalies, axis=1)
        logging.info("Potential anomalies flagged")
        
        # Sort by municipality code, energy label, and construction year range
        df = df.sort_values(['municipality_code', 'energy_label', 'construction_year_range'])
        
        logging.info(f"Final dataframe shape: {df.shape}")
        logging.info(f"Top 5 rows of data:\n{df.head().to_string()}")

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        df.to_excel(output_path, index=False)
        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

    logging.info("Script completed successfully")