import pandas as pd
import datetime

in_file = "./data/2026-1-1_2026-7-7.parquet"
out_file = "./data/2026-1-1_2026-7-7_processed.parquet"

df = pd.read_parquet(in_file)

cols_to_keep = [
    "SURVEY_DATE",
    "ROUTE_NAME",
    "ROUTE_NUMBER",
    "DIRECTION_NAME",
    "PATTERN_KEY",
    "TRIP_KEY",
    "TRIP_START_TIME",
    "TRIP_END_TIME",
    "ACTUAL_START_TIME",
    "ACTUAL_END_TIME",
    "ACTUAL_RUNNING_TIME",
    "SERVICE_PERIOD",
    "TIME_PERIOD",
    "ACTUAL_SPEED",
    "DWELL_TIME_AVG",
    "GARAGE_NAME",
    "MAX_LOAD",
    "MAX_LOAD_P",
    "MIN_LOAD",
    "ONTIME",
    "ONTIME_DIFF_AVG",
    "PASS_PER_HOUR",
    "PASS_PER_MILE",
    "REVENUE_HOURS",
    "REVENUE_MILES",
    "SCHEDULED_RUNNING_TIME",
    "SCHEDULED_SPEED",
    "SERVICE_DAY",
    "TOTAL_DWELL_TIME",
    "TOTAL_PASSENGER_MILES",
    "TOTAL_PASSENGERS_IN",
    "TOTAL_PASSENGERS_OFF",
    "TOTAL_PASSENGERS_ON",
    "TOTAL_SEAT_MILES",
    "TOTAL_STOPS",
]
df = df[cols_to_keep]

df.columns = [col.lower() for col in df.columns]

df["route_name"] = df["route_name"].astype(str)
df["survey_date"] = pd.to_datetime(df["survey_date"])

df["trip_date"] = df["survey_date"].dt.date
df["trip_month"] = df["survey_date"].dt.month
df["trip_month_name"] = df["survey_date"].dt.month_name()

df = df[df["time_period"].notna()]

df = df.sort_values(
    ["survey_date", "route_name", "direction_name", "pattern_key", "trip_start_time"]
)

df.to_parquet(out_file)
