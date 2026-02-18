import geopandas as gpd
import pandas as pd
from pathlib import Path

data_dir = Path("./data")
gdfs = []
for file in data_dir.rglob("*.geojson"):
    gdf = gpd.read_file(file)
    gdfs.append(gdf)
combined = pd.concat(gdfs)
gdf = gpd.GeoDataFrame(combined, geometry="geometry", crs=4326)

gdf["% Non-White"] = round(gdf["pct_non_white"] * 100, 1).astype(str) + "%"
gdf["% 0-Car Households"] = round(gdf["pct_0_car_hh"] * 100, 1).astype(str) + "%"
gdf["% Commute by Transit"] = (
    round(gdf["pct_commute_transit"] * 100, 1).astype(str) + "%"
)
gdf["Median Household Income"] = gdf["median_hh_income"].apply(lambda x: f"${x:,.0f}")
gdf["Population Density"] = round(gdf["people_per_acre"], 1).astype(str)
gdf["Median Age"] = gdf["median_age"]

cols = [
    "pct_non_white",
    "pct_0_car_hh",
    "pct_commute_transit",
    "% Non-White",
    "% 0-Car Households",
    "% Commute by Transit",
    "median_hh_income",
    "people_per_acre",
    "Median Household Income",
    "Population Density",
]

print(gdf[cols])

gdf.to_parquet("./combined.parquet")
