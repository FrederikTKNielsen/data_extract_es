# ES_DATA_ANALYSE Project

This project is designed to analyze and process data from Elasticsearch queries related to building information, energy labels, and heating systems in various municipalities.

## Project Structure

```
ES_DATA_ANALYSE/
├── app.py                  # Flask application for web interface
├── data/                   # Input data directory (generated at runtime)
├── output/                 # Output directory for analysis results (generated at runtime)
├── query/                  # Elasticsearch query files
├── templates/              # HTML templates for the web interface
├── scripts/                # Python scripts for data analysis
│   ├── brændeovn_pejs.py
│   ├── building_area.py
│   ├── building_area_small.py
│   ├── construction_years.py
│   ├── energy_label_age.py
│   ├── energy_labels.py
│   ├── energy_labels_year_of_construction.py
│   ├── heating_matrix.py
│   ├── null_heating_installation.py
│   ├── supplementary_heating.py
│   ├── unit_areas.py
│   ├── unit_usage_140_vs_energy_label_validity.py
│   ├── units_usage_all_energy_label_validity.py
│   ├── units_usage_energy_label_validity.py
│   ├── year_extension_vs_construction.py
│   ├── buildings_1000.py
│   ├── large_buildings_energy_labels.py
│   └── 9_heating_installation_null_mediums.py
├── request_data.py         # Script to fetch data from Elasticsearch
├── dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements.txt        # Python package requirements
├── makefile
└── README.md               # Project documentation

```

## Setup and Installation

1. Ensure you have Docker and Docker Compose installed on your system.
2. Clone this repository to your local machine:
   ```
   git clone this
   ```
3. Navigate to the project directory:
   ```
   cd es_data_analyse
   ```
4. create a .env file with the url:
   ```
   echo "ELASTICSEARCH_URL=http://your-elasticsearch-url" > .env
   see config.py.example
   ```
5. Build the Docker Image and Run the Application:
   ```
   make build
   make run
   ```
   
## Usage


### Running Analyses via Web Interface
   ```
   The web interface provides an easy way to run analyses, execute custom queries, and download results.
   ```
### Access the Web Interface:
   ```
   Open your web browser and navigate to http://localhost:5000.
   Run All Analyses:

   Click on "Run All Scripts" to execute all analyses.
   After completion, click on "Download All Results" to download a ZIP file containing all output files.
   Run Individual Analysis:

   Select an analysis from the "Run Individual Analysis" dropdown menu.
   Click on "Run Selected Analysis" to execute it.
   After completion, you can:
   Click "Download Output" to download the Excel output file.
   Click "Download Query" to download the corresponding Elasticsearch query.
   Run Custom Query:

   Enter your custom Elasticsearch query in JSON format in the "Run Custom Query" text area.
   Click on "Run Custom Query" to execute it.
   After execution, a download link will appear if the query was successful.
   Important Notes
   Network Access: Ensure you are connected to the VMAS network or VPN to access Elasticsearch.
   Data and Output Directories: The data/ and output/ directories are generated at runtime and are not tracked by Git.
   ```

### Available Scripts
   ```
- `brændeovn_pejs.py`: Analyzes wood stove data.
- `building_area.py`: Processes building area information.
- `building_area_small.py`: Analyzes smaller building areas.
- `construction_years.py`: Analyzes building construction years.
- `energy_label_age.py`: Examines the age of energy labels.
- `energy_labels_year_of_contruction.py`: Correlates energy labels with construction years.
- `energy_labels.py`: Provides an overview of energy label distribution.
- `heating_matrix.py`: Analyzes heating installation types and mediums.
- `supplementary_heating.py`: Examines supplementary heating systems.
- `unit_areas.py`: Processes unit area information.
- `unit_usage_140_vs_energy_label_validity.py`: Analyzes energy label validity for specific unit usage.
- `units_usage_energy_label_validity.py`: Examines energy label validity across different unit usages.
- `null_heating_installation.py`: Analyzes mediums with no heating installation types.
- `buildings_1000.py` : Analyzes building energy label where construction year = 1000.
- `units_usage_all_energy_label_validity.py` : Examines energy label validity across all unit usages.
- `large_buildings_energy_labels.py` : analysis of energy labels for large buildings (1000+ m²), excluding private unit usage codes.
- `year_extension_vs_construction.py` : Analyzes year of extension vs. construction year.
- `9_heating_installation_null_mediums.py` : Analyzes data where there are no mediums or heating installation types.
- Each script have a corresponding address script attached that gets a sample up to 1000 adresses based on the analysis
   ```

## Output
```
- Each analysis script generates an Excel file in the output/ directory.
- The output includes detailed data and a summary sheet containing key statistics.
- These files are not tracked by Git to keep the repository size manageable.
```

## Customization

### Modify Elasticsearch Queries:
```
- Edit the corresponding query files in the query/ directory.
- The query files are named to match the analysis scripts (e.g., building_area.json corresponds to building_area.py).
```
### Add New Analysis Scripts:
```
- Place your new Python script in the main directory.
- Ensure the script is designed to process data from a corresponding query.
- Update the SCRIPTS list in app.py to include your new script.
```
### Web Interface Templates:
```
- The HTML templates are located in the templates/ directory.
- Customize the web interface by editing index.html.
```
## Requirements
```
- Python Packages: All required Python packages are listed in requirements.txt.
- Docker: The application runs inside a Docker container, which handles all dependencies.
- Environment Variables: Ensure the ELASTICSEARCH_URL is set in the .env file.
```