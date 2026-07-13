from dash import html, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from datetime import timedelta
from data import (
    min_date,
    max_date,
    daily_pct_reporting,
    template,
    continous_color_scale,
)

dash.register_page(__name__, path="/", title="Data Quality")


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Percentage of Trips Reported in Ridecheck Plus",
                        ),
                        dbc.Col(
                            [
                                dcc.DatePickerRange(
                                    id="data_quality_date_picker",
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
                            id="data_quality",
                        ),
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
)


@callback(
    Output("data_quality", "figure"),
    Input("data_quality_date_picker", "start_date"),
    Input("data_quality_date_picker", "end_date"),
)
def update_daily_trips_counts(start_date, end_date):
    dff = daily_pct_reporting.loc[
        :,
        (daily_pct_reporting.columns >= start_date)
        & (daily_pct_reporting.columns <= end_date),
    ]
    return px.imshow(
        dff,
        labels={
            "x": "Date",
            "y": "Route",
            "color": "% of Trips",
        },
        x=dff.columns,
        y=dff.index,
        # text_auto=".0%",
        color_continuous_scale=continous_color_scale,
        template=template,
    )
