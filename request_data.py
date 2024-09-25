import requests
import json
import os
import argparse
import time
from dotenv import load_dotenv
load_dotenv()

def process_query(query_name, payload):
    url = os.environ.get('ELASTICSEARCH_URL')
    headers = {
        'Content-Type': 'application/json'
    }

    # Make the API request
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    # Generate the output filename based on the query name
    if query_name == 'custom_query':
        output_file = f"{query_name}_{int(time.time())}.txt"  # Add timestamp to avoid overwriting
    else:
        output_file = os.path.splitext(query_name)[0] + '.txt'
    output_path = os.path.join('data', output_file)

    # Write the response to the file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, indent=2, ensure_ascii=False)

    print(f"Data for {query_name} has been saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process queries to fetch data.')
    parser.add_argument('--query-file', help='Specific query file to process')
    parser.add_argument('--custom-query', help='Custom KQL query string in JSON format')
    args = parser.parse_args()

    # Create 'data' folder if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    # Create 'query' folder if it doesn't exist
    if not os.path.exists('query'):
        os.makedirs('query')
        print("'query' folder created. Please place your query JSON files in this folder.")
        exit()

    if args.custom_query:
        # Process the custom query
        query_name = 'custom_query'
        payload = json.loads(args.custom_query)
        process_query(query_name, payload)
    elif args.query_file:
        # Process the specified query file
        query_file = args.query_file
        if not os.path.exists(query_file):
            print(f"Query file {query_file} not found.")
            exit()
        with open(query_file, 'r') as f:
            payload = json.load(f)
        query_name = os.path.basename(query_file)
        process_query(query_name, payload)
    else:
        # List all JSON files in the query folder
        query_files = [f for f in os.listdir('query') if f.endswith('.json')]

        if not query_files:
            print("No JSON files found in the 'query' folder. Please add query files.")
            exit()

        # Process each query file
        for query_file in query_files:
            print(f"Processing query file: {query_file}")

            with open(os.path.join('query', query_file), 'r') as f:
                payload = json.load(f)

            process_query(query_file, payload)

        print("All queries have been processed.")
