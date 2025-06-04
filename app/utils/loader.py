import geopandas as gpd
import pandas as pd
import streamlit as st
import os
from shapely.geometry import Polygon
from config import LOAD_LOCAL, REMOTE_REPO_URL

@st.cache_data
def load_geodata():

    if LOAD_LOCAL:
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
        geodata = gpd.read_file(os.path.join(data_dir, "bairros_clustered.geojson"))
    else: # Load from the remote repo
        geodata_url = REMOTE_REPO_URL
        geodata = gpd.read_file(geodata_url)

    return geodata