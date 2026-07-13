from dash import Dash, html
import dash_bootstrap_components as dbc
import dash

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SANDSTONE])


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Data Quality", href="/")),
        dbc.NavItem(dbc.NavLink("Trip Counts", href="/trip-counts")),
        dbc.NavItem(dbc.NavLink("Daily Boardings", href="/daily-ons")),
        dbc.NavItem(dbc.NavLink("Monthly Boardings", href="/monthly-ons")),
    ],
    brand=[
        html.A(
            html.Img(
                src="./assets/cropped-SRTA-Banner.png",
                height="48px",
            )
        ),
    ],
    brand_href="/",
    color="#010066",
    dark=True,
    links_left=True,
    class_name="nav",
)

app.layout = dbc.Container(
    [
        dbc.Row([dbc.Col([html.Div([navbar])])]),
        dbc.Row([dbc.Col([html.Div([dash.page_container])])]),
    ],
)


if __name__ == "__main__":
    app.run(debug=True)
