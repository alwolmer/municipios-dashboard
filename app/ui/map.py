import geopandas as gpd
import pandas as pd
import folium
import branca.colormap as cm
import functools
import pandas as pd
import folium
import numpy as np
import streamlit as st

def calculate_map_center(geodf):
  reprojected = geodf.to_crs(epsg=4326)
  map_center = [reprojected.geometry.centroid.y.mean(), reprojected.geometry.centroid.x.mean()]
  return map_center

def calculate_outer_bounds(geodf):
  bounds = geodf.total_bounds

  # Calculate the distance between edges
  lon_distance = bounds[2] - bounds[0]
  lat_distance = bounds[3] - bounds[1]

  # Calculate margin increase
  lon_margin = lon_distance * 0.5
  lat_margin = lat_distance * 0.3

  # Apply margin increase to outer bounds
  expanded_bounds = [
      bounds[0] - lon_margin,  # Min Longitude - Margin
      bounds[1] - lat_margin,  # Min Latitude - Margin
      bounds[2] + lon_margin,  # Max Longitude + Margin
      bounds[3] + lat_margin   # Max Latitude + Margin
  ]

  return expanded_bounds

def generate_colormap(series, discrete=False):
    if discrete:
        # Define five colors for the five percentiles
        colors = ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']
        # Calculate percentiles
        percentiles = np.quantile(series, [0, 0.2, 0.4, 0.6, 0.8, 1])
        # Create a discrete colormap using branca.colormap.StepColormap
        colormap = cm.StepColormap(
            colors,
            index=percentiles,  # Set the percentiles as index
            vmin=series.min(),  # Set minimum value for colormap
            vmax=series.max()   # Set maximum value for colormap
        )
    else:
        min_value = series.min()
        max_value = series.max()
        colormap = cm.linear.YlOrRd_09.scale(min_value, max_value)

    return colormap


def style_function(feature, colormap, column, discrete=False):
    """Style function for choropleth map."""
    value = feature['properties'][column]
    if discrete:
        # For discrete colormaps, directly get color from colormap
        color = colormap(value)
        return {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.9
        }
    else:
        # For continuous colormaps, apply colormap to value
        return {
            'fillColor': colormap(value),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.9
        }


def highlight_function(feature):
    return {
        'weight': 3,
        'color': 'black',
        'fillOpacity': 1
    }


def generate_choro_layer(geodf, column, name=None, alias=None, discrete=False):
    colormap = generate_colormap(geodf[column], discrete)

    if name is None:
        name = column

    if alias is None:
        alias = column

    styled_style_function = functools.partial(style_function, colormap=colormap, column=column, discrete=discrete)

    tooltip = folium.GeoJsonTooltip(
        fields=['nome_bairro', column],
        aliases=['Bairro', alias]
    )

    popup = folium.GeoJsonPopup(
        fields=['nome_bairro', column],
        aliases=['Bairro', alias]
    )

    layer = folium.GeoJson(
        geodf,
        name=name,
        style_function=styled_style_function,
        highlight_function=highlight_function,
        tooltip=tooltip,
        popup=popup,
        # show=False,
        show=True,
        control=True,
        max_zoom=16,
        min_zoom=10
    )

    
    # add legend to the map
    # colormap.caption = alias
    # colormap.add_to(layer)

    return layer, colormap

    # layer = folium.GeoJson(
    #     geodf,
    #     name=name,
    #     style_function=styled_style_function,
    #     highlight_function=highlight_function,
    #     tooltip=folium.features.GeoJsonTooltip(
    #         fields=['nome_bairro', column],
    #         aliases=['Bairro', alias]
    #     ),
    #     show=False,
    #     # overlay=False,
    #     control=True,
    #     max_zoom=16,
    #     min_zoom=10
    # )


# def generate_choro_layer(geodf, column, name=None, alias=None, discrete=False):
#     colormap = generate_colormap(geodf[column], discrete)

#     if name is None:
#         name = column

#     if alias is None:
#         alias = column

#     styled_style_function = functools.partial(style_function, colormap=colormap, column=column, discrete=discrete)

#     # Create a FeatureGroup with a name (important!)
#     fg = folium.FeatureGroup(name=name, show=False)

#     geojson = folium.GeoJson(
#         geodf,
#         style_function=styled_style_function,
#         highlight_function=highlight_function,
#         tooltip=folium.features.GeoJsonTooltip(
#             fields=['nome_bairro', column],
#             aliases=['Bairro', alias]
#         )
#     )

#     geojson.add_to(fg)
#     fg.layer_name = name  # important for LayerControl
#     return fg

# @st.cache_resource
def generate_base_map(_geodata):
    map_center = calculate_map_center(_geodata)
    outer_bounds = calculate_outer_bounds(_geodata)

    m = folium.Map(
        location=map_center,
        max_bounds=True,
        min_lat=outer_bounds[1],
        max_lat=outer_bounds[3],
        min_lon=outer_bounds[0],
        max_lon=outer_bounds[2],
        control_scale=True,
        zoom_start=10, 
        tiles=None
    )

    folium.TileLayer(
        tiles='http://localhost:4472/{z}/{x}/{y}.png',
        attr='Offline OSM',
        name='Offline Tiles',
        max_zoom=15,
        min_zoom=12,
        overlay=False,
        control=False
    ).add_to(m)

    return m