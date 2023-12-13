# --- MODULO PARA IMPORTAÇÃO DO PYGWLKER (VISUALIZAÇÃO) ---
import datetime as dt
import numpy as np
import pandas as pd
import streamlit as st
import base64                                   # modulo padrão (utilizado p/ exportação do arquivo)
from io import StringIO, BytesIO                # modulo padrão (utilizado p/ exportação do arquivo)


import openpyxl                                 # pip install openpyxl
import pygwalker as pyg                         # pip install pygwalker
import streamlit.components.v1 as components    
import plotly.express as px                     # pip install plotly-express

# --- AUXILIARES ---
import db_connection
import constants


# --- CONFIG ---
COR_PALETA = constants.PALETA_GRAFICOS_OP01


# --- DOWNLOAD EXCEL ---
def generate_excel_download_link(df):
    '''Retorna um link href com arquivo para download.'''

    # Obtendo o nome do arquivo
    datahora_atual = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    excel_filename = f"registros_videre_{datahora_atual}.xlsx"
    # Salvando
    towrite = BytesIO()
    df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download={excel_filename}>Download Arquivo Excel</a>'

    return st.markdown(href, unsafe_allow_html=True)


# --- DOWNLOAD HTML ---
def generate_html_download_link(fig):
    '''Retorna um arquivo .html dos Gráficos do App.'''

    # Obtendo o nome do arquivo
    datahora_atual = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    html_filename = f"graficos_videre_{datahora_atual}.html"
    # Salvando
    towrite = StringIO()
    fig.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()

    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download={html_filename}>Download Graficos</a>'

    return st.markdown(href, unsafe_allow_html=True)


def create_data_viz_pygwalk():
    '''Cria o html para geração de visualização.'''

    # Importando a tabela do Formulario
    df = db_connection.load_data()
    # Criando o html
    pyg_html = pyg.walk(dataset=df, return_html=True)
    # Criando o component p/ renderizar no streamlit
    component = components.html(html=pyg_html, height=1000, scrolling=True)

    return component


def load_viz_config(filepath):
    '''Função auxiliar para retornar a string do arquivo.json de configuração do relatório.
       Necessário criar um arquivo config.json com a especificação do arquivo.'''

    with open(filepath, 'r') as config_file:
        config_str = config_file.read()
    return config_str

# - DATAFRAMES ---
# Agregação Simples
def aggregate_df(dataframe, columns_by):
    '''Faz a agregação do Dataframe pelo tipo especificado.
    Util para resumir os dados para plotagem.'''

    # Definindo as agregações
    aggregations = {
        'VALOR VENDA': 'sum',
        'VLR LENTE + TRAT.': 'sum',
        'OS': 'count',
        'OS REF': 'count',
        'Custo Total': 'sum',
        'MKP': 'mean',
        '%': 'mean'
    }

    # Fazendo a agregação
    df_aggregated = dataframe.groupby(by=columns_by).agg(aggregations).reset_index()

    return df_aggregated


# --- MEDIA MOVEL ---
def get_moving_average_df(dataframe, column_by):
    '''Retorna um Dataframe com as médias móveis de acordo com as Datas Iniciais e Finais selecionadas.'''

    # Faz uma copia
    dataframe = dataframe.copy()
    # Retem a 1a e Ultima data
    data_inicio = dataframe['DATA DA VENDA'].min()
    data_fim = dataframe['DATA DA VENDA'].max()
    # Calcula o número de dias
    num_dias = (data_fim - data_inicio).days

    # Verifica o período da média móvel dinamicamente
    if num_dias >= 90:
        periodo_media_movel = '90d'
    elif num_dias >= 60:
        periodo_media_movel = '60d'
    else:
        periodo_media_movel = '30d'

     # Calcula a média móvel
    dataframe['MediaMovel'] = dataframe.rolling(window=periodo_media_movel, 
                                                on='DATA DA VENDA')\
                                                    [column_by].mean()

    return dataframe, periodo_media_movel


# --- GRÁFICOS ---

# --- BARRAS ---
def plot_bar_chart(df, x_axis, y_axis, color_axis, title_text, text_format=',.2f', orientation='v'):
    '''Retorna um gráfico de BARRAS do plotly express.'''

    fig = px.bar(data_frame=df,
                 x=x_axis,
                 y=y_axis,
                 color=color_axis,
                 text_auto=text_format,
                 title=title_text,
                 color_discrete_sequence=COR_PALETA,
                 template='simple_white',
                 )

    # bar_chart = st.plotly_chart(figure_or_data=fig, use_container_width=True)

    return fig


# --- LINHA ---
def plot_line_chart(df, x_axis, y_axis, color_axis, title_text):
    '''Retorna um gráfico de LINHAS do plotly express.'''

    fig = px.line(data_frame=df,
                  x=x_axis,
                  y=y_axis,
                  color=color_axis,
                  title=title_text,
                  color_discrete_sequence=COR_PALETA,
                  template='simple_white'
                  )

    return fig
