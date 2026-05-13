import pandas as pd
import numpy as np
import geopandas as gpd
import requests

api_key_path = (
    "../../../Users/whitep8140/OneDrive - ARCADIS/Documents/_General/census_api_key.txt"
)
with open(api_key_path, "r") as f:
    api_key = f.readline().strip()

# see this for what is avaible: https://www.census.gov/data/developers/data-sets.html#accordion-a8ec3eb6f0-item-e2df35399d
year = 2024
dataset = "acs5"

# see this for geo codes https://www.census.gov/library/reference/code-lists/ansi.html
places = [
    # (place name, statefp, countyfp, countyname)
    ("Boston", "25", "025", "Suffolk County"),
    ("Baltimore County", "24", "005", "Baltimore County"),
    ("Baltimore City", "24", "510", "Baltimore City"),
    ("Minneapolis", "27", "053", "Hennepin County"),
    ("St Paul", "27", "123", "Ramsey County"),
    ("Denver", "08", "031", "Denver County"),
    ("Portland", "41", "051", "Multnomah County"),
    ("Philadelphia", "42", "101", "Philadelphia County"),
    ("Chicago", "17", "031", "Cook County"),
    ("Washington DC", "11", "001", "District of Columbia"),
    ("Seattle", "53", "033", "King County"),
    ("Salt Lake City", "49", "035", "Salt Lake County"),
    ("San Fransisco", "06", "075", "San Francisco County"),
    ("Los Angeles", "06", "037", "Los Angeles County"),
    ("Pittsburgh", "42", "003", "Allegheny County"),
    ("Detroit", "26", "163", "Wayne County"),
    ("Fairfax County", "51", "059", "Fairfax County"),
    ("Arlington County", "51", "013", "Arlington County"),
    ("Montgomery County", "24", "031", "Montgomery County"),
    ("Prince George's County", "24", "033", "Prince George's County"),
]

variables = {
    "NAME": "name",
    "B01001_001E": "total_pop",
    "B01001A_001E": "total_pop_white_alone",
    "B08201_001E": "total_hh",
    "B08201_002E": "total_hh_0_car",
    "B19013_001E": "median_hh_income",
    "B01002_001E": "median_age",
    "B08301_001E": "total_commute_all",
    "B08301_010E": "total_commute_transit",
}

url_stem_demo = "https://api.census.gov/data"
url_stem_geo = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb"

print(f"Downloading {dataset} data for {year}")
for place in places:
    print("  Downloading demographic data for", place[0])
    url = f"{url_stem_demo}/{year}/acs/{dataset}?get={','.join(variables.keys())}&for=tract:*&in=state:{place[1]}&in=county:{place[2]}&key={api_key}"
    r = requests.get(url)
    if r.status_code == 200:
        columns = r.json()[0]
        data = r.json()[1:]
        df = pd.DataFrame(data=np.array(data), columns=columns)
        df.columns = [
            variables[col] if col in variables.keys() else col for col in df.columns
        ]

        df["pct_non_white"] = 1 - (
            df["total_pop_white_alone"].astype(int) / df["total_pop"].astype(int)
        )
        df["pct_0_car_hh"] = df["total_hh_0_car"].astype(int) / df["total_hh"].astype(
            int
        )
        df["pct_commute_transit"] = df["total_commute_transit"].astype(int) / df[
            "total_commute_all"
        ].astype(int)

        if "Baltimore" in place[0]:
            peer = "Baltimore"
        elif place[0] == "St Paul":
            peer = "Minneapolis"
        elif place[0] in [
            "Arlington County",
            "Fairfax County",
            "Montgomery County",
            "Prince George's County",
        ]:
            peer = "Washington DC"
        else:
            peer = place[0]
        df["peer"] = peer

        df.to_csv(f"acs_5_year_2024_{place[0]}.csv", index=False)
    else:
        print(r.text, f"url: {r.url}", sep="\n")

    print("  Downloading geographic data for", place[0])
    url = f"{url_stem_geo}/Tracts_Blocks/MapServer/7/query"
    params = {
        "where": f"STATE='{place[1]}' AND COUNTY='{place[2]}'",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        gdf = gpd.GeoDataFrame.from_features(data, crs=4326)
        gdf = gdf.merge(df, how="left", left_on="TRACT", right_on="tract")

        gdf["people_per_acre"] = gdf["total_pop"].astype(int) / (
            gdf["AREALAND"].astype(int) / 4046.9
        )

        for col in variables.values():
            if col != "name":
                gdf[col] = gdf[col].astype(float)

        gdf.to_file(f"acs_5_year_2024_{place[0]}.geojson", driver="GeoJSON")
    else:
        print(r.text, f"url: {r.url}", sep="\n")
