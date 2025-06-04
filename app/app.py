import streamlit as st
from streamlit_folium import st_folium
from ui.map import generate_base_map, generate_choro_layer
from utils.loader import load_geodata
from ui.plots import generate_bairro_plot
from ui.dash import render_dashboard, render_pie_charts

st.set_page_config(layout="wide")

st.title("Visualizador Recife")

st.session_state.geodata = load_geodata()
if 'cod_bairro_selecionado' not in st.session_state:
    st.session_state.cod_bairro_selecionado = None

m = generate_base_map(
    st.session_state.geodata,
)

MAP_MODES = {
    'basic': {
        'title': 'Dados básicos',
        'data': {
            'residentes_2022': {
                'alias': 'População (2022)',
                'unit': None,
                'year': 2022,
                'description': 'População residente total em 2022'
            }
        }
    },
    'demographic': {
        'title': 'Dados demográficos',
        'data': {
            'idade_media_2022': {
                'alias': 'Idade Média (2022)',
                'unit': 'anos',
                'year': 2022,
                'description': 'Idade média da população residente em 2022'
            },
            'pct_menores_2022': {
                'alias': 'Menores (2022)',
                'unit': '%',
                'year': 2022,
                'group': 'age_group',
                'description': 'Proporção de indivíduos de 0 a 19 anos em 2022'
            },
            'pct_adultos_2022': {
                'alias': 'Adultos (2022)',
                'unit': '%',
                'year': 2022,
                'group': 'age_group',
                'description': 'Proporção de indivíduos de 20 a 59 anos em 2022'
            },
            'pct_idosos_2022': {
                'alias': 'Idosos (2022)',
                'unit': '%',
                'year': 2022,
                'group': 'age_group',
                'description': 'Proporção de indivíduos de 60 anos ou mais em 2022'
            },
            'pct_masc_2022': {
                'alias': 'Indivíduos masculinos (2022)',
                'unit': '%',
                'year': 2022,
                'binary': True,
                'description': 'Proporção de indivíduos do sexo masculino em 2022',
                'other_group': 'feminino',
                'other_description': 'Indivíduos femininos (2022)'
            },
            'pct_brancos_2022': {
                'alias': 'Brancos (2022)',
                'unit': '%',
                'year': 2022,
                'group': 'race_group',
                'description': 'Proporção de indivíduos que se identificam como brancos em 2022'
            },
            'pct_pardos_2022': {
                'alias': 'Pardos (2022)',
                'unit': '%',
                'year': 2022,
                'group': 'race_group',
                'description': 'Proporção de indivíduos que se identificam como pardos em 2022'
            },
            'pct_pretos_2022': {
                'alias': 'Pretos (2022)',
                'unit': '%',
                'year': 2022,
                'group': 'race_group',
                'description': 'Proporção de indivíduos que se identificam como pretos em 2022'
            },
            'pct_amarelos_2022': {
                'alias': 'Amarelos (2022)',
                'unit': '%',
                'year': 2022,
                'group': 'race_group',
                'description': 'Proporção de indivíduos que se identificam como amarelos em 2022'
            },
            'pct_indigenas_2022': {
                'alias': 'Indígenas (2022)',
                'unit': '%',
                'year': 2022,
                'group': 'race_group',
                'description': 'Proporção de indivíduos que se identificam como indígenas em 2022'
            }
        }
    },
    'income': {
        'title': 'Dados de renda e alfabetização',
        'data': {
            'renda_mensal_global_2010': {
                'alias': 'Renda mensal global (2010)',
                'unit': 'R$',
                'year': 2010,
                'description': 'Renda mensal global média dos domicílios em 2010'
            },
            'renda_per_capita_2010': {
                'alias': 'Renda mensal per capita (2010)',
                'unit': 'R$',
                'year': 2010,
                'description': 'Renda mensal per capita média dos domicílios em 2010'
            },
            'pct_domicilios_0a05sm_2010': {
                'alias': 'Domicílios com renda mensal até 0,5 SM per capita',
                'unit': '%',
                'year': 2010,
                'group': 'income_group',
                'description': 'Proporção de domicílios com renda mensal per capita até 0,5 salário mínimo em 2010'
            },
            'pct_domicilios_05a3sm_2010': {
                'alias': 'Domicílios com renda mensal entre 0,5 e 3 SM per capita (2010)',
                'unit': '%',
                'year': 2010,
                'group': 'income_group',
                'description': 'Proporção de domicílios com renda mensal per capita entre 0,5 e 3 salários mínimos em 2010'
            },
            'pct_domicilios_3a10sm_2010': {
                'alias': 'Domicílios com renda mensal 3+ SM per capita (2010)',
                'unit': '%',
                'year': 2010,
                'group': 'income_group',
                'description': 'Proporção de domicílios com renda mensal per capita maior que 3 salários mínimos em 2010'
            },
            'pct_alfabetizadas_2022': {
                'alias': 'População 15+ alfabetizada (2022)',
                'unit': '%',
                'year': 2022,
                'binary': True,
                'other_group': 'População 15+ não alfabetizada',
                'other_description': 'Proporção de indivíduos (15+ anos) não alfabetizados em 2022',
                'description': 'População 15+ alfabetizada (2022)'
            }
        }
    },
    'space': {
        'title': 'Dados espaciais',
        'data': {
            'area_km2': {
                'alias': 'Área',
                'unit': 'km²',
                'year': None,
                'description': 'Área total do bairro em km²'
            },
            'pct_construida_2013': {
                'alias': 'Área construída (2013)',
                'unit': '%',
                'year': 2013,
                'binary': True,
                'other_group': 'não construída',
                'other_description': 'Área não construída (2013)',
                'description': 'Proporção da área total do bairro que é construída em 2013'
            },
            'media_moradores_domicilios_ocupados_2022': {
                'alias': 'Média de moradores por domicílios ocupados (2022)',
                'unit': None,
                'year': 2022,
                'description': 'Média de moradores por domicílios ocupados em 2022'
            },
            'densidade_bruta_area': {
                'alias': 'Densidade bruta',
                'unit': 'hab/km²',
                'year': None,
                'description': None
            },
            'densidade_liquida_area': {
                'alias': 'Densidade líquida',
                'unit': 'hab/km² construído',
                'year': None,
                'description': None
            }
        }
    },
    'clusters': {
        'title': 'Clusters',
        'data': {
            'cluster_qualidade_vida': {
                'alias': 'Clusters de qualidade de vida',
                'features': [('income', 'renda_per_capita_2010'), ('income','pct_alfabetizadas_2022'), ('demographic', 'pct_idosos_2022')],
                'titles': ['Bairros nobres', 'Bairros de classe média (ou muito heterogêneos)', 'Bairros populares'],
                'description': 'Aproxima IDH, levando em conta variáveis de renda, educação e expectativa de vida.'
            },
            'cluster_renda': {
                'alias': 'Clusters de faixas de distribuição de renda',
                'features': [('income', 'pct_domicilios_0a05sm_2010'), ('income', 'pct_domicilios_05a3sm_2010'), ('income', 'pct_domicilios_3a10sm_2010')],
                'titles': ['Bairros de alta renda', 'Bairros de renda média', 'Bairros de baixa renda'],
                'description': 'Agrupa os bairros de acordo com a distribuição de renda, considerando a proporção de domicílios em diferentes faixas de renda.'
            },
            'cluster_idades': {
                'alias': 'Clusters de faixas etárias',
                'features': [('demographic', 'pct_menores_2022'), ('demographic', 'pct_adultos_2022'), ('demographic', 'pct_idosos_2022')],
                'titles': ['Bairros com população idosa', 'Bairros com população adulta', 'Bairros com população jovem'],
                'description': 'Agrupa os bairros de acordo com a distribuição etária, considerando a proporção de indivíduos em diferentes faixas etárias.'
            },
            'cluster_corraca': {
                'alias': 'Clusters de cor/raça',
                'features': [('demographic', 'pct_brancos_2022'), ('demographic', 'pct_pardos_2022'), ('demographic', 'pct_pretos_2022'), ('demographic', 'pct_amarelos_2022'), ('demographic', 'pct_indigenas_2022')],
                'titles': ['Bairros de maioria branca', 'Bairros com presença de pessoas indígenas', 'Bairros de maioria negra', 'Bairros de maioria negra (e maiores índices de pessoas pretas)'],
                'description': 'Agrupa os bairros de acordo com a distribuição de cor/raça, considerando a proporção de indivíduos que se identificam como brancos, pardos, pretos, amarelos e indígenas.'
            }
        }
    }
}

# Seleção da categoria
category = st.selectbox(
    "Escolha o tipo de dado:",
    list(MAP_MODES.keys()),
    format_func=lambda k: MAP_MODES[k]["title"]
)

# Acessa os dados e metadados da categoria
selected_data = MAP_MODES[category]["data"]

# Cria uma lista de (coluna, alias) para o selectbox
column_options = [(col, meta["alias"]) for col, meta in selected_data.items()]

# Selectbox mostra os aliases, mas retorna a coluna
selected_column = st.selectbox(
    "Escolha o indicador para destacar no mapa:",
    options=column_options,
    format_func=lambda x: x[1]
)[0]  # extrai apenas o nome da coluna (a chave)

selected_alias = selected_data[selected_column]["alias"]

upper_left, upper_right = st.columns([2, 1])

with upper_left:
    # Generate updated layer and add to fresh group
    geojson, colormap = generate_choro_layer(
        st.session_state.geodata,
        column=selected_column,
        alias=selected_alias,
        unit=selected_data[selected_column].get('unit', None),
    )

    geojson.add_to(m)
    colormap.add_to(m)

    st_data = st_folium(m, height=500, use_container_width=True, returned_objects=['last_active_drawing'])

with upper_right:

    if category != 'clusters':
    # Renderiza o dashboard com os dados selecionados:
        render_dashboard(
            geodata=st.session_state.geodata,
            cod_bairro=st.session_state.cod_bairro_selecionado,
            map_modes=MAP_MODES,
            categoria=category
        )
    else:
        st.write(selected_data[selected_column]['description'])
        clusters = sorted(st.session_state.geodata[selected_column].unique())
        titles = selected_data[selected_column].get('titles', [])
        features = selected_data[selected_column].get('features', [])

        # Prepare column headers (aliases)
        col_aliases = [MAP_MODES[cat]['data'][col]['alias'] for cat, col in features]

        # Build table: rows = clusters (titles), columns = features (aliases)
        table_rows = []
        for cluster, title in zip(clusters, titles):
            row = {"Cluster": title}
            cluster_data = st.session_state.geodata[st.session_state.geodata[selected_column] == cluster]
            for (cat, col), alias in zip(features, col_aliases):
                mean_value = cluster_data[col].mean()
                # .replace(",", "X").replace(".", ",").replace("X", ".")
                row[alias] = mean_value
            table_rows.append(row)

        st.table(table_rows)
                # st.write(f"{MAP_MODES[cat]['data'][col]['alias']}: {st.session_state.geodata.query(f'{selected_column} == {cluster}')[col].mean()}")
            
            # st.write(f"### {selected_data[selected_column]['titles'][cluster]}")

# st.write(f"# Indicador Selecionado: {selected_alias}")


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

proportions, comparisons = st.tabs(['Proporções (dentro do bairro)', 'Comparações (entre bairros)'])


with proportions:
    render_pie_charts(
        geodata=st.session_state.geodata,
        cod_bairro=st.session_state.cod_bairro_selecionado,
        map_modes=MAP_MODES,
        categoria=category
    )

with comparisons:
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
        (column, meta["alias"]) for column, meta in selected_data.items()
        if column != selected_column
    ]
    # remaining_columns = [
    #     (column, alias) for column, alias in zip(MAP_MODES[category]['data'], MAP_MODES[category]['aliases'])
    #     if column != selected_column
    # ]

    # Create a two-wide grid for the remaining plots
    num_remaining = len(remaining_columns)
    rows = (num_remaining + 1) // 2  # Calculate the number of rows needed

    # st.write(f"## Gráficos restantes ({num_remaining}):")

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