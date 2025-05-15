import geopandas as gpd
import pandas as pd
import streamlit as st
import plotly.express as px

def generate_bairro_plot(geodata, column_to_plot, alias, highlight_bairro):

    # Sort geodata by 'area_km2' in descending order
    sorted_geodata = geodata.sort_values(column_to_plot, ascending=False)

    # Create a color column to highlight the selected bairro
    sorted_geodata['color'] = sorted_geodata['cod_bairro_ibge'].apply(
        lambda x: '#FF5733' if x == highlight_bairro else '#3498DB'
    )

    # Create the bar chart using Plotly
    fig = px.bar(
        sorted_geodata,
        x='nome_bairro',
        y=column_to_plot,
        color='color',
        color_discrete_map='identity',
        title=f"{alias} por bairro",
        labels={'nome_bairro': 'Bairro', column_to_plot: alias},
        # log_y=True,
    )

    # Update layout for better visualization
    fig.update_layout(
        xaxis_title="Bairro",
        yaxis_title=alias,
        showlegend=False,
        xaxis=dict(tickangle=45, categoryorder='array', categoryarray=sorted_geodata['nome_bairro']),
    )

    return fig
