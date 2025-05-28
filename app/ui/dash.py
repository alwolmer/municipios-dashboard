import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import plotly.express as px

def render_dashboard(geodata, cod_bairro, map_modes, categoria):
    if cod_bairro is None:
        st.write("# Nenhum bairro selecionado.")
        st.write("Por favor, selecione um bairro no mapa.")
        return

    selected_data = map_modes[categoria]['data']
    bairro_data = geodata.query(f"cod_bairro_ibge == {cod_bairro}").iloc[0]

    nome = bairro_data['nome_bairro']
    st.write(f"# Bairro selecionado: {nome}")

    total_rows = len(geodata)

    table = []

    # Mostrar os valores com alias + unidade
    for col, meta in selected_data.items():
        
        alias = meta['alias']
        value = bairro_data[col]
        rank = (geodata[col].rank(ascending=False, method='min')[bairro_data.name]).astype(int)
        group = meta.get('group', 'N/A')
        unit = meta.get('unit') or ''

        if unit == 'R$':
            # statement = f"{alias}: R$ {value:,.2f} ({rank}/{total_rows}) ({group})".replace(",", "X").replace(".", ",").replace("X", ".")
            value_str = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            # statement = f"{alias}: {value} {unit} ({rank}/{total_rows}) ({group})"
            value_str = f"{value:,} {unit}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # st.write(statement)

        row = {
            'Variável': alias,
            'Valor': value_str,
            'Ranking': rank,
            'Grupo': meta.get('group', 'N/A'),
        }
        table.append(row)

    # Configuração da tabela
    gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(table))
    grid_options = gb.build()
    grid_options['defaultColDef'] = {
        'sortable': True,
        'filter': True,
        'resizable': True,
        'wrapText': True,
        'autoHeight': True,
    }
    grid_response = AgGrid(
        pd.DataFrame(table),
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        theme='streamlit',
        fit_columns_on_grid_load=True,
    )

def render_pie_charts(geodata, cod_bairro, map_modes, categoria):
    if cod_bairro is None:
        st.write("# Nenhum bairro selecionado.")
        st.write("Por favor, selecione um bairro no mapa.")
        return

    selected_data = map_modes[categoria]['data']
    bairro_data = geodata.query(f"cod_bairro_ibge == {cod_bairro}").iloc[0]
    
    # === Agrupamento ===
    grouped = {}
    binary_columns = []

    for col, meta in selected_data.items():
        if meta.get("group"):
            grouped.setdefault(meta["group"], []).append((col, meta))
        elif meta.get("binary"):
            binary_columns.append((col, meta))

    # === Pie charts por grupo ===
    if grouped:
        st.subheader("Distribuições agrupadas")
        for group_name, variables in grouped.items():
            labels = []
            values = []
            for col, meta in variables:
                labels.append(meta['alias'])
                values.append(bairro_data[col])
            fig = px.pie(
                names=labels,
                values=values,
                title=f"Distribuição: {group_name.replace('_', ' ').title()}"
            )
            st.plotly_chart(fig)

    # === Pie charts binários ===
    if binary_columns:
        st.subheader("Distribuições binárias")
        for col, meta in binary_columns:
            valor_true = bairro_data[col]
            valor_false = 100 - valor_true
            nome_true = meta['alias']
            nome_false = meta.get('other_description', 'Outro')
            fig = px.pie(
                names=[nome_true, nome_false],
                values=[valor_true, valor_false],
                title=meta['description']
            )
            st.plotly_chart(fig)