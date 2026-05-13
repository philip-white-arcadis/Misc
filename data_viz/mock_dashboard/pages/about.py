import dash
from dash import html
import pandas as pd

dash.register_page(__name__, path="/", name="About")


layout = html.Div(
    [
        html.H1("About This Dashboard"),
        html.P("Blah blah blah..."),
        html.H1("Data Sources"),
        html.Ul([html.Li("Source1"), html.Li("Source2")]),
    ],
    className="about-page-container",
)
