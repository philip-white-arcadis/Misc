from dash import html, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from datetime import timedelta
from data import min_date, max_date, daily_boardings, template, continous_color_scale

dash.register_page(__name__, path="/daily-ons", title="Daily Boardings")


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Total Daily Boardings by Route",
                        ),
                        dbc.Col(
                            [
                                dcc.DatePickerRange(
                                    id="daily_ons_date_picker",
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
                            id="daily_ons",
                        ),
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
)


@callback(
    Output("daily_ons", "figure"),
    Input("daily_ons_date_picker", "start_date"),
    Input("daily_ons_date_picker", "end_date"),
)
def update_daily_ons_counts(start_date, end_date):
    dff = daily_boardings.loc[
        :,
        (daily_boardings.columns >= start_date) & (daily_boardings.columns <= end_date),
    ]
    return px.imshow(
        dff,
        labels={"x": "Date", "y": "Route", "color": "Boardings"},
        x=dff.columns,
        y=dff.index,
        text_auto=True,
        color_continuous_scale=continous_color_scale,
        template=template,
    )
