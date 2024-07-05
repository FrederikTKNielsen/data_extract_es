import json
import pandas as pd
import os

# Hardcoded path for municipalities file
MUNICIPALITIES_FILE = "/app/data/total_units.txt"

def parse_municipalities(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = {}
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        count = municipality['doc_count']
        results[municipality_code] = count
    
    return results

def parse_energy_labels(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = {}
    
    for municipality in data['aggregations']['municipalities']['buckets']:
        municipality_code = municipality['key']
        energy_labels = {}
        for label in municipality['energy_label']['buckets']:
            energy_labels[label['key']] = label['doc_count']
        results[municipality_code] = energy_labels
    
    return results

def combine_data(municipalities, energy_labels):
    results = []
    
    for code, total in municipalities.items():
        labels = energy_labels.get(code, {})
        labeled_count = sum(labels.values())
        
        row = {
            'municipality_code': code,
            'total_units': total,
            'labeled_buildings': labeled_count,
            'label_percentage': (labeled_count / total) * 100 if total > 0 else 0
        }
        
        # Add counts for each energy label
        for label, count in labels.items():
            row[f'label_{label}'] = count
        
        results.append(row)
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    energy_labels_file = os.environ.get('INPUT_FILE', 'energy_labels.txt')
    output_file = os.environ.get('OUTPUT_FILE', 'energy_labels.xlsx')

    energy_labels_path = f"/app/data/{energy_labels_file}"
    
    if not os.path.exists(MUNICIPALITIES_FILE):
        print(f"Error: Municipalities file not found at {MUNICIPALITIES_FILE}")
        exit(1)
    
    if not os.path.exists(energy_labels_path):
        print(f"Error: Energy labels file not found at {energy_labels_path}")
        exit(1)

    municipalities = parse_municipalities(MUNICIPALITIES_FILE)
    energy_labels = parse_energy_labels(energy_labels_path)
    
    df = combine_data(municipalities, energy_labels)
    
    # Sort by total buildings in descending order
    df = df.sort_values('total_units', ascending=False)
    
    print(df)

    # Calculate summary statistics
    total_units = df['total_units'].sum()
    total_labeled = df['labeled_buildings'].sum()
    overall_label_percentage = (total_labeled / total_units) * 100 if total_units > 0 else 0
    
    label_columns = [col for col in df.columns if col.startswith('label_') and col != 'label_percentage']
    label_totals = df[label_columns].sum()
    label_percentages = (label_totals / total_labeled * 100).round(2)

    # Save to Excel
    output_path = f"/app/output/{output_file}"
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Municipality Data', index=False)
        
        # Create a summary sheet
        summary_data = {
            'Metric': ['Total Units', 'Total Labeled Buildings', 'Overall Label Percentage'] + 
                      [f'Total {label.replace("label_", "")}' for label in label_columns] +
                      [f'{label.replace("label_", "")} Percentage' for label in label_columns],
            'Value': [total_units, total_labeled, f"{overall_label_percentage:.2f}%"] + 
                     label_totals.tolist() + label_percentages.tolist()
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

    print(f"Results saved to {output_path}")