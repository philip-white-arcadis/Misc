from dash import Dash, html
import dash_bootstrap_components as dbc
import dash

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SANDSTONE])


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("About", href="/")),
        dbc.NavItem(dbc.NavLink("Frequency", href="/frequency")),
        dbc.NavItem(dbc.NavLink("Ridership", href="/ridership")),
    ],
    brand=[
        html.A(
            html.Img(
                src="https://media.arcadis.com/-/media/themes/arcadiscom/com/com-theme/images/arcadis-logo-white.svg?rev=14d8161f40b3413e92109f74cc132784",
                height="22px",
            )
        ),
    ],
    brand_href="/",
    color="#1E2D2F",
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
