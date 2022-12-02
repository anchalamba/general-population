import pandas as pd
import numpy as np
import math
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

def generalPopDF():
    """
    generalPopDF pulls per-county COVID-19 data from three CDPH sources, cleans, and merges it into one dataframe
    """
    # pulling in tests/cases data from CDPH
    tests_cases = pd.read_csv("https://data.chhs.ca.gov/dataset/f333528b-4d38-4814-bebb-12db1f10f535/resource/046cdd2b-31e5-4d34-9ed3-b48cdbc4be7a/download/covid19cases_test.csv", \
                              usecols = ['date', 'area', 'population', 'reported_cases', 'cumulative_reported_cases', 'reported_deaths', 'cumulative_reported_deaths', 'reported_tests'])

    # manually creating a column for Tests (General population, current), as it is currently missing in the dataset
    tests_cases['cumulative_reported_tests'] = tests_cases['reported_tests'].cumsum(skipna=True)

    # removing entries where County is “California”, “Unknown” or “Out of State”
    tests_cases = tests_cases.loc[~tests_cases['area'].isin(['California', 'Unknown', 'Out of state'])]

    # removing entries where As of Date is NA
    tests_cases = tests_cases.loc[~tests_cases['date'].isnull()]

    # pulling in hospitalizations data from CDPH
    hospitalizations = pd.read_csv("https://data.chhs.ca.gov/dataset/2df3e19e-9ee4-42a6-a087-9761f82033f6/resource/47af979d-8685-4981-bced-96a6b79d3ed5/download/covid19hospitalbycounty.csv", \
                                   usecols = ['county', 'todays_date','hospitalized_covid_confirmed_patients'])

    # pulling in vaccinations data from CDPH
    vaccinations = pd.read_csv("https://data.chhs.ca.gov/dataset/e283ee5a-cf18-4f20-a92c-ee94a2866ccd/resource/130d7ba2-b6eb-438d-a412-741bde207e1c/download/covid19vaccinesbycounty.csv", \
                               usecols = ['county', 'administered_date', 'fully_vaccinated', 'cumulative_fully_vaccinated', 'booster_recip_count', 'cumulative_booster_recip_count'])

    # removing entries where County is “All CA Counties”, “All CA and Non-CA Counties”, “Unknown” or “Outside California”
    vaccinations = vaccinations.loc[~vaccinations['county'].isin(['All CA Counties', 'All CA and Non-CA Counties', 'Outside California', 'Unknown'])]
    vaccinations = vaccinations.loc[vaccinations['administered_date'] != '2020-01-05']

    # removing entries which had 01/05/20 in As of Date (outlier, not relevant)
    hospitalizations = hospitalizations.rename({'county': 'area', 'todays_date': 'date'}, axis=1)
    vaccinations = vaccinations.rename({'county': 'area', 'administered_date': 'date'}, axis=1)

    # merging tests/cases and hospitalizations data
    df = pd.merge(tests_cases, hospitalizations, how='left', on=['area', 'date'])

    # merging above with vaccinations data
    df2 = pd.merge(df, vaccinations, how='left', on=['area', 'date'])

    # Pulling Census 2020 + 2021 Estimates
    df = pd.read_csv(
        "https://www2.census.gov/programs-surveys/popest/datasets/2020-2021/counties/totals/co-est2021-alldata.csv",
        encoding='latin-1', index_col=False)

    # temporarily removing "County" from the county name e.g. Alameda County for mapping to the original data
    df['CTYNAME'] = df['CTYNAME'].str.split(' ').str[0]

    # Census Bureau values for As of Date = 2020
    popEst2020_df = df.loc[df['STNAME'] == 'California'][1:][['CTYNAME', 'ESTIMATESBASE2020']]
    popEst2020 = popEst2020_df.set_index('CTYNAME')['ESTIMATESBASE2020'].to_dict()

    # Census Bureau estimates for As of Date = 2021
    popEst2021_df = df.loc[df['STNAME'] == 'California'][1:][['CTYNAME', 'POPESTIMATE2021']]
    popEst2021 = popEst2021_df.set_index('CTYNAME')['POPESTIMATE2021'].to_dict()

    # California Department of Finance estimates for As of Date = 2022 (January 2022)
    popEst2022 = {'Alameda': 1651979, 'Alpine': 1200, 'Amador': 40297, 'Butte': 201608, 'Calaveras': 45049,
                  'Colusa': 21807, 'Contra Costa': 1156555, 'Del Norte': 27218, 'El Dorado': 190465, 'Fresno': 1011273,
                  'Glenn': 28750, 'Humboldt': 135168, 'Imperial': 179329, 'Inyo': 18978, 'Kern': 909813,
                  'Kings': 152023, 'Lake': 67407, 'Lassen': 30274, 'Los Angeles': 9861224, 'Madera': 157396,
                  'Marin': 257135, 'Mariposa': 17045, 'Mendocino': 89999, 'Merced': 284338, 'Modoc': 8690,
                  'Mono': 13379, 'Monterey': 433716, 'Napa': 136179, 'Nevada': 101242, 'Orange': 3162245,
                  'Placer': 409025, 'Plumas': 18942, 'Riverside': 2435525, 'Sacramento': 1576618, 'San Benito': 65479,
                  'San Bernardino': 2187665, 'San Diego': 3287306, 'San Francisco': 842754, 'San Joaquin': 784298,
                  'San Luis Obispo': 280721, 'San Mateo': 744662, 'Santa Barbara': 445164, 'Santa Clara': 1894783,
                  'Santa Cruz': 266564, 'Shasta': 180531, 'Sierra': 3229, 'Siskiyou': 43830, 'Solano': 447241,
                  'Sonoma': 482404, 'Stanislaus': 549466, 'Sutter': 99145, 'Tehama': 65052, 'Trinity': 16023,
                  'Tulare': 475014, 'Tuolumne': 55291, 'Ventura': 833652, 'Yolo': 221165, 'Yuba': 82275}

    # splitting up the final dataset by year so it is easier to replace the stagnant Population (General population, current) values by year
    df2020 = df2.loc[df2['date'].str.startswith('2020')]
    df2020['population'] = df2020['area'].map(popEst2020)

    df2021 = df2.loc[df2['date'].str.startswith('2021')]
    df2021['population'] = df2021['area'].map(popEst2021)

    df2022 = df2.loc[df2['date'].str.startswith('2022')]
    df2022['population'] = df2022['area'].map(popEst2022)

    # combining split dataframes by year into one dataframe
    final_df = pd.concat([df2020, df2021, df2022])

    # converting all the float columns into integer columns to match format e.g. Santa Rita Jail Data
    final_df[final_df.columns.tolist()[3:]] = final_df[final_df.columns.tolist()[3:]].astype('Int64')

    # manually calculating and creating Percent of Population Fully Vaccinated (General population) column
    final_df['Percent of Population Fully Vaccinated (General population)'] = final_df['cumulative_fully_vaccinated'] / \
                                                                              final_df['population'] * 100
    final_df['Percent of Population Fully Vaccinated (General population)'] = final_df[
        'Percent of Population Fully Vaccinated (General population)'].round(2)

    # manually calculating and creating Percent of Population Fully Boosted (General population) column
    final_df['Percent of Population Boosted (General population)'] = final_df['cumulative_booster_recip_count'] / \
                                                                     final_df['population'] * 100
    final_df['Percent of Population Boosted (General population)'] = final_df[
        'Percent of Population Boosted (General population)'].round(2)

    # renaming columns to match format e.g. Santa Rita Jail Data
    final_df = final_df.rename(
        {'date': 'As of Date', 'area': 'County', 'population': 'Population (General population, current)',
         'reported_cases': 'Confirmed Cases (General population, current)',
         'cumulative_reported_cases': 'Confirmed Cases (General population, cumulative)',
         'reported_deaths': 'Deaths (General population, current)',
         'cumulative_reported_deaths': 'Deaths (General population, cumulative)',
         'reported_tests': 'Tests (General population, current)',
         'cumulative_reported_tests': 'Tests (General population, cumulative)',
         'hospitalized_covid_confirmed_patients': 'Hospitalizations (General population, current)',
         'fully_vaccinated': 'Fully Vaccinated (General population, current)',
         'cumulative_fully_vaccinated': 'Fully Vaccinated (General population, cumulative)',
         'booster_recip_count': 'Boosted (General population, current)',
         'cumulative_booster_recip_count': 'Boosted (General population, cumulative)'}, axis=1)

    # reordering columns to match format e.g. Santa Rita Jail Data
    final_df = final_df[['As of Date', 'County', 'Confirmed Cases (General population, current)',
                         'Confirmed Cases (General population, cumulative)', 'Deaths (General population, current)',
                         'Deaths (General population, cumulative)', 'Tests (General population, current)',
                         'Tests (General population, cumulative)', 'Population (General population, current)',
                         'Hospitalizations (General population, current)',
                         'Fully Vaccinated (General population, current)',
                         'Fully Vaccinated (General population, cumulative)', 'Boosted (General population, current)',
                         'Boosted (General population, cumulative)',
                         'Percent of Population Fully Vaccinated (General population)',
                         'Percent of Population Boosted (General population)']]

    # add 'County' to each value in the 'County' column
    final_df['County'] = final_df['County'].astype(str) + ' County'

    filepath = Path('general_population.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(filepath, index=False)

    return final_df