import pandas as pd
import numpy as np
import math
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

def generalPopDF():
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

    # merging all three datasets by As of Date and County
    df = pd.merge(tests_cases, hospitalizations, how='left', on = ['area', 'date'])
    df2 = pd.merge(df, vaccinations, how='left', on = ['area', 'date'])

    # manually replacing stagnant Population (General population, current) values with data from the Census Bureau for As of Date = 2020
    # and As of Date = 2021 (July 2021 estimates) and data from the California Department of Finance for As of Date = 2022 (January 2022 estimates)
    popEst2020 = {'Alameda': 1682353, 'Alpine': 1204, 'Amador': 40474, 'Butte': 211632, 'Calaveras': 45292, 'Colusa': 21839,
                  'Contra Costa': 1165927, 'Del Norte': 27743, 'El Dorado': 191185, 'Fresno': 1008654, 'Glenn': 28917,
                  'Humboldt': 136463, 'Imperial': 179702, 'Inyo': 19016, 'Kern': 909235, 'Kings': 152486, 'Lake': 68163,
                  'Lassen': 32730, 'Los Angeles': 10014009, 'Madera': 156255, 'Marin': 262321, 'Mariposa': 17131,
                  'Mendocino': 91601, 'Merced': 281202, 'Modoc': 8700, 'Mono': 13195, 'Monterey': 439035, 'Napa': 138019,
                  'Nevada': 102241, 'Orange': 3186989, 'Placer': 404739, 'Plumas': 19790, 'Riverside': 2418185,
                  'Sacramento': 1585055, 'San Benito': 64209, 'San Bernardino': 2181654, 'San Diego': 3298634,
                  'San Francisco': 873965, 'San Joaquin': 779233, 'San Luis Obispo': 282424, 'San Mateo': 764442,
                  'Santa Barbara': 448229, 'Santa Clara': 1936259, 'Santa Cruz': 270861, 'Shasta': 182155, 'Sierra': 3236,
                  'Siskiyou': 44076, 'Solano': 453491, 'Sonoma': 488863, 'Stanislaus': 552878, 'Sutter': 99633, 'Tehama': 65829,
                  'Trinity': 16112, 'Tulare': 473117, 'Tuolumne': 55620, 'Ventura': 843843, 'Yolo': 216403, 'Yuba': 81575}
    popEst2021 = {'Alameda': 1648556, 'Alpine': 1235, 'Amador': 41259, 'Butte': 208309, 'Calaveras': 46221, 'Colusa': 21917,
                  'Contra Costa': 1161413, 'Del Norte': 28100, 'El Dorado': 193221, 'Fresno': 1013581, 'Glenn': 28805,
                  'Humboldt': 136310, 'Imperial': 179851, 'Inyo': 18970, 'Kern': 917673, 'Kings': 153486, 'Lake': 68766,
                  'Lassen': 33159, 'Los Angeles': 9829544, 'Madera': 159410, 'Marin': 260206, 'Mariposa': 17147,
                  'Mendocino': 91305, 'Merced': 286461, 'Modoc': 8661, 'Mono': 13247, 'Monterey': 437325, 'Napa': 136207,
                  'Nevada': 103487, 'Orange': 3167809, 'Placer': 412300, 'Plumas': 19915, 'Riverside': 2458395,
                  'Sacramento': 1588921, 'San Benito': 66677, 'San Bernardino': 2194710, 'San Diego': 3286069,
                  'San Francisco': 815201, 'San Joaquin': 789410, 'San Luis Obispo': 283159, 'San Mateo': 737888,
                  'Santa Barbara': 446475, 'Santa Clara': 1885508, 'Santa Cruz': 267792, 'Shasta': 182139, 'Sierra': 3283,
                  'Siskiyou': 44118, 'Solano': 451716, 'Sonoma': 485887, 'Stanislaus': 552999, 'Sutter': 99063, 'Tehama': 65498,
                  'Trinity': 16060, 'Tulare': 477054, 'Tuolumne': 55810, 'Ventura': 839784, 'Yolo': 216986, 'Yuba': 83421}
    popEst2022 = {'Alameda': 1651979, 'Alpine': 1200, 'Amador': 40297, 'Butte': 201608, 'Calaveras': 45049, 'Colusa': 21807,
                  'Contra Costa': 1156555, 'Del Norte': 27218, 'El Dorado': 190465, 'Fresno': 1011273, 'Glenn': 28750,
                  'Humboldt': 135168, 'Imperial': 179329, 'Inyo': 18978, 'Kern': 909813, 'Kings': 152023, 'Lake': 67407,
                  'Lassen': 30274, 'Los Angeles': 9861224, 'Madera': 157396, 'Marin': 257135, 'Mariposa': 17045, 'Mendocino': 89999,
                  'Merced': 284338, 'Modoc': 8690, 'Mono': 13379, 'Monterey': 433716, 'Napa': 136179, 'Nevada': 101242,
                  'Orange': 3162245, 'Placer': 409025, 'Plumas': 18942, 'Riverside': 2435525, 'Sacramento': 1576618,
                  'San Benito': 65479, 'San Bernardino': 2187665, 'San Diego': 3287306, 'San Francisco': 842754,
                  'San Joaquin': 784298, 'San Luis Obispo': 280721, 'San Mateo': 744662, 'Santa Barbara': 445164,
                  'Santa Clara': 1894783, 'Santa Cruz': 266564, 'Shasta': 180531, 'Sierra': 3229, 'Siskiyou': 43830,
                  'Solano': 447241, 'Sonoma': 482404, 'Stanislaus': 549466, 'Sutter': 99145, 'Tehama': 65052, 'Trinity': 16023,
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
    final_df['Percent of Population Fully Vaccinated (General population)'] = final_df['cumulative_fully_vaccinated']/final_df['population']*100
    final_df['Percent of Population Fully Vaccinated (General population)'] = final_df['Percent of Population Fully Vaccinated (General population)'].round(2)

    # manually calculating and creating Percent of Population Fully Boosted (General population) column
    final_df['Percent of Population Boosted (General population)'] = final_df['cumulative_booster_recip_count']/final_df['population']*100
    final_df['Percent of Population Boosted (General population)'] = final_df['Percent of Population Boosted (General population)'].round(2)

    # renaming columns to match format e.g. Santa Rita Jail Data
    final_df = final_df.rename({'date': 'As of Date', 'area': 'County', 'population': 'Population (General population, current)',
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
    final_df = final_df[['As of Date', 'County', 'Confirmed Cases (General population, current)', 'Confirmed Cases (General population, cumulative)',
                         'Deaths (General population, current)', 'Deaths (General population, cumulative)', 'Tests (General population, current)',
                         'Tests (General population, cumulative)', 'Population (General population, current)', 'Hospitalizations (General population, current)',
                         'Fully Vaccinated (General population, current)', 'Fully Vaccinated (General population, cumulative)',
                         'Boosted (General population, current)', 'Boosted (General population, cumulative)',
                         'Percent of Population Fully Vaccinated (General population)', 'Percent of Population Boosted (General population)']]

    # add 'County' to each value in the 'County' column
    final_df['County'] = final_df['County'].astype(str) + ' County'

    # writing the sample csv file output in the same directory
    # from pathlib import Path
    # filepath = Path('general_population.csv')
    # filepath.parent.mkdir(parents=True, exist_ok=True)
    # final_df.to_csv(filepath, index=False)

    return final_df

generalPopDF()