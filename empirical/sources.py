import requests, json
import pandas as pd
# Density and population data, US only


def get_census():
    """ US Census data by county ... a little old :) """
    data = requests.get('https://api.census.gov/data/2019/pep/population?get=DENSITY,POP,NAME&for=county:*').json()
    headings = [h.lower() for h in data[0]]
    census = pd.DataFrame(columns=headings, data=data[1:])
    census['pop']     = census['pop'].astype(float)
    census['density'] = census['density'].astype(float)
    return census


def get_nyt():
    """ New York Times case data by county """
    counties = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
    counties['deaths'] = counties['deaths'].astype(float)
    counties['cases'] = counties['cases'].astype(float)
    return counties

def merge_recent(nyt, census):
    """ NYT most recent case count only merged with census density data """
    nyt['name'] = [county + ', ' + state for county, state in zip(nyt['county'].values, nyt['state'].values)]
    del nyt['county']
    del nyt['state']
    sorted_cases = nyt[:len(nyt)].sort_values(by=['name', 'date'], inplace=False)
    recent_cases = sorted_cases.drop_duplicates(subset=['name'], keep='last')
    census['name'] = [n.replace(' County', '').replace(' Parish', '') for n in census['name'].values]
    merged = recent_cases.merge(census, on=["name"])
    return merged

if __name__=="__main__":
    nyt    = get_nyt()
    census = get_census()
    merged = merge_recent(nyt, census)
    print(merged[:4])

