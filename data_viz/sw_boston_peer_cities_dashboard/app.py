from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import geopandas as gpd

app = Dash(__name__)
server = app.server

gdf = gpd.read_parquet("./combined.parquet")
gdf = gdf.loc[gdf["total_pop"] > 100]
gdf = gdf.replace(-666666666.0, 0)

cities_list = list(gdf.peer.unique())

vars = {
    "% Non-White": "pct_non_white",
    "% 0-Car Households": "pct_0_car_hh",
    "% Commute by Transit": "pct_commute_transit",
    "Median Household Income": "median_hh_income",
    "Median Age": "median_age",
    "Population Density": "people_per_acre",
}
var_options = list(vars.keys())

zoom_levels = {
    "Baltimore": 9,
    "Boston": 10,
    "Chicago": 8,
    "Denver": 10,
    "Los Angeles": 8,
    "Minneapolis": 9,
    "Philadelphia": 10,
    "Portland": 9,
    "Salt Lake City": 9,
    "San Fransisco": 11,
    "Seattle": 8,
    "SW Boston": 10,
    "Washington DC": 10,
}

app.layout = html.Div(
    [
        dcc.Dropdown(
            cities_list,
            cities_list[0],
            id="cities_dropdown",
            style={"width": 255, "margin": "0.4em"},
        ),
        dcc.RadioItems(
            id="variable_radio",
            options=var_options,
            value=var_options[0],
            inline=True,
            style={"margin": "0.4em"},
        ),
        dcc.Graph(
            id="graph", style={"margin": "0.4em", "border": "solid 1px lightgray"}
        ),
        dcc.Graph(
            id="graph2", style={"margin": "0.4em", "border": "solid 1px lightgray"}
        ),
    ]
)


@app.callback(
    Output("graph", "figure"),
    Input("variable_radio", "value"),
    Input("cities_dropdown", "value"),
)
def display_choropleth1(selected_variable, selected_city):
    gdf_filtered = gdf.loc[gdf["peer"] == "SW Boston"]
    min = gdf.loc[gdf["peer"].isin([selected_city, "SW Boston"])][
        vars[selected_variable]
    ].min()
    max = gdf.loc[gdf["peer"].isin([selected_city, "SW Boston"])][
        vars[selected_variable]
    ].max()
    centroid = gdf_filtered["geometry"].union_all().centroid
    fig = px.choropleth_map(
        gdf_filtered,
        geojson=gdf_filtered.geometry,
        color=vars[selected_variable],
        locations=gdf_filtered.index,
        map_style="carto-positron",
        center={"lat": centroid.y, "lon": centroid.x},
        zoom=11,
        range_color=[min, max],
        hover_data=[
            var + "_f" if var != "median_age" else var for var in vars.values()
        ],
        opacity=0.7,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@app.callback(
    Output("graph2", "figure"),
    Input("cities_dropdown", "value"),
    Input("variable_radio", "value"),
)
def display_choropleth2(selected_city, selected_variable):
    gdf_filtered = gdf.loc[gdf["peer"] == selected_city]
    min = gdf.loc[gdf["peer"].isin([selected_city, "SW Boston"])][
        vars[selected_variable]
    ].min()
    max = gdf.loc[gdf["peer"].isin([selected_city, "SW Boston"])][
        vars[selected_variable]
    ].max()
    centroid = gdf_filtered["geometry"].union_all().centroid
    fig = px.choropleth_map(
        gdf_filtered,
        geojson=gdf_filtered.geometry,
        locations=gdf_filtered.index,
        color=vars[selected_variable],
        map_style="carto-positron",
        center={"lat": centroid.y, "lon": centroid.x},
        zoom=zoom_levels[selected_city],
        range_color=[min, max],
        hover_data=[
            var + "_f" if var != "median_age" else var for var in vars.values()
        ],
        opacity=0.7,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
