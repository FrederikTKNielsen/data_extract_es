import json
import pandas as pd
import os
import logging

logging.basicConfig(filename='/app/logs/units_usage_energy_label_validity.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_energy_label_validity(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = []
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        
        for usage in municipality['unit_usage']['buckets']:
            usage_code = usage['key']
            total_units = usage['doc_count']
            
            valid_labels = 0
            for validity in usage['energy_label_validity']['buckets']:
                if validity['key_as_string'] == 'true':
                    valid_labels = validity['doc_count']
                    break
            
            percentage_valid = (valid_labels / total_units) * 100 if total_units > 0 else 0
            
            results.append({
                'municipality_code': municipality_code,
                'unit_usage': usage_code,
                'total_units': total_units,
                'valid_energy_labels': valid_labels,
                'percentage_valid': percentage_valid
            })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    try:
        input_file = os.environ.get('INPUT_FILE', 'units_usage_energy_label_validity.txt')
        output_file = os.environ.get('OUTPUT_FILE', 'units_usage_energy_label_validity.xlsx')

        input_path = f"/app/data/{input_file}"
        
        if not os.path.exists(input_path):
            logging.error(f"Input file not found at {input_path}")
            raise FileNotFoundError(f"Input file not found at {input_path}")

        logging.info("Parsing energy label validity data...")
        df = parse_energy_label_validity(input_path)
        logging.info(f"Data parsed. Shape of resulting dataframe: {df.shape}")
        
        # Sort by percentage of valid energy labels in descending order
        df = df.sort_values(['municipality_code', 'unit_usage', 'percentage_valid'], ascending=[True, True, False])
        
        logging.info(f"Top 5 rows of sorted data:\n{df.head().to_string()}")

        # Calculate overall statistics
        total_units = df['total_units'].sum()
        total_valid_labels = df['valid_energy_labels'].sum()
        overall_percentage = (total_valid_labels / total_units) * 100 if total_units > 0 else 0
        
        logging.info(f"Overall statistics:")
        logging.info(f"Total units: {total_units}")
        logging.info(f"Total valid energy labels: {total_valid_labels}")
        logging.info(f"Overall percentage of valid energy labels: {overall_percentage:.2f}%")

        # Calculate statistics by unit usage
        usage_stats = df.groupby('unit_usage').agg({
            'total_units': 'sum',
            'valid_energy_labels': 'sum'
        }).reset_index()
        usage_stats['percentage_valid'] = (usage_stats['valid_energy_labels'] / usage_stats['total_units']) * 100
        usage_stats = usage_stats.sort_values('percentage_valid', ascending=False)
        
        logging.info("Statistics by unit usage:")
        logging.info(usage_stats.to_string(index=False))

        # Save to Excel
        output_path = f"/app/output/{output_file}"
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Municipality Data', index=False)
            
            # Create a summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Units', 'Total Valid Energy Labels', 'Overall Percentage'],
                'Value': [total_units, total_valid_labels, f"{overall_percentage:.2f}%"]
            })
            summary_df.to_excel(writer, sheet_name='Overall Summary', index=False)
            
            # Add usage statistics to the Excel file
            usage_stats.to_excel(writer, sheet_name='Usage Summary', index=False)
        
        logging.info(f"Results saved to {output_path}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

    logging.info("Script completed successfully")