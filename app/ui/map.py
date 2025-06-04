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

def generate_colormap(series, alias=None, discrete=False):
    
    min_value = series.min()
    max_value = series.max()

    if discrete:
        # Define five colors for the five percentiles
        colors = ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']
        # Calculate percentiles
        percentiles = np.quantile(series, [0, 0.2, 0.4, 0.6, 0.8, 1])
        # Create a discrete colormap using branca.colormap.StepColormap
        colormap = cm.StepColormap(
            colors,
            index=percentiles,  # Set the percentiles as index
            vmin=min_value,  # Set minimum value for colormap
            vmax=max_value   # Set maximum value for colormap
        )
    else:
        colormap = cm.linear.YlOrRd_09.scale(min_value, max_value)

    caption = alias if alias else series.name
    colormap.caption = caption

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

def scale_features(geodf, column):
    """Scale features in the GeoDataFrame based on a specified column."""
    scaled = geodf[column].copy()

    max_value = scaled.max()

    oom = 0  # Order of magnitude
    if abs(max_value) > 1e6:
        scaled = scaled / 1e6
        oom = 6
    elif abs(max_value) > 1e3:
        scaled = scaled / 1e3
        oom = 3
    
    scaled = pd.Series(np.round(scaled, 2).astype(float))

    return scaled, oom

def generate_choro_layer(geodf, column, name=None, alias=None, unit=None, discrete=False):


    column_scaled = f'{column}_scaled'
    temp_geodf = geodf.copy()

    scaled, oom = scale_features(geodf, column)

    temp_geodf[column_scaled] = scaled

    colormap = generate_colormap(scaled, alias=alias, discrete=discrete)

    oom_str = "milhões" if oom == 6 else "milhares" if oom == 3 else ""

    colormap.caption = f"{alias} (em {oom_str} de {unit})" if unit and oom_str else f"{alias} (em {unit})" if unit else  f"{alias} (em {oom_str})" if oom_str else alias

    if name is None:
        name = column

    if alias is None:
        alias = column

    styled_style_function = functools.partial(style_function, colormap=colormap, column=column_scaled, discrete=discrete)

    # Format the column values according to Portuguese convention
    def format_pt_br(val):
        if isinstance(val, int):
            try:
                return f"{val:,}".replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                return val
        elif isinstance(val, float):
            try:
                return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                return val
    

    formatted_col = f"{column}_ptbr"
    temp_geodf[formatted_col] = temp_geodf[column].apply(format_pt_br)
    tooltip_fields = ['nome_bairro', formatted_col]
    popup_fields = ['nome_bairro', formatted_col]
    tooltip_aliases = ['Bairro', alias + (f" ({unit})" if unit else "")]
    popup_aliases = ['Bairro', alias + (f" ({unit})" if unit else "")]

    tooltip = folium.GeoJsonTooltip(
        fields=tooltip_fields,
        aliases=tooltip_aliases
    )

    popup = folium.GeoJsonPopup(
        fields=popup_fields,
        aliases=popup_aliases
    )

    layer = folium.GeoJson(
        temp_geodf,
        name=name,
        style_function=styled_style_function,
        highlight_function=highlight_function,
        tooltip=tooltip,
        popup=popup,
        show=True,
        control=True,
        max_zoom=16,
        min_zoom=10
    )

    return layer, colormap

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
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='OpenStreetMap',
        name='OpenStreetMap',
        max_zoom=15,
        min_zoom=11,
        overlay=False,
        control=False
    ).add_to(m)

    # folium.TileLayer(
    #     tiles='http://localhost:4472/{z}/{x}/{y}.png',
    #     attr='Offline OSM',
    #     name='Offline Tiles',
    #     max_zoom=15,
    #     min_zoom=12,
    #     overlay=False,
    #     control=False
    # ).add_to(m)

    return m