import pandas as pd

trips_table = pd.read_parquet("./data/2026-1-1_2026-7-7_processed.parquet")

# constants
min_date = trips_table.trip_date.min()
max_date = trips_table.trip_date.max()

route_names = trips_table.route_name.unique().tolist()

direction_names = trips_table.direction_name.unique().tolist()

template = "simple_white"

continous_color_scale = "Blues"

# add missing dates
dates = pd.date_range(trips_table.trip_date.min(), trips_table.trip_date.max())
dates_trips_table = pd.DataFrame({"date": dates})
trips_table = dates_trips_table.merge(
    trips_table,
    how="left",
    left_on=dates_trips_table["date"],
    right_on=trips_table["survey_date"],
)

# agg tables
daily_trips = (
    trips_table.groupby(["date", "route_name"], dropna=False)
    .agg(
        num_trips=pd.NamedAgg("trip_date", "count"),
        total_ons=pd.NamedAgg("total_passengers_on", "sum"),
    )
    .reset_index()
)

daily_trip_counts = daily_trips.pivot(
    index="route_name", columns="date", values="num_trips"
).fillna(0)

daily_boardings = daily_trips.pivot(
    index="route_name", columns="date", values="total_ons"
).fillna(0)

monthly_boardings = (
    trips_table.groupby(["trip_month", "trip_month_name", "route_name"])
    .agg(total_ons=pd.NamedAgg("total_passengers_on", "sum"))
    .reset_index()
)
