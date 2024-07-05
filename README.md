# ES_DATA_ANALYSE Project

This project is designed to analyze and process data from Elasticsearch queries related to building information, energy labels, and heating systems in various municipalities.

## Project Structure

```
ES_DATA_ANALYSE/
├── data/                 # Input data directory
├── output/               # Output directory for analysis results
├── query/                # Elasticsearch query files
├── brændeovn.py
├── building_area.py
├── construction_years.py
├── dockerfile
├── energy_label_age.py
├── energy_labels_year_of_contruction.py
├── energy_labels.py
├── heating_matrix.py
├── makefile
├── request_data.py
├── requirements.txt
├── supplementary_heating.py
├── unit_usage_140_vs_energy_label_validity.py
└── units_usage_energy_label_validity.py
```

## Setup and Installation

1. Ensure you have Docker installed on your system.
2. Clone this repository to your local machine.
3. Navigate to the project directory.

## Usage

### Running All Scripts

To run all scripts in the correct order:

```
make run-all
```

This will first run `request_data.py` to fetch the latest data, and then execute all other analysis scripts.

### Running Individual Scripts

To run a specific script:

```
make run-SCRIPTNAME
```

Replace SCRIPTNAME with the name of the script you want to run (without the .py extension).

For example:
```
make run-energy_labels
```

### Available Scripts

- `request_data.py`: Fetches the latest data from Elasticsearch.
- `brændeovn.py`: Analyzes wood stove data.
- `building_area.py`: Processes building area information.
- `construction_years.py`: Analyzes building construction years.
- `energy_label_age.py`: Examines the age of energy labels.
- `energy_labels_year_of_contruction.py`: Correlates energy labels with construction years.
- `energy_labels.py`: Provides an overview of energy label distribution.
- `heating_matrix.py`: Analyzes heating installation types and mediums.
- `supplementary_heating.py`: Examines supplementary heating systems.
- `unit_usage_140_vs_energy_label_validity.py`: Analyzes energy label validity for specific unit usage.
- `units_usage_energy_label_validity.py`: Examines energy label validity across different unit usages.

## Output

Each script generates an Excel file in the `output/` directory with detailed data and a summary sheet containing key statistics.

## Customization

- To modify Elasticsearch queries, edit the corresponding files in the `query/` directory.
- To add new analysis scripts, create a new Python file and update the Makefile to include it in the `SCRIPTS` variable.

## Requirements

Python packages required for this project are listed in `requirements.txt`. They are automatically installed in the Docker container.

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

GET SOME!