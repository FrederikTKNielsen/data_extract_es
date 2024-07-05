# ES_DATA_ANALYSE Project

This project is designed to analyze and process data from Elasticsearch queries related to building information, energy labels, and heating systems in various municipalities.

## Project Structure

```
ES_DATA_ANALYSE/
├── data/                 # Input data directory (not tracked by Git)
├── output/               # Output directory for analysis results (not tracked by Git)
├── query/                # Elasticsearch query files
├── templates/            # HTML templates for the web interface
├── app.py                # Flask application for web interface
├── brændeovn.py
├── building_area.py
├── building_area_small.py
├── construction_years.py
├── dockerfile
├── docker-compose.yaml
├── docker-compose.prod.yaml
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

1. Ensure you have Docker and Docker Compose installed on your system.
2. Clone this repository to your local machine:
   ```
   git clone https://github.com/Frederiktk/es_data_analyse.git
   ```
3. Navigate to the project directory:
   ```
   cd es_data_analyse
   ```

## Usage

### Running the Web Interface

To start the web interface for easy script execution:

```
make build
make run
```

This will build the Docker image if necessary and start the Flask application. Access the web interface at `http://localhost:5001`.


### Available Scripts

- `request_data.py`: Fetches the latest data from Elasticsearch.
- `brændeovn.py`: Analyzes wood stove data.
- `building_area.py`: Processes building area information.
- `building_area_small.py`: Analyzes smaller building areas.
- `construction_years.py`: Analyzes building construction years.
- `energy_label_age.py`: Examines the age of energy labels.
- `energy_labels_year_of_contruction.py`: Correlates energy labels with construction years.
- `energy_labels.py`: Provides an overview of energy label distribution.
- `heating_matrix.py`: Analyzes heating installation types and mediums.
- `supplementary_heating.py`: Examines supplementary heating systems.
- `unit_usage_140_vs_energy_label_validity.py`: Analyzes energy label validity for specific unit usage.
- `units_usage_energy_label_validity.py`: Examines energy label validity across different unit usages.

## Output

Each script generates an Excel file in the `output/` directory with detailed data and a summary sheet containing key statistics. These files are not tracked by Git to keep the repository size manageable.

## Customization

- To modify Elasticsearch queries, edit the corresponding files in the `query/` directory.
- To add new analysis scripts, create a new Python file and update the `app.py` file to include it in the `SCRIPTS` list.

## Requirements

Python packages required for this project are listed in `requirements.txt`. They are automatically installed in the Docker container for the production environment.

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request