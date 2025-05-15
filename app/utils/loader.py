import geopandas as gpd
import pandas as pd
import streamlit as st
import os
from shapely.geometry import Polygon

@st.cache_data
def load_geodata():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
    print(os.listdir(data_dir))
    geodata = gpd.read_file(os.path.join(data_dir, "bairros_clustered.geojson"))
    return geodata