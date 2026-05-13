import pandas as pd

apc_table = pd.read_csv("./data/apc.csv")
trips_table = pd.read_csv("./data/trips.csv")
stops_table = pd.read_csv("./data/stops.csv")

MIN_DATE = trips_table.trip_date.min()
MAX_DATE = trips_table.trip_date.max()

route_ids = sorted(trips_table.route.unique().tolist())

DIRECTIONS = {"IB": "1", "OB": "2"}

variants = (
    apc_table.groupby(["route", "direction"])
    .agg(variants_list=pd.NamedAgg("variant", lambda x: sorted(list(set(x)))))
    .reset_index()
)

ROUTE_VARIANTS = {}

for idx, row in variants.iterrows():
    # print(row["route"], row["direction"], row["variants_list"])
    route, dir, variants_list = row["route"], row["direction"], row["variants_list"]
    if route in ROUTE_VARIANTS:
        ROUTE_VARIANTS[route][dir] = variants_list
    else:
        ROUTE_VARIANTS[route] = {}
        ROUTE_VARIANTS[route][dir] = variants_list
