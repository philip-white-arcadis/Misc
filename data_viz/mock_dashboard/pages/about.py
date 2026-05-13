import dash
from dash import html
import pandas as pd

dash.register_page(__name__, path="/", name="About")


layout = html.Div(
    [
        html.H1("About This Dashboard"),
        html.P(
            """This is a mock dashboard for promotional purposes. The dashboard was created using Dash."""
        ),
        html.H1("Data Sources"),
        html.Ul([html.Li("Source 1"), html.Li("Source 2")]),
    ],
    className="about-page-container",
)
