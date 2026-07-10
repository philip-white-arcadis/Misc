from dash import html, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from datetime import timedelta
from data import min_date, max_date, daily_trip_counts, template, continous_color_scale

dash.register_page(__name__, path="/", title="Trip Counts")


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
                                    id="trip_counts_date_picker",
                                    min_date_allowed=min_date,
                                    max_date_allowed=max_date,
                                    start_date=max_date - timedelta(days=30),
                                    end_date=max_date,
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
                            id="trip_counts",
                        ),
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
)


@callback(
    Output("trip_counts", "figure"),
    Input("trip_counts_date_picker", "start_date"),
    Input("trip_counts_date_picker", "end_date"),
)
def update_daily_trips_counts(start_date, end_date):
    dff = daily_trip_counts.loc[
        :,
        (daily_trip_counts.columns >= start_date)
        & (daily_trip_counts.columns <= end_date),
    ]
    return px.imshow(
        dff,
        labels={"x": "Date", "y": "Route", "color": "Number of Trips"},
        x=dff.columns,
        y=dff.index,
        text_auto=True,
        color_continuous_scale=continous_color_scale,
        template=template,
    )
