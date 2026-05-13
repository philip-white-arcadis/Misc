from dash import html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash
from data import MIN_DATE, MAX_DATE, trips_table, route_ids, DIRECTIONS

dash.register_page(__name__, path="/frequency", title="Frequency")


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Daily Trips by Route",
                        ),
                        dbc.Col(
                            [
                                dcc.DatePickerRange(
                                    id="freq_heatmap_date_picker",
                                    min_date_allowed=MIN_DATE,
                                    max_date_allowed=MAX_DATE,
                                    start_date=MIN_DATE,
                                    end_date=MAX_DATE,
                                ),
                            ]
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H1(
                            "Hourly Trips by Route, Date, Direction",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Dropdown(
                                            route_ids,
                                            route_ids[0],
                                            id="freq_bar_route_select",
                                        ),
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        dcc.DatePickerSingle(
                                            id="freq_bar_date_picker",
                                            min_date_allowed=MIN_DATE,
                                            max_date_allowed=MAX_DATE,
                                            date=MIN_DATE,
                                        ),
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        dcc.RadioItems(
                                            options=["IB", "OB"],
                                            value="IB",
                                            id="direction_radio",
                                        ),
                                    ],
                                    width=4,
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="freq_heatmap",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="freq_bar",
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
    ],
    fluid=True,
)


@callback(
    Output("freq_heatmap", "figure"),
    Input("freq_heatmap_date_picker", "start_date"),
    Input("freq_heatmap_date_picker", "end_date"),
)
def update_freq_heatmap(start_date, end_date):
    df_grouped = (
        trips_table.groupby(["trip_date", "route"])
        .agg(num_trips=pd.NamedAgg("trip_date", "count"))
        .reset_index()
    )
    dff = df_grouped.loc[
        (df_grouped["trip_date"] >= start_date) & (df_grouped["trip_date"] <= end_date)
    ]
    dff["route"] = dff["route"].astype(str)
    pivot = dff.pivot(index="route", columns="trip_date", values="num_trips")
    return px.imshow(
        pivot,
        labels={"x": "Date", "y": "Route", "color": "Number of Trips"},
        x=pivot.columns,
        y=pivot.index,
        text_auto=True,
        color_continuous_scale="BuPu",
        template="simple_white",
    )


@callback(
    Output("freq_bar", "figure"),
    Input("freq_bar_route_select", "value"),
    Input("freq_bar_date_picker", "date"),
    Input("direction_radio", "value"),
)
def update_freq_bar(selected_route, selected_date, selected_direction):
    df_grouped = (
        trips_table.groupby(["trip_date", "route", "direction", "trip_start_hour"])
        .agg(num_trips=pd.NamedAgg("trip_date", "count"))
        .reset_index()
    )
    dff = df_grouped.loc[
        (df_grouped["route"] == int(selected_route))
        & (df_grouped["trip_date"] == selected_date)
        & (df_grouped["direction"] == int(DIRECTIONS[(selected_direction)]))
    ]
    return px.bar(
        dff,
        x="trip_start_hour",
        y="num_trips",
        template="simple_white",
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={"trip_start_hour": "Trip Start Hour", "num_trips": "Number of Trips"},
    )
