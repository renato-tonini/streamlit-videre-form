
# --- MODULO PARA OS CALCULOS E RESUMOS ---
import pandas as pd
import streamlit as st

# --- AUXILIARES ---
import constants
import forms


# --- CALCULOS --- 
def calculate_additional_costs():
    '''
    Retorna os custos adicionais de acordo com a seleção dos Radio Buttons (Armação, Montagem e Exame).
    Valor referenciado por lista de constantes.
    '''
    # Inicializando as variaveis com valor Zero.
    custo_armacao, custo_montagem, custo_exame = 0, 0, 0
    # Verificacao dos inputs do usuario p/ Radio Buttons
    # Dependendo de cada opção ele retorna o respectivo custo baseado nas constantes
    if st.session_state[forms.header_list[10]] == "Sim":
        custo_armacao = constants.VALORES_PADRAO[forms.header_list[10]]
    if st.session_state[forms.header_list[11]] == "Sim":
        custo_montagem = constants.VALORES_PADRAO[forms.header_list[11]]
    if st.session_state[forms.header_list[12]] == "Sim":
        custo_exame = constants.VALORES_PADRAO[forms.header_list[12]]

    return custo_armacao, custo_montagem, custo_exame


def calculate_total_costs():
    '''
    Calcula o valor do Custo Total baseado nos custos fixos (custo_armacao, custo_montagem, custo_exame) + custo_lente.
    '''
    # Chamando a função de custos adicionais
    custo_armacao, custo_montagem, custo_exame = calculate_additional_costs()
    # Buscando o valor inputado pelo usuario na sessao
    custo_lente = st.session_state[forms.header_list[9]]
    if custo_lente == None:
        custo_lente = 0
    # Calculando Custo Total
    custo_total = custo_lente + custo_armacao + custo_montagem + custo_exame
    # Atriubuindo o Custo Total a Sessao
    st.session_state['custo_total'] = custo_total

    return custo_total


def calculate_markup():
    '''Calcula o Markup.'''
    # Chamando a função para retornar o custo total
    custo_total = calculate_total_costs()
    valor_venda = st.session_state[forms.header_list[8]]
    # Verificando se o custo é diferente de zero para evitar erro (divisão por zero)
    if custo_total != 0:
        markup = valor_venda / custo_total
        return markup
    else: # caso o custo seja zero
        return None


def calculate_margin():
    '''Calcula o percentual de venda sobre a lente.'''
    # Chamando a função para retornar o custo total
    valor_venda = st.session_state[forms.header_list[8]]
    custo_lente = st.session_state[forms.header_list[9]]
    if valor_venda != 0:
        margin = custo_lente / valor_venda
        return margin
    else:
        return None


# --- RESUMOS ---
def get_costs_summary():
    '''Retorna um Dataframe com um resumo discriminando os custos.'''

    # Chamando a função de Custos Aadicionais (Armação, Montagem e Exame)
    custo_armacao, custo_montagem, custo_exame = calculate_additional_costs()
    # Buscando o valor inputado pelo usuario na sessao
    custo_lente = st.session_state[forms.header_list[9]]
    if custo_lente == None:
        custo_lente = 0
    # Chamando a função de Custo Total
    custo_total = calculate_total_costs()
    
    # Lista com os itens ref. a Custo
    items = [forms.header_list[10], forms.header_list[11], forms.header_list[12], forms.header_list[9], "Custo Total"]
    # Criando um DataFrame com os Custos
    df_custos = pd.DataFrame({"Custos": [custo_armacao, custo_montagem, custo_exame, custo_lente, custo_total]},
                             columns=["Custos"],
                             index=items)
    # Ajustando o nome do Índice
    df_custos.index.name = "Item"

    return df_custos


def get_kpi_metrics():
    '''Retorna os KPIs Basicos.'''

    # Retendo os valores via sessao ou função
    venda = st.session_state[forms.header_list[8]]
    custo = calculate_total_costs()
    markup = calculate_markup()

    # Checagem básica somente para manter o padrão dos demais campos
    if custo == 0:
        custo = None

    # Definindo uma base target p/ markup e o delta
    markup_target = 4
    try:
        delta_markup = markup - markup_target
    except:
        delta_markup = None

    # Formatando os valores com duas casas decimais e o símbolo da moeda
    venda_formatted = f"R$ {venda:.2f}" if venda is not None else None
    custo_formatted = f"R$ {custo:.2f}" if custo is not None else None
    markup_formatted = f"{markup:.2f}" if markup is not None else None
    delta_markup_formatted = f"{delta_markup:.2f}" if delta_markup is not None else None
    help_markup = "Markup abaixo do mínimo desejado" if (markup is not None and markup < 4) else None

    # # Centralizando os KPIs
    # st.write("<h2 style='text-align: center;'>KPIs Centrais</h2>", unsafe_allow_html=True)

    # # Lendo o arquivo css
    # with open("kpis_style.css") as f:
    #     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Separando as colunas
    col1, col2, col3= st.columns(3)
    # Definindo as metricas
    kpi_venda = col1.metric(label="Valor Venda", value=venda_formatted)
    kpi_custo = col2.metric(label="Valor Custo", value=custo_formatted)
    kpi_markup = col3.metric(label="Markup", value=markup_formatted, delta=delta_markup_formatted, help=help_markup)
