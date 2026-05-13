from dash import html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash
import dash_leaflet as dl
import geopandas as gpd
from shapely.geometry import Point
from data import (
    MIN_DATE,
    MAX_DATE,
    apc_table,
    stops_table,
    route_ids,
    DIRECTIONS,
    ROUTE_VARIANTS,
)

dash.register_page(__name__, path="/ridership", name="Ridership")

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Daily Boardings by Route",
                        ),
                        dcc.DatePickerRange(
                            id="freq_heatmap_date_picker",
                            min_date_allowed=MIN_DATE,
                            max_date_allowed=MAX_DATE,
                            start_date=MIN_DATE,
                            end_date=MAX_DATE,
                        ),
                    ],
                    width=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="boardings_heatmap",
                        ),
                    ],
                    width=12,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Daily Boardings and Alightings by Stop",
                        ),
                    ],
                    width=8,
                ),
                dbc.Col(
                    [
                        html.H1("Daily Boardgins and Alightings Map"),
                    ],
                    width=4,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            route_ids,
                            placeholder="Route",
                            id="freq_bar_route_select",
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.RadioItems(
                            options=["IB", "OB"],
                            id="direction_radio",
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="route_variant_select",
                            placeholder="Variant",
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.DatePickerSingle(
                            id="freq_bar_date_picker",
                            min_date_allowed=MIN_DATE,
                            max_date_allowed=MAX_DATE,
                        ),
                    ],
                    width=3,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Store(id="stops_map_storage", storage_type="memory"),
                        dcc.Graph(
                            # inline style used to avoid bug described here:
                            # https://github.com/plotly/dash/issues/1263
                            id="boardings_route_stop_bar",
                            style={"height": "600px"},
                        ),
                    ],
                    width=8,
                ),
                dbc.Col(
                    [
                        # dl.Map(
                        #     dl.TileLayer(
                        #         url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                        #         attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
                        #     ),
                        #     center=[42.27078779786199, -71.13680852901824],
                        #     zoom=12,
                        #     style={"height": "600px"},
                        #     id="stops_map",
                        # ),
                        dcc.Graph(id="stops_map", style={"height": "600px"}),
                    ],
                    width=4,
                ),
            ],
        ),
    ],
    fluid=True,
)


@callback(
    Output("boardings_heatmap", "figure"),
    Input("freq_heatmap_date_picker", "start_date"),
    Input("freq_heatmap_date_picker", "end_date"),
)
def update_boardings_heatmap(start_date, end_date):
    df_grouped = (
        apc_table.groupby(["trip_date", "route"])
        .agg(total_boardings=pd.NamedAgg("psgr_on", "sum"))
        .reset_index()
    )
    dff = df_grouped.loc[
        (df_grouped["trip_date"] >= start_date) & (df_grouped["trip_date"] <= end_date)
    ]
    dff["route"] = dff["route"].astype(str)
    pivot = dff.pivot(index="route", columns="trip_date", values="total_boardings")
    return px.imshow(
        pivot,
        labels={"x": "Date", "y": "Route", "color": "Number of Boardings"},
        x=pivot.columns,
        y=pivot.index,
        text_auto=True,
        color_continuous_scale="BuPu",
        template="simple_white",
    )


@callback(
    Output("route_variant_select", "options"),
    Input("freq_bar_route_select", "value"),
    Input("direction_radio", "value"),
)
def update_variants_dropdown(selected_route, selected_direction):
    direction = int(DIRECTIONS[selected_direction])
    return [{"label": i, "value": i} for i in ROUTE_VARIANTS[selected_route][direction]]


@callback(
    Output("stops_map_storage", "data"),
    Input("freq_bar_route_select", "value"),
    Input("freq_bar_date_picker", "date"),
    Input("direction_radio", "value"),
    Input("route_variant_select", "value"),
)
def update_stops_map_storage(
    selected_route, selected_date, selected_direction, selected_variant
):
    if (
        selected_route is None
        or selected_date is None
        or selected_direction is None
        or selected_variant is None
    ):
        pass
    else:
        apc_stop_info = apc_table.merge(
            stops_table[["stop_id", "stop_name"]], how="left", on="stop_id"
        )
        grouping = [
            "trip_date",
            "route",
            "direction",
            "variant",
            "stop_name",
            "stop_seq_id",
        ]
        df_grouped = (
            apc_stop_info.groupby(grouping)
            .agg(
                Boardings=pd.NamedAgg("psgr_on", "sum"),
                Alightings=pd.NamedAgg("psgr_off", "sum"),
            )
            .reset_index()
        )
        dff = df_grouped.loc[
            (df_grouped["route"] == int(selected_route))
            & (df_grouped["trip_date"] == selected_date)
            & (df_grouped["direction"] == int(DIRECTIONS[selected_direction]))
            & (df_grouped["variant"] == int(selected_variant))
        ]
        pivot = dff.melt(
            id_vars=grouping,
            value_vars=["Boardings", "Alightings"],
            var_name="type",
            value_name="passengers",
        )
        pivot = pivot.sort_values("stop_seq_id")
        stops = (
            pivot.groupby("stop_name")
            .agg(total_passengers=pd.NamedAgg("passengers", "sum"))
            .reset_index()
        )
        stops = stops.merge(stops_table, how="left", on="stop_name").drop_duplicates(
            "stop_name"
        )
        stops_dict = stops.to_dict("records")
        return stops_dict


@callback(
    Output("boardings_route_stop_bar", "figure"),
    State("freq_bar_route_select", "value"),
    Input("freq_bar_date_picker", "date"),
    Input("direction_radio", "value"),
    Input("route_variant_select", "value"),
)
def update_boardings_route_stop_bar(
    selected_route, selected_date, selected_direction, selected_variant
):
    if (
        selected_route is None
        or selected_date is None
        or selected_direction is None
        or selected_variant is None
    ):
        pass
    else:
        apc_stop_info = apc_table.merge(
            stops_table[["stop_id", "stop_name"]], how="left", on="stop_id"
        )
        grouping = [
            "trip_date",
            "route",
            "direction",
            "variant",
            "stop_name",
            "stop_seq_id",
        ]
        df_grouped = (
            apc_stop_info.groupby(grouping)
            .agg(
                Boardings=pd.NamedAgg("psgr_on", "sum"),
                Alightings=pd.NamedAgg("psgr_off", "sum"),
            )
            .reset_index()
        )
        dff = df_grouped.loc[
            (df_grouped["route"] == int(selected_route))
            & (df_grouped["trip_date"] == selected_date)
            & (df_grouped["direction"] == int(DIRECTIONS[selected_direction]))
            & (df_grouped["variant"] == int(selected_variant))
        ]
        pivot = dff.melt(
            id_vars=grouping,
            value_vars=["Boardings", "Alightings"],
            var_name="type",
            value_name="passengers",
        )
        pivot = pivot.sort_values("stop_seq_id")
        return px.bar(
            pivot,
            x="stop_name",
            y="passengers",
            color="type",
            barmode="group",
            category_orders={"stop_name": pivot["stop_name"].unique()},
            template="simple_white",
            color_discrete_sequence=px.colors.qualitative.Prism,
            labels={
                "stop_name": "Stop",
                "passengers": "Passengers",
            },
        )


# @callback(Output("stops_map", "children"), Input("stops_map_storage", "data"))
@callback(Output("stops_map", "figure"), Input("stops_map_storage", "data"))
def update_stops_map(stops):
    if stops:
        df = pd.DataFrame(stops)
        return px.scatter_map(
            df,
            lat="lat",
            lon="lon",
            hover_data=["stop_name", "total_passengers"],
            size="total_passengers",
            # height=600,
            map_style="carto-positron",
            zoom=12,
        )
        # df["geometry"] = df.apply(lambda row: Point(row["lon"], row["lat"]), axis=1)
        # gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        # geojson = gdf.to_json()
        # return dl.GeoJSON(data=geojson)
    else:
        pass
