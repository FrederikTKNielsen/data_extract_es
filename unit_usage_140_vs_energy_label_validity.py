import json
import pandas as pd
import os
import logging

logging.basicConfig(filename='/app/logs/unit_usage_140_vs_energy_label_validity.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_energy_label_validity(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = []
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        total_units = municipality['doc_count']
        
        valid_labels = 0
        for validity in municipality['energy_label_validity']['buckets']:
            if validity['key_as_string'] == 'true':
                valid_labels = validity['doc_count']
                break
        
        percentage_valid = (valid_labels / total_units) * 100 if total_units > 0 else 0
        
        results.append({
            'municipality_code': municipality_code,
            'total_units': total_units,
            'valid_energy_labels': valid_labels,
            'percentage_valid': percentage_valid
        })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'unit_usage_140_vs_energy_label_validity.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'unit_usage_140_vs_energy_label_validity.xlsx')

        input_path = f"/app/data/{input_file}"
        
        if not os.path.exists(input_path):
            logging.error(f"Input file not found at {input_path}")
            raise FileNotFoundError(f"Input file not found at {input_path}")

        logging.info("Parsing energy label validity data...")
        df = parse_energy_label_validity(input_path)
        logging.info(f"Data parsed. Shape of resulting dataframe: {df.shape}")
        
        # Sort by percentage of valid energy labels in descending order
        df = df.sort_values('percentage_valid', ascending=False)
        
        logging.info(f"Top 5 municipalities by percentage of valid energy labels:\n{df.head().to_string()}")

        # Calculate overall statistics
        total_units = df['total_units'].sum()
        total_valid_labels = df['valid_energy_labels'].sum()
        overall_percentage = (total_valid_labels / total_units) * 100 if total_units > 0 else 0
        
        logging.info(f"Overall statistics:")
        logging.info(f"Total units: {total_units}")
        logging.info(f"Total valid energy labels: {total_valid_labels}")
        logging.info(f"Overall percentage of valid energy labels: {overall_percentage:.2f}%")

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Municipality Data', index=False)
            
            # Create a summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Units', 'Total Valid Energy Labels', 'Overall Percentage'],
                'Value': [total_units, total_valid_labels, f"{overall_percentage:.2f}%"]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

    logging.info("Script completed successfully")