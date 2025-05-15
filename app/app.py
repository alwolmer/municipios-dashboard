import streamlit as st
from streamlit_folium import st_folium
from ui.map import generate_base_map, generate_choro_layer
from utils.loader import load_geodata
from ui.plots import generate_bairro_plot

st.set_page_config(layout="wide")

st.title("Visualizador Recife")

st.session_state.geodata = load_geodata()
if 'cod_bairro_selecionado' not in st.session_state:
    st.session_state.cod_bairro_selecionado = None

m = generate_base_map(
    st.session_state.geodata,
)

# TODO: change the map mode dict to have each data entry contain a dict with the column name, alias, unit and year

MAP_MODES = {
    'basic': {
        'title': 'Dados básicos',
        'data': ['area_km2', 'residentes_2022'],
        'aliases': ['Área (km²)', 'População (2022)']
    },
    'demographic': {
        'title': 'Dados demográficos',
        'data': ['idade_media_2022', 'pct_menores_2022', 'pct_adultos_2022', 'pct_idosos_2022', 'pct_masc_2022'],
        'aliases': ['Idade Média (2022)', '% Menores (2022)', '% Adultos (2022)', '% Idosos (2022)', '% indivíduos masculinos (2022)']
    },
    'race': {
        'title': 'Dados raciais',
        'data': ['pct_brancos_2022', 'pct_pardos_2022', 'pct_pretos_2022', 'pct_amarelos_2022', 'pct_indigenas_2022'],
        'aliases': ['% Brancos (2022)', '% Pardos (2022)', '% Pretos (2022)', '% Amarelos (2022)', '% Indígenas (2022)']
    },
    'income': {
        'title': 'Dados de renda e alfabetização',
        'data': ['renda_mensal_global_2010', 'renda_per_capita_2010', 'pct_domicilios_0a05sm_2010', 'pct_domicilios_05a3sm_2010', 'pct_domicilios_3a10sm_2010', 'pct_alfabetizadas_2022'],
        'aliases': ['Renda mensal global (2010)', 'Renda mensal per capital (2010)', '% domicílios com renda mensal até 0,5 SM per capita', '% domicílios com renda mensal entre 0,5 e 3 SM per capita (2010)', '% domicílios com renda mensal > 3 SM per capita (2010)' , '% alfabetizados (2022)']
    },
    'space': {
        'title': 'Dados espaciais',
        'data': ['area_km2', 'pct_construida_2013', 'media_moradores_domicilios_ocupados_2022', 'densidade_bruta_area', 'densidade_liquida_area'],
        'aliases': ['Área (km²)', '% área construída (2013)', 'Média de moradores por domicílios ocupados (2022)', 'Densidade bruta (hab/km²)', 'Densidade líquida (hab/km² construído)']
    }
}

# "renda_per_capita_2010": 440.52, "renda_por_domicilio_2010":  "pct_domicilios_0a05sm_2010": 47.26, "pct_domicilios_05a3sm_2010": 49.22, "pct_domicilios_3a10sm_2010": 3.52

left, right = st.columns(2)

with left:
    category = st.selectbox("Escolha o tipo de dado:", list(MAP_MODES.keys()), format_func=lambda k: MAP_MODES[k]["title"])

    columns = MAP_MODES[category]["data"]
    aliases = MAP_MODES[category]["aliases"]

    var_idx = st.selectbox("Escolha o indicador:", range(len(columns)), format_func=lambda i: aliases[i])

    selected_column = columns[var_idx]
    selected_alias = aliases[var_idx]

with right:
    if st.session_state.cod_bairro_selecionado is not None:
        try:
            nome = st.session_state.geodata.query(
                f'cod_bairro_ibge == {st.session_state.cod_bairro_selecionado}'
            )['nome_bairro'].values[0]
            st.write(f"# Bairro selecionado: {nome}")
            for column, alias in zip(columns, aliases):
                value = st.session_state.geodata.query(
                    f'cod_bairro_ibge == {st.session_state.cod_bairro_selecionado}'
                )[column].values[0]
                st.write(f"{alias}: {value}")
        except IndexError:
            st.warning("Código de bairro inválido ou não encontrado.")
    else:
        st.write("# Nenhum bairro selecionado.")

    # if st.session_state.cod_bairro_selecionado is None:
    #     st.write("# Nenhum bairro selecionado.")
    # else:
    #     st.write(f"# Bairro selecionado: {st.session_state.geodata.query(f'cod_bairro_ibge == {st.session_state.cod_bairro_selecionado}')['nome_bairro'].values[0]}")

# dynamic_fg = folium.FeatureGroup(name="Layer", show=True)

# Generate updated layer and add to fresh group
geojson, colormap = generate_choro_layer(
    st.session_state.geodata,
    column=selected_column,
    alias=selected_alias
)

geojson.add_to(m)
colormap.add_to(m)
colormap.caption = selected_alias
# dynamic_fg.add_to(m)

st.write(f"# Indicador Selecionado: {selected_alias}")

st_data = st_folium(m, height=500, use_container_width=True, returned_objects=['last_active_drawing'])

# if st_data is not None and st_data.get('last_active_drawing') is not None:
#     cod_bairro = st_data['last_active_drawing']['properties'].get('cod_bairro_ibge')
#     if cod_bairro is not None:
#         # st.write("Selected Bairro Code:", cod_bairro)
#         st.session_state.cod_bairro_selecionado = cod_bairro
#         st.rerun()
# After st_folium()
if st_data is not None and st_data.get('last_active_drawing') is not None:
    cod_bairro = st_data['last_active_drawing']['properties'].get('cod_bairro_ibge')
    
    # Only trigger rerun if selection changed
    if cod_bairro is not None and cod_bairro != st.session_state.cod_bairro_selecionado:
        st.session_state.cod_bairro_selecionado = cod_bairro
        st.rerun()
    else:
        # st.write("No Bairro Code found in the last active drawing.")
        pass

# st.write(st.session_state.cod_bairro_selecionado)

st.write("# Gráficos")
if st.session_state.cod_bairro_selecionado is not None:
    st.write(f"## Destacado: {st.session_state.geodata.query(f'cod_bairro_ibge == {st.session_state.cod_bairro_selecionado}')['nome_bairro'].values[0]}")

# Plot the selected column first
st.plotly_chart(
    generate_bairro_plot(
        st.session_state.geodata,
        column_to_plot=selected_column,
        alias=selected_alias,
        highlight_bairro=st.session_state.cod_bairro_selecionado
    ),
)

# Prepare the remaining columns for plotting
remaining_columns = [
    (column, alias) for column, alias in zip(MAP_MODES[category]['data'], MAP_MODES[category]['aliases'])
    if column != selected_column
]

# Create a two-wide grid for the remaining plots
num_remaining = len(remaining_columns)
rows = (num_remaining + 1) // 2  # Calculate the number of rows needed

for i in range(rows):
    cols = st.columns(2)
    for j in range(2):
        idx = i * 2 + j
        if idx < num_remaining:
            column, alias = remaining_columns[idx]
            with cols[j]:
                st.plotly_chart(
                    generate_bairro_plot(
                        st.session_state.geodata,
                        column_to_plot=column,
                        alias=alias,
                        highlight_bairro=st.session_state.cod_bairro_selecionado
                    ),
                )
        elif num_remaining % 2 != 0 and i == rows - 1:  # Center the last plot if odd number
            with cols[0]:
                st.empty()  # Leave the second column empty