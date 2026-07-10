from dash import html, dcc, callback, Output, Input
from pages import daily_boardings
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from data import route_names, monthly_boardings, template, continous_color_scale

dash.register_page(__name__, path="/monthly-ons", title="Monthly Boardings")

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Total Monthly Boardings by Route",
                        ),
                        dcc.Dropdown(
                            id="route_dropdown",
                            options=route_names,
                            value=route_names,
                            multi=True,
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
                            id="monthly_ons",
                        ),
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
)


@callback(Output("monthly_ons", "figure"), Input("route_dropdown", "value"))
def update_monthly_ons_counts(selected_routes):
    dff = monthly_boardings[monthly_boardings["route_name"].isin(selected_routes)]
    return px.line(
        dff,
        labels={
            "trip_month_name": "Month",
            "total_ons": "Total Boardings",
            "route_name": "Route",
        },
        x="trip_month_name",
        y="total_ons",
        color="route_name",
        template=template,
        markers=True,
    )
