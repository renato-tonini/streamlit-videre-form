import datetime as dt
import locale             # Para formatação correta da moeda
import pandas as pd
import streamlit as st

# pip install streamlit-option-menu (menu suspenso)
from streamlit_option_menu import option_menu
import plotly.express as px                      # pip install plotly-express
from plotly.subplots import make_subplots

# --- AUXILIARES ---
import constants
import db_connection
import dataviz


# ==============================
# --- CONFIG INICIAL (MOEDA) ---
# ==============================
# Configurando a localização para o Brasil
# locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
# locale.setlocale(locale.LC_ALL, 'pt_BR')
# locale.setlocale(locale.LC_ALL, "Portuguese_Brazil.1252")


# ==================
# --- CONSTANTES ---
# ==================
# --- DATA BASE CONSULTA ---
DATA_REFERENCIA = "DATA DA VENDA"

# --- PALETA DOS GRÁFICOS ---
COR_PALETA = constants.PALETA_GRAFICOS_OP01

# --- TARGETS ---
TARGET_MARKUP = 4
TARGET_PCT_CUSTO = 0.1


# ==================
# --- LISTAS ---
# ==================
# --- LISTA COM ORDEM DAS COLUNAS P/ EXIBIÇÃO ---
columns_order = ['LOJA', 'TIPO', 'OS', 'OS REF', 'FORNECEDOR', 'TIPO LENTE', 'QUALIDADE',
                 'LENTE', 'VALOR VENDA', 'VLR LENTE + TRAT.',
                 #  'Arm.', 'Mont.', 'Exame',
                 'Custo Total', 'MKP', '%', 'VENDEDOR', 'CLIENTE', 'DATA DA VENDA',
                 'ENTREGA', 'DATA PEDIDO', 'DATA LENTE', 'MONTAGEM', 'RETIRADA',
                 #  'N° PEDIDO', 'OBSERVAÇÃO / MOTIVO', 'O.S ANTIGA / REF ARMAÇÃO',
                 #  'IsActive?', 'user', 'modified'
                 ]


# --- LISTA DE COLUNAS P/ TRATAMENTO ---
# Exclusão - Colunas desnecessárias a serem excluídas
columns_to_drop = ['N° PEDIDO', 'OBSERVAÇÃO / MOTIVO',
                   'O.S ANTIGA / REF ARMAÇÃO', 'user', 'modified']


# --- CONVERSAO DOS TIPOS DE DADOS ---
date_columns = ['DATA DA VENDA', 'ENTREGA', 'DATA PEDIDO',
                'DATA LENTE', 'MONTAGEM', 'RETIRADA']

float_columns = ['VALOR VENDA', 'VLR LENTE + TRAT.', 'Arm.',
                 'Mont.', 'Exame', 'Custo Total', 'MKP', '%']

cat_columns = ['LOJA', 'TIPO', 'OS', 'OS REF', 'FORNECEDOR',
               'TIPO LENTE', 'QUALIDADE', 'LENTE',
               'VENDEDOR', 'CLIENTE', 'IsActive?']


# --- LISTA COM FILTROS (VISÃO) ---
# Filtros de Tempo
visao_opcoes = ['Semanal', 'Quinzenal', 'Mensal',
                'Trimestral', "Semestral", 'Anual', 'Todas']


# ===============
# --- FUNÇÕES ---
# ===============
# --- MENU DE NAVEGAÇÃO ---
def get_selection_menu():
    '''Retorna um menu suspenso p/ troca entre Registros e Gráficos.'''
    selected_menu = option_menu(
        menu_title=None,
        # source: https://icons.getbootstrap.com/
        options=['Registros', 'Gráficos'],
        icons=['table', 'bar-chart-fill'],
        orientation='horizontal',
        default_index=0,
        menu_icon=['table', 'bar-chart-line-fill'],
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#220750", "font-size": "20px"},
            "nav-link": {"font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#FF4B4B"},
        }
    )

    return selected_menu


# --- IMPORTAÇÃO DA BASE ---
def import_data(tabela=constants.TABELAS_GSHEETS[0]):
    '''Retorna o dataframe do Googlesheets com um pre-processamento.'''

    # Chamando função de carregamento dos dados
    df = db_connection.load_data()

    # # Criando a conexão com Google Sheets
    # conn = st.connection(name="gsheets", type=GSheetsConnection)
    # # Lendo a planilha especificada no parametro da função
    # df = conn.read(worksheet=tabela) #, ttl=0)
    # # Retirando os registros em branco
    # df = df.dropna(how='all')
    # # Criando uma cópia
    # df = df.copy()

    # Pre-processamento do Dataframe
    df_pre_processed = pre_process_df(df)

    return df_pre_processed


# --- PRE-PROCESSAMENTO DO DATAFRAME ORIGINAL ---
def pre_process_df(dataframe):
    '''Elimina colunas desnecessarias, filtra registros ativos, e faz a conversao correta das colunas'''

    # Eliminando colunas desnecessárias p/ esta análise
    dataframe = dataframe.drop(columns_to_drop, axis=1, inplace=False)

    # Conversão de Datas
    dataframe[date_columns] = dataframe[date_columns].apply(
        pd.to_datetime, errors='coerce')

    # Conversõa de Valores Numericos
    dataframe[float_columns] = dataframe[float_columns].astype(float)

    # Conversõa de strings
    dataframe[cat_columns] = dataframe[cat_columns].astype(str)

    # Filtrando o Dataframe somente com registros ativos
    dataframe = dataframe[(dataframe['IsActive?'] == 'VERDADEIRO') |
                          (dataframe['IsActive?'] == True) |
                          (dataframe['IsActive?'] == 1)]

    # Ordenando por 'DATA DA VENDA' e fazendo uma cópia
    dataframe = dataframe.sort_values(
        by='DATA DA VENDA').reset_index(drop=True).copy()

    return dataframe


# --- RANGE DE DATAS DINAMICO ---
def get_initial_slider_date(visao_selecionada, data_final_ref):
    ''' Retorna a data inicial baseado no tipo de visão selecionada baseado na data final de referencia passada.'''

    if visao_selecionada == 'Semanal':
        data_inicial_slider = data_final_ref - pd.DateOffset(weeks=1)
    elif visao_selecionada == 'Quinzenal':
        data_inicial_slider = data_final_ref - pd.DateOffset(weeks=2)
    elif visao_selecionada == 'Mensal':
        data_inicial_slider = data_final_ref - pd.DateOffset(months=1)
    elif visao_selecionada == 'Trimestral':
        data_inicial_slider = data_final_ref - pd.DateOffset(months=3)
    elif visao_selecionada == 'Semestral':
        data_inicial_slider = data_final_ref - pd.DateOffset(months=6)
    elif visao_selecionada == 'Anual':
        data_inicial_slider = data_final_ref - pd.DateOffset(years=1)
    else:  # Todas as datas (será considerada a primeira data do dataset)
        data_inicial_slider = None

    return data_inicial_slider


def get_date_slider(df):
    '''Cria um slider de datas.'''

    # Selectbox com a visão desejada (semanal, quinzenal, etc...)
    visao_selecionada = st.sidebar.selectbox(label="Visão", options=visao_opcoes,
                                             placeholder="Selecione o período desejado", index=None)

    # --- DATAS DE REFERENCIA PARA SLIDER ---
    # PRIMEIRA DATA
    primeira_data_disponivel = min(df['DATA DA VENDA'].dt.date)

    # ULTIMA DATA
    # Opções:
    #   01 - Ultima data do Dataset
    ultima_data_disponivel = max(df['DATA DA VENDA'].dt.date)
    #   02 - Data Atual
    # ultima_data_disponivel = dt.date.today()

    # Chamando função para retornar a data inicial a partir da visão selecionada
    data_inicial_slider = get_initial_slider_date(
        visao_selecionada=visao_selecionada, data_final_ref=ultima_data_disponivel)

    # Verifica se o usuario escolheu Todas (função retorna None)
    if data_inicial_slider is None:
        # Atribui a primeira data do conjunto
        data_inicial_slider = primeira_data_disponivel

    # Convertendo em Data somente (exclui hora p/ evitar erro no slider)
    data_inicial_slider = dt.date(
        data_inicial_slider.year, data_inicial_slider.month, data_inicial_slider.day)
    # Criando o Slider
    slider_data = st.sidebar.slider(label="Data Mínima", min_value=primeira_data_disponivel,
                                    max_value=ultima_data_disponivel,
                                    value=(data_inicial_slider,
                                           ultima_data_disponivel),
                                    format="DD/MM/YYYY",
                                    key="slider_data")

    # Formatando as datas do Slider de Datas
    data_inicial_slider = slider_data[0].strftime("%d/%m/%Y")
    data_final_slider = slider_data[1].strftime("%d/%m/%Y")

    return data_inicial_slider, data_final_slider


def get_multiselect_filters(df):
    # --- CABECALHOS DA BASE ---
    # Chamando a função para obter os cabeçalhos da Planilha Formulario
    header_list = db_connection.get_form_fields()

    # --- OPÇÕES MULTISELECT ---
    # Lojas
    opcoes_lojas = df['LOJA'].unique()
    multi_lojas = st.sidebar.multiselect(
        label=header_list[0], options=opcoes_lojas, default=opcoes_lojas, key="multi_lojas")
    # Vendedor
    # Filtrando as opções de vendedor somente dentro da(s) Loja(s) escolhida(s)
    if multi_lojas:
        opcoes_vendedor = df[df['LOJA'].isin(multi_lojas)]['VENDEDOR'].unique()
    else:
        opcoes_vendedor = df['VENDEDOR'].unique()

    multi_vendedor = st.sidebar.multiselect(
        label=header_list[16], options=opcoes_vendedor, default=opcoes_vendedor, key="multi_vendedor")
    # Tipos
    opcoes_tipo = df['TIPO'].unique()
    multi_tipos = st.sidebar.multiselect(
        label=header_list[1], options=opcoes_tipo, default=['VENDA'], key="multi_tipos")
    # Fornecedor
    opcoes_fornecedor = df['FORNECEDOR'].unique()
    multi_fornecedores = st.sidebar.multiselect(
        label=header_list[4], options=opcoes_fornecedor, default=opcoes_fornecedor, key="multi_fornecedores")
    # Tipo de Lente
    opcoes_tipo_lente = df['TIPO LENTE'].unique()
    multi_tipo_lente = st.sidebar.multiselect(
        label=header_list[5], options=opcoes_tipo_lente, default=opcoes_tipo_lente, key="multi_tipo_lente")
    # Qualidade
    # Filtrando as opções de qualidade somente dentro do(s) Tipo(s) de Lente escolhido(s)
    if multi_tipo_lente:
        opcoes_qualidade = df[df['TIPO LENTE'].isin(
            multi_tipo_lente)]['QUALIDADE'].unique()
    else:
        opcoes_qualidade = df['QUALIDADE'].unique()

    multi_qualidade = st.sidebar.multiselect(
        label=header_list[6], options=opcoes_qualidade, default=opcoes_qualidade, key="multi_qualidade")

    return multi_lojas, multi_vendedor, multi_tipos, multi_fornecedores, multi_tipo_lente, multi_qualidade


def filter_df(df, data_inicial_slider, data_final_slider,
              multi_lojas, multi_vendedor, multi_tipos, multi_fornecedores, multi_tipo_lente, multi_qualidade):

    # --- DATAS ---
    # Data Inicial e Final do Slider
    df_filtered = df[(df['DATA DA VENDA'] >= data_inicial_slider)
                     & (df['DATA DA VENDA'] <= data_final_slider)]

    # --- CATEGORIAS ---
    # Lojas
    df_filtered = df_filtered[df_filtered['LOJA'].isin(multi_lojas)]
    # Vendedor
    df_filtered = df_filtered[df_filtered['VENDEDOR'].isin(multi_vendedor)]
    # Tipos
    df_filtered = df_filtered[df_filtered['TIPO'].isin(multi_tipos)]
    # Fornecedor
    df_filtered = df_filtered[df_filtered['FORNECEDOR'].isin(
        multi_fornecedores)]
    # Tipo de Lente
    df_filtered = df_filtered[df_filtered['TIPO LENTE'].isin(multi_tipo_lente)]
    # Qualidade
    df_filtered = df_filtered[df_filtered['QUALIDADE'].isin(multi_qualidade)]

    return df_filtered


def get_general_kpis(df):
    '''Retorna um dataframe com os cálculos dos KPIs e uma coluna adicional com valores formatados.'''

    # Cálculos básicos
    total_vendas = df['VALOR VENDA'].sum()
    total_lentes = df['VLR LENTE + TRAT.'].sum()
    total_custos = df['Custo Total'].sum()

    # Verificação para retirar NAs
    if total_vendas == 0 or total_custos == 0:
        pct_custo_medio = 0
        markup_medio = 0
        delta_pct_custo_medio = 0
        delta_markup_medio = 0
    else:
        pct_custo_medio = total_lentes / total_vendas
        markup_medio = df['MKP'].mean()
        # Diferenças sobre o Target (Deltas)
        delta_pct_custo_medio = pct_custo_medio - TARGET_PCT_CUSTO
        delta_markup_medio = markup_medio - TARGET_MARKUP

    # Criando um DataFrame para o retorno da função
    # Primeira coluna com o valor calculado e a segunda com o valor formatado
    df_kpis = pd.DataFrame(
        {
            "total_vendas": [total_vendas, format_numbers(total_vendas, 'currency')],
            "total_lentes": [total_lentes, format_numbers(total_lentes, 'currency')],
            "total_custos": [total_custos, format_numbers(total_custos, 'currency')],
            "pct_custo_medio": [pct_custo_medio, format_numbers(pct_custo_medio, '%')],
            "markup_medio": [markup_medio, format_numbers(markup_medio, 'markup')],
            "delta_pct_custo_medio": [delta_pct_custo_medio, format_numbers(delta_pct_custo_medio, '%')],
            "delta_markup_medio": [delta_markup_medio, format_numbers(delta_markup_medio, 'markup')]
        },  # Renomeando as colunas
        index=["KPIs", "KPIs formatted"]).T

    return df_kpis


def get_sales_kpis(df_filtered):
    '''Retorna um dataframe com os cálculos dos KPIs e uma coluna adicional com valores formatados.'''

    # Contagem distinta de OS (NFs emitidas - Nº de Vendas)
    contagem_os = df_filtered['OS'].nunique()
    # Contagem distinta de OS REF (Número de Produtos Vendidos)
    contagem_os_ref = df_filtered['OS REF'].nunique()

    # Ordenando pela coluna 'VALOR VENDA' e retornando o 1º registro
    vendas_ordenada = df_filtered.sort_values(
        by='VALOR VENDA', ascending=False)
    # Verificando se possui registros dentro dos filtros aplicados
    if vendas_ordenada.shape[0] == 0:
        ticket_medio_os = 0
        ticket_medio_os_ref = 0
        top_vendedor = "-"
    else:
        # Ticket médio por OS  (Ticket médio por NFs emitida - Nº de Vendas)
        ticket_medio_os = df_filtered['VALOR VENDA'].sum() / contagem_os
        # Ticket médio por OS REF (Ticket médio por Produto)
        ticket_medio_os_ref = df_filtered['VALOR VENDA'].sum(
        ) / contagem_os_ref
        top_vendedor = vendas_ordenada['VENDEDOR'].tolist()[0]

    # Criando um DataFrame para o retorno da função
    # Primeira coluna com o valor calculado e a segunda com o valor formatado
    df_kpis = pd.DataFrame(
        {
            "contagem_os": [contagem_os, contagem_os],
            "contagem_os_ref": [contagem_os_ref, contagem_os_ref],
            "ticket_medio_os": [ticket_medio_os, format_numbers(ticket_medio_os, 'currency')],
            "ticket_medio_os_ref": [ticket_medio_os_ref, format_numbers(ticket_medio_os_ref, 'currency')],
            "top_vendedor": [top_vendedor, top_vendedor],
        },  # Renomeando as colunas
        index=["KPIs", "KPIs formatted"]).T

    return df_kpis


def calculate_deadlines(df):
    '''Calcula a diferença de dias entre a data base ('DATA DA VENDA') e demais datas.
    Retorna um Dataframe com as diferenças.
    '''

    # Lista com as colunas de datas p/ cálculo
    date_columns_to_check = ['ENTREGA', 'DATA PEDIDO',
                             'DATA LENTE', 'MONTAGEM', 'RETIRADA']
    # Filtra as linhas onde a data relevante não está vazia
    df_filtered = df[df['DATA DA VENDA'].notnull()]
    # Calcula a diferença em dias entre a data relevante ('DATA DA VENDA') e cada outra data
    for coluna_data in ['ENTREGA', 'DATA PEDIDO', 'DATA LENTE', 'MONTAGEM', 'RETIRADA']:
        # Verifica a diferença entre a DATA DA VENDA e demais colunas de Datas
        df[f'diff_{coluna_data}'] = (
            df[coluna_data] - df['DATA DA VENDA']).dt.days
        # Substitui diferenças negativas por NaN
        df.loc[df[f'diff_{coluna_data}'] < 0, f'diff_{coluna_data}'] = None

    # Filtra as colunas de diferenças
    colunas_diferencas = [f'diff_{coluna_data}' for coluna_data in [
        'ENTREGA', 'DATA PEDIDO', 'DATA LENTE', 'MONTAGEM', 'RETIRADA']]
    df_diferencas = df[colunas_diferencas]

    return df_diferencas


def get_deadlines_kpis(df_diferencas):
    '''Retorna um dataframe com as médias de datas.'''

    # Calcula a média das diferenças (Geral)
    prazo_medio_geral = df_diferencas.mean().mean()
    # Separando o dataframe de prazos médios
    prazo_medio_entrega = df_diferencas['diff_ENTREGA'].mean()
    prazo_medio_pedido = df_diferencas['diff_DATA PEDIDO'].mean()
    prazo_medio_data_lente = df_diferencas['diff_DATA LENTE'].mean()
    prazo_medio_montagem = df_diferencas['diff_MONTAGEM'].mean()
    prazo_medio_retirada = df_diferencas['diff_RETIRADA'].mean()

    # Criando um Dataframe para retorno da função
    # Primeira coluna é o valor calculado e a segunda o valor formatado
    df_deadlines = pd.DataFrame(
        {
            "prazo_medio_geral": [prazo_medio_geral, format_days(prazo_medio_geral)],
            "prazo_medio_entrega": [prazo_medio_entrega, format_days(prazo_medio_entrega)],
            "prazo_medio_pedido": [prazo_medio_pedido, format_days(prazo_medio_pedido)],
            "prazo_medio_data_lente": [prazo_medio_data_lente, format_days(prazo_medio_data_lente)],
            "prazo_medio_montagem": [prazo_medio_montagem, format_days(prazo_medio_montagem)],
            "prazo_medio_retirada": [prazo_medio_retirada, format_days(prazo_medio_retirada)],
        },  # Renomeando as colunas
        index=["KPIs", "KPIs formatted"]).T

    return df_deadlines


# --- FUNÇÕES DE FORMATAÇÃO ---
# Numericos
def format_numbers(value, data_type=['currency', '%', 'markup']):
    if data_type == 'currency':
        return "R$ {:,.2f}".format(value) # locale.currency(value, grouping=True, symbol=None)
    if data_type == '%':
        return "{:.2%}".format(value)
    if data_type == 'markup':
        return "{:.2f}".format(value)
    else:  # p/ evitar erros (não faz formatação alguma)
        return value


def format_currency(val):
    if pd.notna(val):
        return f"R$ {val:.2f}"
    return val


# Dias
def format_days(val):
    '''Formata as datas para os KPIs incluindo o sufixo 'dia(s) ou '-' caso esteja vazio'''

    if pd.isna(val) or val is None:
        return "-"
    else:
        return "{:.0f} {}".format(val, "dia" if val == 1 else "dias")


# Datas
def format_date(val):
    '''Formata as datas em DD/MM/YYYY.'''
    if isinstance(val, pd.Timestamp):
        return val.strftime("%d/%m/%Y")
    return val


# --- CORES ---
def color_df_mkup(val):
    '''Retorna a cor do KPI de Markup conforme criterio'''

    # Acima do Target
    if val >= TARGET_MARKUP:
        color = 'green'
    # Até 80% do Target
    elif val >= (TARGET_MARKUP * 0.8):
        color = 'orange'
    # Demais: Abaixo de 80% do target
    else:
        color = 'red'

    return f'color: {color}'


def color_df_pct_custo(val):
    '''Retorna a cor do KPI de % Custo conforme criterio'''

    # Acima do Target
    if val >= TARGET_PCT_CUSTO:
        color = 'green'
    # Até 80% do Target
    elif val >= (TARGET_PCT_CUSTO * 0.8):
        color = 'orange'
    # Demais: Abaixo de 80% do target
    else:
        color = 'red'

    return f'color: {color}'


def add_arrows_mkup(val):
    '''Retorna a seta de acordo com o KPI de Markup.'''

    # Acima do Target
    if val >= TARGET_MARKUP:
        arrow = '↑'
    # Até 80% do Target
    elif val >= (TARGET_MARKUP * 0.8):
        arrow = '→'
    # Demais: Abaixo de 80% do target
    else:
        arrow = '↓'

    return f'{val:.2f} {arrow}'


def add_arrows_pct_cost(val):
    '''Retorna a seta de acordo com o KPI de % Custo.'''

    # Acima do Target
    if val >= TARGET_PCT_CUSTO:
        arrow = '↑'
    # Até 80% do Target
    elif val >= (TARGET_PCT_CUSTO * 0.8):
        arrow = '→'
    # Demais: Abaixo de 80% do target
    else:
        arrow = '↓'

    return f'{val:.2%} {arrow}'


def get_styled_df(dataframe):
    '''Estiliza o Dataframe para ser exibido com as formatações corretas.'''

    styled_df = dataframe.style.applymap(func=color_df_mkup, subset='MKP')\
        .applymap(func=color_df_pct_custo, subset='%')\
        .format({'MKP': add_arrows_mkup,
                 '%': add_arrows_pct_cost,
                 'VALOR VENDA': format_currency,
                 'VLR LENTE + TRAT.': format_currency,
                 'Custo Total': format_currency,
                 'DATA DA VENDA': format_date,
                 "ENTREGA": format_date,
                 "DATA PEDIDO": format_date,
                 "DATA LENTE": format_date,
                 "MONTAGEM": format_date,
                 "RETIRADA": format_date,
                 "diff_ENTREGA": format_days,
                 "diff_DATA PEDIDO": format_days,
                 "diff_DATA LENTE": format_days,
                 "diff_MONTAGEM": format_days,
                 "diff_RETIRADA": format_days,
                 })

    return styled_df


def create_queries():
    '''Função principal chamada pela main para Consulta de Registros.'''

    # --- IMPORTANDO A BASE ---
    # Importa a base e faz um pre-processamento simples
    df = import_data()

    # --- SIDEBAR C/ FILTROS ---
    # Incluindo um divisor para os filtros
    with st.sidebar:
        # Incluindo um divisor no Sidebar p/ separação dos filtros
        st.divider()
        # Titulo
        st.subheader("Filtros de Consulta")

        # --- SLIDER PERIODO (DATAS) ---
        data_inicial_slider, data_final_slider = get_date_slider(df)

        # --- FILTROS MULTISELECT ---
        multi_lojas, multi_vendedor, multi_tipos, multi_fornecedores, multi_tipo_lente, multi_qualidade = get_multiselect_filters(
            df)

    # --- FILTRANDO DATAFRAME ---
    # Função para filtrar o DataFrame
    # df_filtered = filter_df(df, data_inicial_slider, data_final_slider, multi_lojas, multi_vendedor, multi_tipos, multi_fornecedores, multi_tipo_lente, multi_qualidade)

    df_filtered = df[
        # DATAS
        (df['DATA DA VENDA'] >= data_inicial_slider)
        & (df['DATA DA VENDA'] <= data_final_slider)
        # MULTISELECT
        & (df['LOJA'].isin(multi_lojas))
        & (df['VENDEDOR'].isin(multi_vendedor))
        & (df['TIPO'].isin(multi_tipos))
        & (df['FORNECEDOR'].isin(multi_fornecedores))
        & (df['TIPO LENTE'].isin(multi_tipo_lente))
        & (df['TIPO LENTE'].isin(multi_tipo_lente))
        & (df['QUALIDADE'].isin(multi_qualidade))
    ]

    # --- KPI's ---
    # KPIs Geral
    df_kpis_geral = get_general_kpis(df_filtered)
    # KPIs Vendas
    df_kpis_vendas = get_sales_kpis(df_filtered)

    # KPIs de Prazos
    # Função para retornar um Dataframe com as diferenças de Datas
    df_diferencas_deadlines = calculate_deadlines(df_filtered)
    # Função para retornar um Dataframe com um resumo das diferenças
    # Obs.: passado como parametro a variavel da função anterior
    df_deadlines_kpis = get_deadlines_kpis(df_diferencas_deadlines)

    # --- EXIBIÇÃO DOS DADOS ---
    # TODO: Definir a opção de Menu (Tab ou Suspenso)

    # --- TABS ---
    # tab1, tab2 = st.tabs(tabs=[':clipboard: Cadastros', ":bar_chart: Visualização"])
    # --- CONSULTA REGISTROS ---
    # with tab1:
    # --- MENU SUSPENSO ---
    selected_menu = get_selection_menu()

    # Verificação do Menu Suspenso
    if selected_menu == 'Registros':

        st.header(body="Consultas")

        # --- KPIs ---
        # GERAL
        st.subheader("Geral")

        # Separando os containers
        col1, col2, col3, col4, col5 = st.columns(5)
        # Exibindo as métricas
        col1.metric(
            label="Vendas", value=df_kpis_geral['KPIs formatted'][0], help="Somatória da coluna VALOR VENDA")
        col2.metric(
            label="Lentes", value=df_kpis_geral['KPIs formatted'][1], help="Somatória da coluna VLR LENTE + TRAT.")
        col3.metric(
            label="Custos", value=df_kpis_geral['KPIs formatted'][2], help="Somatória da coluna Custo Total")
        col4.metric(label="Custo Médio %", value=df_kpis_geral['KPIs formatted'][3],
                    delta=df_kpis_geral['KPIs formatted'][5], help="Divisão entre VLR LENTE + TRAT. e VALOR VENDA")
        col5.metric(label="Markup Médio", value=df_kpis_geral['KPIs formatted'][4],
                    delta=df_kpis_geral['KPIs formatted'][6], help="Média da coluna MKP")

        # VENDAS
        st.subheader("Vendas")

        # Separando os containers
        col1, col2, col3, col4, col5 = st.columns(5)

        # # Exibindo as métricas
        col1.metric(label="Número de NFs",
                    value=df_kpis_vendas['KPIs formatted'][0], help="Contagem de OS distintas.")
        col2.metric(label="Número de Produtos Vendidos",
                    value=df_kpis_vendas['KPIs formatted'][1], help="Contagem de OS REF distintas.")
        col3.metric(label="Ticket Médio por NF",
                    value=df_kpis_vendas['KPIs formatted'][2], help="Valor Médio de VALOR VENDA por número de OS.")
        col4.metric(label="Ticket Médio por Produto",
                    value=df_kpis_vendas['KPIs formatted'][3], help="Valor Médio do VALOR VENDA por número de OS REF.")
        col5.metric(label="Top Vendedor",
                    value=df_kpis_vendas['KPIs formatted'][4], help="Vendedor com maior VALOR VENDA.")

        # PRAZOS
        st.subheader("Prazos Médios")

        # Separando os containers
        col1, col2, col3, col4, col5 = st.columns(5)
        # Exibindo as métricas
        col1.metric(label="Média de Entrega",
                    value=df_deadlines_kpis['KPIs formatted'][1], help="Prazo médio de entrega com relação a DATA DA VENDA.")
        col2.metric(label="Média da Pedido",
                    value=df_deadlines_kpis['KPIs formatted'][2],  help="Prazo médio do Pedido com relação a DATA DA VENDA.")
        col3.metric(label="Média da Data da Lente",
                    value=df_deadlines_kpis['KPIs formatted'][3], help="Prazo médio da Lente com relação a DATA DA VENDA.")
        col4.metric(label="Média de Montagem",
                    value=df_deadlines_kpis['KPIs formatted'][4], help="Prazo médio de Montagem com relação a DATA DA VENDA.")
        col5.metric(label="Média de Retirada",
                    value=df_deadlines_kpis['KPIs formatted'][5], help="Prazo médio de Retirada com relação a DATA DA VENDA.")

        # # Disclaimer da Base de Comparação de Datas
        # disclaimer = st.markdown("<p style='font-size: 13px;'> <em>* Todos os prazos são comparados com a DATA DA VENDA</em> </p>", unsafe_allow_html=True)

        st.divider()

        # --- DATAFRAME ---
        st.subheader("Registros:")

        # --- EXIBIÇÃO DO PERÍODO FILTRADO
        # Exibindo o período dos filtros de data (slider)
        # exibicao_periodo = st.markdown(f'''Período de **{data_inicial_slider}** até **{data_final_slider}**''')
        exibicao_periodo = st.markdown(f'''<span style="font-size:1.3em;"> Período de **{data_inicial_slider}** até **{data_final_slider}**</span> ''',
                                       unsafe_allow_html=True)

        # # Estiliza o Dataframe - Aplica as devidas formatações e cores, conforme KPI pré-definidos.
        df_styled = get_styled_df(df_filtered)

        # Exibindo o Dataframe com colunas formatadas
        # st.dataframe(df_filtered.iloc[:, :-6],  # Omitindo colunas do usuário final
        st.dataframe(df_styled,  # Omitindo colunas do usuário final
                     use_container_width=True,   # utilizando toda margem
                     hide_index=True,            # Omitindo indice

                     # Configurando a formatação
                     column_config={
                         # Moedas
                         "VALOR VENDA": st.column_config.ProgressColumn(label="VALOR VENDA", format="R$ %.2f", min_value=0, max_value=df_filtered['VALOR VENDA'].max(), help="O tamanho máximo das barras são baseados no valor mais alto dentro do filtro especificado."),
                         "Custo Total": st.column_config.ProgressColumn(label="Custo Total", format="R$ %.2f", min_value=0, max_value=df_filtered['Custo Total'].max()),
                         "VLR LENTE + TRAT.": st.column_config.ProgressColumn(label="VLR LENTE + TRAT.", format="R$ %.2f", min_value=0, max_value=df_filtered['VLR LENTE + TRAT.'].max()),

                         # Percentual (Alterado o formato da coluna original do dataframe e passado como texto)
                         #  "%": st.column_config.NumberColumn(),
                         #  "%": st.column_config.TextColumn(),
                         "diff_ENTREGA": st.column_config.NumberColumn(label="Prazo Entrega"),
                         "diff_DATA PEDIDO": st.column_config.NumberColumn(label="Prazo Pedido"),
                         "diff_DATA LENTE": st.column_config.NumberColumn(label="Prazo Lente"),
                         "diff_MONTAGEM": st.column_config.NumberColumn(label="Prazo Montagem"),
                         "diff_RETIRADA": st.column_config.ProgressColumn(label="Prazo Retirada", format="%d dias", min_value=0, max_value=df_filtered['diff_RETIRADA'].max()),
                     },  # variável definida no inicio do script + Colunas adicionais calculadas
                     column_order=columns_order + \
                     ['diff_ENTREGA', 'diff_DATA PEDIDO', 'diff_DATA LENTE',
                      'diff_MONTAGEM', 'diff_RETIRADA']

                     )

        # Exibindo o número de registros com os filtros (todos)
        st.markdown(f''' **Número de Registros:** {len(df_filtered)}''')

        # --- SESSÃO DE DOWNLOAD DOS REGISTROS ---
        # Cria um novo DataFrame sem modificar o original
        # excluindo a coluna 'IsActive?'
        df_to_export = df_filtered.drop(labels='IsActive?', axis=1)
        # Gerando o arquivo
        dataviz.generate_excel_download_link(df=df_filtered)

    # --- GRÁFICOS ---
    # --- MENU TAB ---
    # with tab2:

    # --- MENU SUSPENSO ---
    if selected_menu == 'Gráficos':

        st.markdown('---')

        st.header(body="Visualização")
        # Exibe o período selecionado
        exibicao_periodo = st.markdown(f'''<span style="font-size:1.3em;"> Período de **{data_inicial_slider}** até **{data_final_slider}**</span> ''',
                                       unsafe_allow_html=True)

        # --- EXPANSOR COM DATAFRAME ---
        with st.expander("Dados:"):
            # Exibe os dados do Dataframe
            st.dataframe(df_filtered)

        # ================
        # --- SEÇÃO 01 ---
        # ================
        st.header("Seção 01 - Média Móvel ao longo do tempo")

        # --- DATAS / MÉDIA MÓVEL ---
        col1, col2, col3 = st.columns(3)
        with col1:
            # --- GRÁFICO 01 ---
            # Obtendo a média móvel de VENDAS
            df_moving_average_vendas, periodo_media_movel = dataviz.get_moving_average_df(dataframe=df_filtered,
                                                                                          column_by='VALOR VENDA')

            # Plotando o Gráfico
            fig_datas_vendas = dataviz.plot_line_chart(df=df_moving_average_vendas, x_axis='DATA DA VENDA', y_axis='VALOR VENDA',
                                                       color_axis='LOJA',
                                                       title_text=f"Média móvel de VENDAS dos ultimos {periodo_media_movel}")

            # Plotando no streamlit
            line_chart = st.plotly_chart(
                figure_or_data=fig_datas_vendas, use_container_width=True)

        with col2:
            # --- GRÁFICO 02---
            # Obtendo a média móvel de CUSTO
            df_moving_average_custo, periodo_media_movel = dataviz.get_moving_average_df(dataframe=df_filtered,
                                                                                         column_by='Custo Total')

            # Plotando o Gráfico
            fig_data_custos = dataviz.plot_line_chart(df=df_moving_average_custo, x_axis='DATA DA VENDA', y_axis='Custo Total',
                                                      color_axis='LOJA',
                                                      title_text=f"Média móvel de CUSTO dos ultimos {periodo_media_movel}")

            # Plotando no streamlit
            line_chart = st.plotly_chart(
                figure_or_data=fig_data_custos, use_container_width=True)

        with col3:
            # --- GRÁFICO 03 ---
            # Obtendo a média móvel de MARKUP
            df_moving_average_markup, periodo_media_movel = dataviz.get_moving_average_df(dataframe=df_filtered,
                                                                                          column_by='MKP')

            # Plotando o Gráfico
            fig_data_markup = dataviz.plot_line_chart(df=df_moving_average_markup, x_axis='DATA DA VENDA', y_axis='MKP',
                                                      color_axis='LOJA',
                                                      title_text=f"Média móvel de MKP dos ultimos {periodo_media_movel}")

            # Plotando no streamlit
            line_chart = st.plotly_chart(
                figure_or_data=fig_data_markup, use_container_width=True)

        # ================
        # --- SEÇÃO 02 ---
        # ================
        st.header("Seção 02 - Valores por LOJA")

        # --- DATAFRAME ---
        df_agg_loja = dataviz.aggregate_df(
            dataframe=df_filtered, columns_by=['LOJA'])

        # --- VALORES POR LOJA ---
        col1, col2, col3 = st.columns(3)
        with col1:
            # --- GRÁFICO 01 ---
            fig_lojas_venda = dataviz.plot_bar_chart(df=df_agg_loja, x_axis='LOJA', y_axis='VALOR VENDA', color_axis='LOJA',
                                                     title_text='VENDAS por LOJA', text_format=".2s")

            bar_chart1 = st.plotly_chart(
                figure_or_data=fig_lojas_venda, use_container_width=True)

        with col2:
            # --- GRÁFICO 02 ---
            fig_lojas_custo = dataviz.plot_bar_chart(df=df_agg_loja, x_axis='LOJA', y_axis='Custo Total', color_axis='LOJA',
                                                     title_text='CUSTOS por LOJA', text_format=".2s")

            # Plotando no streamlit
            bar_chart2 = st.plotly_chart(
                figure_or_data=fig_lojas_custo, use_container_width=True)

        with col3:
            # --- GRÁFICO 03 ---
            fig_lojas_mkup = dataviz.plot_bar_chart(df=df_agg_loja, x_axis='LOJA', y_axis='MKP', color_axis='LOJA',
                                                    title_text='MARKUP Médio por LOJA', text_format=".2s")

            # Plotando no streamlit
            bar_chart3 = st.plotly_chart(
                figure_or_data=fig_lojas_mkup, use_container_width=True)

        # ================
        # --- SEÇÃO 03 ---
        # ================
        st.header("Seção 03 - Quantidades por LOJA")

        # --- QTDADES POR LOJA ---
        col1, col2, col3 = st.columns(3)
        with col1:
            # --- GRÁFICO 01 ---
            fig_lojas_os = dataviz.plot_bar_chart(df=df_agg_loja, x_axis='LOJA', y_axis='OS',
                                                  color_axis='LOJA', title_text='Quantidade de OS (NFs) por LOJA', text_format='.0d')

            bar_chart = st.plotly_chart(
                figure_or_data=fig_lojas_os, use_container_width=True)

        with col2:
            # --- GRÁFICO 02 ---
            fig_lojas_os_ref = dataviz.plot_bar_chart(df=df_agg_loja, x_axis='LOJA', y_axis='OS REF',
                                                      color_axis='LOJA', title_text='Quantidade de OS (Itens vendidos) por LOJA', text_format='.0d')
            bar_chart = st.plotly_chart(
                figure_or_data=fig_lojas_os_ref, use_container_width=True)

        with col3:
            # --- GRÁFICO 03 ---
            fig_lojas_pct_custo = dataviz.plot_bar_chart(df=df_agg_loja, x_axis='LOJA', y_axis='%', color_axis='LOJA',
                                                         title_text='Custo percentual por LOJA',
                                                         text_format=".2%")

            bar_chart = st.plotly_chart(
                figure_or_data=fig_lojas_pct_custo, use_container_width=True)

        # ================
        # --- SEÇÃO 04 ---
        # ================
        st.header("Seção 04 - Por VENDEDOR/LOJA")

        # --- DATAFRAME ---
        df_agg_vendedor = dataviz.aggregate_df(
            dataframe=df_filtered, columns_by=['LOJA', 'VENDEDOR'])

        col1, col2, col3 = st.columns(3)
        with col1:
            # --- GRÁFICO 01 ---
            fig_lojas_vendedores_vendas = dataviz.plot_bar_chart(df=df_agg_vendedor, x_axis='VENDEDOR', y_axis='VALOR VENDA', color_axis='LOJA',
                                                                 title_text='VENDAS por VENDEDOR/LOJA', text_format=".2s")

            bar_chart = st.plotly_chart(
                figure_or_data=fig_lojas_vendedores_vendas, use_container_width=True)

        with col2:
            # --- GRÁFICO 02 ---
            fig_lojas_vendedores_custo = dataviz.plot_bar_chart(df=df_agg_vendedor, x_axis='VENDEDOR', y_axis='Custo Total', color_axis='LOJA',
                                                                title_text='CUSTOS por VENDEDOR/LOJA', text_format=".2s")
            bar_chart = st.plotly_chart(
                figure_or_data=fig_lojas_vendedores_custo, use_container_width=True)

        with col3:
            # --- GRÁFICO 03 ---
            fig_lojas_vendedores_mkup = dataviz.plot_bar_chart(df=df_agg_vendedor, x_axis='VENDEDOR', y_axis='MKP', color_axis='LOJA',
                                                               title_text='MARKUP Médio por VENDEDOR/LOJA', text_format=".2s")
            bar_chart = st.plotly_chart(
                figure_or_data=fig_lojas_vendedores_mkup, use_container_width=True)

        # --- CRIANDO SUBPLOTS ---
        # Cria os subplots para passa-los de uma vez para a função de conversão para HTML
        fig_subplots = make_subplots(rows=5, cols=3)
        # --- SESSÃO 01 ---
        fig_subplots.add_trace(fig_datas_vendas.data[0], row=1, col=1)
        fig_subplots.add_trace(fig_data_custos.data[0], row=1, col=2)
        fig_subplots.add_trace(fig_data_markup.data[0], row=1, col=3)
        # --- SESSÃO 02 ---
        fig_subplots.add_trace(fig_lojas_venda.data[0], row=2, col=1)
        fig_subplots.add_trace(fig_lojas_custo.data[0], row=2, col=2)
        fig_subplots.add_trace(fig_lojas_mkup.data[0], row=2, col=3)
        # --- SESSÃO 03 ---
        fig_subplots.add_trace(fig_lojas_os.data[0], row=3, col=1)
        fig_subplots.add_trace(fig_lojas_os_ref.data[0], row=3, col=2)
        fig_subplots.add_trace(fig_lojas_pct_custo.data[0], row=3, col=3)
        # --- SESSÃO 04 ---
        fig_subplots.add_trace(fig_lojas_vendedores_vendas.data[0], row=4, col=1)
        fig_subplots.add_trace(fig_lojas_vendedores_custo.data[0], row=4, col=2)
        fig_subplots.add_trace(fig_lojas_vendedores_mkup.data[0], row=4, col=3)

        # --- SESSÃO DE DOWNLOAD DO HTML---
        st.markdown("---")
        st.subheader("Download")
        # Gerando o arquivo
        dataviz.generate_html_download_link(fig=fig_subplots)
