import requests
import json
import os


# Create 'data' folder if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Create 'query' folder if it doesn't exist
if not os.path.exists('query'):
    os.makedirs('query')
    print("'query' folder created. Please place your query JSON files in this folder.")
    exit()

# List all JSON files in the query folder
query_files = [f for f in os.listdir('query') if f.endswith('.json')]

if not query_files:
    print("No JSON files found in the 'query' folder. Please add query files.")
    exit()

url = os.environ.get('ELASTICSEARCH_URL')

headers = {
    'Content-Type': 'application/json'
}

# Process each query file
for query_file in query_files:
    print(f"Processing query file: {query_file}")
    
    # Load the query from the file
    with open(os.path.join('query', query_file), 'r') as f:
        payload = json.load(f)

    # Make the API request
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    # Generate the output filename based on the input filename
    output_file = os.path.splitext(query_file)[0] + '.txt'
    output_path = os.path.join('data', output_file)

    # Write the response to the file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, indent=2, ensure_ascii=False)

    print(f"Data for {query_file} has been saved to {output_path}")

print("All queries have been processed.")