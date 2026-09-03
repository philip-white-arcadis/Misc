from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import tomllib


def make_df(gtfs_zip: ZipFile, file_name: str, types: dict = None) -> pd.DataFrame:
    with gtfs_zip.open(file_name + ".txt") as file:
        return pd.read_csv(file, dtype=types)


def save_df(df: pd.DataFrame, gtfs_zip: ZipFile, file_name: str) -> None:
    with gtfs_zip.open(file_name + ".txt", mode="w") as file:
        df.to_csv(file, index=False)
    print(f"Saved {file_name}.txt to {gtfs_zip.filename}")


with open("./config.toml", "rb") as f:
    config = tomllib.load(f)

gtfs_zip_file = ZipFile(Path(config["gtfs_zip_path"]))
print(f"Using gtfs zip file: {gtfs_zip_file.filename}")
print()

# read in and then filter the core files
# may have to change the types based on the columns present in the gtfs in question working with
# e.g., "stop_headsign" is optional in stop_times, so may need to be removed below
routes = make_df(gtfs_zip_file, "routes", {"route_id": str})
trips = make_df(
    gtfs_zip_file, "trips", {"trip_id": str, "route_id": str, "trip_short_name": str}
)
stop_times = make_df(
    gtfs_zip_file, "stop_times", {"stop_id": str, "trip_id": str, "stop_headsign": str}
)
stops = make_df(gtfs_zip_file, "stops", {"stop_id": str})
shapes = make_df(gtfs_zip_file, "shapes", {"shape_id": str, "trip_id": str})

routes_filtered = routes[routes["route_id"].isin(config["route_ids"])]
trips_filtered = trips[trips["route_id"].isin(config["route_ids"])]
stop_times_filtered = stop_times[
    stop_times["trip_id"].isin(trips_filtered["trip_id"].unique())
]
shapes_filtered = shapes[shapes["shape_id"].isin(trips_filtered["shape_id"].unique())]
# need to take into account parent stations for stops
st_stop_ids = stop_times_filtered["stop_id"].unique()
stops_filtered = stops[stops["stop_id"].isin(st_stop_ids)]
no_parent = stops_filtered[stops_filtered["parent_station"].isna()]
has_parent = stops_filtered[stops_filtered["parent_station"].notna()]
# get all the stops entities for the parent_station for stops with a parent
stop_parents = stops[stops["parent_station"].isin(has_parent["parent_station"])]
stops_filtered = pd.concat([no_parent, stop_parents])

print(
    f"Filtered routes from {len(routes)} to {len(routes_filtered)}.",
    f"Filtered trips from {len(trips)} to {len(trips_filtered)}.",
    f"Filtered stop_times from {len(stop_times)} to {len(stop_times_filtered)}.",
    f"Filtered stops from {len(stops)} to {len(stops_filtered)}.",
    f"Filtered shapes from {len(shapes)} to {len(shapes_filtered)}.",
    sep="\n",
)
print()

# build dict of dfs for all other files
dfs = {}
for file in [
    f
    for f in gtfs_zip_file.namelist()
    if f not in ["routes.txt", "trips.txt", "stop_times.txt", "shapes.txt", "stops.txt"]
]:
    file_name = file.replace(".txt", "")
    df = make_df(gtfs_zip_file, file_name)
    dfs[file_name] = df

# search other dfs for references to filtered cols
cols = ["route_id", "trip_id", "shape_id", "stop_id"]
for col in cols:
    for file, df in dfs.items():
        if col in df.columns:
            len_before = len(dfs[file])
            match col:
                case "route_id":
                    dfs[file] = df.loc[df["route_id"].isin(routes_filtered["route_id"])]
                case "trip_id":
                    dfs[file] = df.loc[df["trip_id"].isin(trips_filtered["trip_id"])]
                case "shape_id":
                    dfs[file] = df.loc[df["shape_id"].isin(shapes_filtered["shape_id"])]
                case "stop_id":
                    dfs[file] = df.loc[df["stop_id"].isin(stops_filtered["stop_id"])]
            print(f"Used {col} to filter {file} from {len_before} to {len(dfs[file])}.")
print()

# save new files
filtered_gtfs_zip_file = ZipFile(Path(config["output_gtfs_path"]), mode="w")
save_df(routes_filtered, filtered_gtfs_zip_file, "routes")
save_df(trips_filtered, filtered_gtfs_zip_file, "trips")
save_df(stop_times_filtered, filtered_gtfs_zip_file, "stop_times")
save_df(stops_filtered, filtered_gtfs_zip_file, "stops")
save_df(shapes_filtered, filtered_gtfs_zip_file, "shapes")
for file, df in dfs.items():
    save_df(df, filtered_gtfs_zip_file, file)
print()

print(f"Saved filtered gtfs files to {config['output_gtfs_path']}")
