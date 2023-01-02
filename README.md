
## About the Project

This project aims to compare the infection, testing, and vaccination rates between the incarcerated population and general population per county in California. 

We created our general population dataset from three California Department of Public Health (CDPH) sources: (1) [COVID-19 Cases and Tests Data](https://data.chhs.ca.gov/dataset/covid-19-time-series-metrics-by-county-and-state), (2) [COVID-19 Hospitalizations Data](https://data.ca.gov/dataset/covid-19-hospital-data1), and (3) [COVID-19 Vaccinations Data](https://data.ca.gov/dataset/covid-19-vaccine-progress-dashboard-data).

[Here](https://docs.google.com/document/d/1d-PkM3s3SorPtotlGKZfzX9av5lEaUio4aK-8DaCEX4/edit?usp=sharing) is the code documentation for how data from each source was pulled, cleaned, and merged together into the final dataframe (general_population.csv). Additionally, we included concerns on missing data and methodology from each dataset. [Here](https://docs.google.com/spreadsheets/d/1BwgTPnUbJPn25yfbjsm6uo3LlEorqG23wErnbmlDPmU/edit?usp=sharing) is the documentation of each source, including which columns were chosen, their definitions, and additional clarifying information.

Please contact info@covidincustody.org for any questions or concerns.

## Usage

There are no prerequisites or installation required. Data from all sources will be pulled directly from the webpage, and an output csv (general_population.csv) will be stored in the same directory as `utils.py` and `run.py`. Once both files are downloaded, please run the following:

```bash
python3 run.py
```
