# --- FUNÇÕES AUXILIARES ---

import pandas as pd
import streamlit as st
from datetime import datetime
import getpass                  # p/ buscar usuário
import pytz                     # pip install pytz (timezone)

# --- AUXILIARES ---
import constants
import forms
import db_connection
import calculations


# --- USUARIO ---
def get_system_username():
    '''Retorna o usuário do sistema.'''
    return getpass.getuser()


# --- SESSOES ---
def reset_session_state():
    '''Deleta todos os itens da sessao. Util para checagem os campos do formulario após o submit.'''
    for key in st.session_state.keys():
        del st.session_state[key]


# --- LIMPEZA ---
def process_text(input_text, capitalize_first=True, remove_all_spaces=True):
    '''Função para tratamento dos campos de texto
    01 - Remove os espaços extras
    02 - Coloca a primeira letra em maiusculo (opcional)
    03 - Remove todos os espaços (opcional).'''

    if input_text != None:
        # Remove espaços extras
        processed_text = ' '.join(word.strip() for word in input_text.split())

        if capitalize_first:
            # Capitaliza as primeiras letras
            processed_text = ' '.join(word.capitalize()
                                      for word in processed_text.split())

        if remove_all_spaces:
            # Remove todos os espaços
            processed_text = processed_text.replace(" ", "")

    else:
        processed_text = None

    return processed_text


# --- VALIDAÇÕES ---
def validate_mandatory_fields():
    '''Valida se os campos obrigatorios foram preenchidos.'''

    # Chamando a função para retornar os campos obrigatórios
    campos_obrigatorios = db_connection.get_options_list("OBRIGATORIOS")
    # Lista vazia para preenchimento dos campos obrigatórios não preenchidos.
    missing_fields = []
    # Iterando sobre os campos mandatórios
    for obrigatorio in campos_obrigatorios:
        # Obtendo o valor do campo
        field_value = st.session_state.get(obrigatorio, None)
        # Checando se o campo está vazio
        if not field_value:
            # if not field_value:
            missing_fields.append(field_value)

    # Se possuir campos vazios
    if len(missing_fields) > 0:
        # Mostra um resumo dos campos não preenchidos e retorna False
        st.error(
            body="Alguns campos obrigatórios não foram preenchidos. Favor preenche-los antes de submeter.")
        return False
    else:
        # st.success(body="Registro efetuado com sucesso.")
        return True


# --- RESUMOS ---
def mandatory_fields_summary():
    '''Retorna um resumo dos campos obrigatórios preenchidos ou não.'''

    # Chamando a função para retornar os campos obrigatórios
    campos_obrigatorios = db_connection.get_options_list("OBRIGATORIOS")

    resumo = ""
    for obrigatorio in campos_obrigatorios:
        # Obtendo o valor do campo
        field_value = st.session_state.get(obrigatorio, None)
        # Checando se o campo está vazio
        if field_value is not None or field_value:
            resumo += f"- **{obrigatorio}:** {field_value} :white_check_mark:\n"
        else:
            resumo += f"- **{obrigatorio}:** {field_value} :x:\n"

    fields_summary = st.markdown(resumo)

    return fields_summary


def values_fields_summary():
    '''Retorna um resumo dos valores numericos (KPIs + Custos discriminados)'''
    # --- TABS ---
    tab1, tab2 = st.tabs(["KPIs", "Custos"])
    # Separações de Abas
    with tab1:
        # Metricas
        calculations.get_kpi_metrics()

    with tab2:
        # DataFrame com os Custos Discriminados
        df_custos = calculations.get_costs_summary()
        st.dataframe(df_custos)


def create_comparison_df(df_from, df_to):
    '''Cria um Dataframe de comparação entre os registros atuais e o registro atualizado.'''

    # Adiciona rótulos 'DE' e 'PARA' aos indice
    df_from.index = ['DE']
    df_to.index = ['PARA']

    # Concatena os 02 Dataframes (FROM/TO)
    # Omite as 03 ultimas colunas
    df_comparison = pd.concat([df_from.iloc[:, :-3], df_to.iloc[:, :-3]])
    # Transpondo o Dataframe
    df_comparison = df_comparison.T
    # Remove espaços extras nas colunas 'DE' e 'PARA'
    df_comparison['DE'] = df_comparison['DE'].apply(
        lambda x: x.strip() if isinstance(x, str) else x)
    df_comparison['PARA'] = df_comparison['PARA'].apply(
        lambda x: x.strip() if isinstance(x, str) else x)
    # Converte a coluna 'OS REF' para float64
    df_comparison['DE']['OS REF'] = pd.to_numeric(
        df_comparison['DE']['OS REF'], errors='coerce')
    df_comparison['PARA']['OS REF'] = pd.to_numeric(
        df_comparison['PARA']['OS REF'], errors='coerce')
    # Substituindo NaN por string vazia
    # Alguns valores numericos podem vir como NaN nao comparando corretamente
    df_comparison = df_comparison.fillna('')

    # --- COMPARAÇÃO
    # Todo o Dataframe
    df_is_equal = df_comparison['DE'].equals(df_comparison['PARA'])

    # Linha a Linha - Adiciona uma coluna marcando quando são diferentes
    df_comparison['Alterado?'] = (df_comparison['DE'] != df_comparison['PARA'])
    # Exibe o Dataframe comparativo
    st.dataframe(df_comparison)
    # Retorna True ou False p/ mostrar se há alguma diferença
    return df_is_equal


# --- PRE-PROCESSAMENTO ---
def create_dataframe_from_session(is_active="VERDADEIRO"):
    '''Cria um Dataframe com os campos do formulario.'''

    # --- ATRIBUINDO AS SESSOES ---
    # Campos Formulário
    loja = st.session_state[forms.header_list[0]]
    tipo = st.session_state[forms.header_list[1]]
    ordem_servico = st.session_state[forms.header_list[2]]
    ordem_servico_ref = st.session_state[forms.header_list[3]]
    fornecedor = st.session_state[forms.header_list[4]]
    tipo_lente = st.session_state[forms.header_list[5]]
    qualidade = st.session_state[forms.header_list[6]]
    lente = st.session_state[forms.header_list[7]]
    valor_venda = st.session_state[forms.header_list[8]]
    valor_lente = st.session_state[forms.header_list[9]]
    # Break - Campos Calculados
    vendedor = st.session_state[forms.header_list[16]]
    cliente = st.session_state[forms.header_list[17]]
    data_venda = st.session_state[forms.header_list[18]]
    data_entrega = st.session_state[forms.header_list[19]]
    data_pedido = st.session_state[forms.header_list[20]]
    data_lente = st.session_state[forms.header_list[21]]
    data_montagem = st.session_state[forms.header_list[22]]
    data_retirada = st.session_state[forms.header_list[23]]
    numero_pedido = st.session_state[forms.header_list[24]]
    os_antiga = st.session_state[forms.header_list[26]]
    observacao = st.session_state[forms.header_list[25]]

    # --- CAMPOS ADICIONAIS CALCULADOS ---
    custo_armacao, custo_montagem, custo_exame = calculations.calculate_additional_costs()
    custo_total = calculations.calculate_total_costs()
    markup = calculations.calculate_markup()
    margem = calculations.calculate_margin()
    # Obtendo o usuário do sistema
    # user = get_system_username()
    # Obtendo usuário logado
    user = st.session_state['username']
    # Obtendo o fuso horário local
    local_timezone = pytz.timezone("America/Sao_Paulo")
    # Criando a data e hora com o fuso horário local
    modified = datetime.now(local_timezone).strftime("%Y-%m-%d %H:%M:%S")

    # --- LIMPEZA / FORMATAÇÃO ---
    #   Limpeza dos campos de texto
    os_ref_clean = process_text(input_text=str(
        ordem_servico_ref), capitalize_first=False, remove_all_spaces=True)
    cliente_clean = process_text(
        input_text=cliente, capitalize_first=True, remove_all_spaces=False)

    #   Formatação das Datas (DD/MM/YYYY)
    data_venda_formatada = (data_venda.strftime(
        '%d/%m/%Y') if data_venda is not None else None)
    data_entrega_formatada = (data_entrega.strftime(
        '%d/%m/%Y') if data_entrega is not None else None)
    data_pedido_formatada = (data_pedido.strftime(
        '%d/%m/%Y') if data_pedido is not None else None)
    data_lente_formatada = (data_lente.strftime(
        '%d/%m/%Y') if data_lente is not None else None)
    data_montagem_formatada = (data_montagem.strftime(
        '%d/%m/%Y') if data_montagem is not None else None)
    data_retirada_formatada = (data_retirada.strftime(
        '%d/%m/%Y') if data_retirada is not None else None)

    # --- DATAFRAME ---
    # Criando um Dicionário com os inputs
    form_data = {
        "LOJA": loja,
        "TIPO": tipo,
        "OS": ordem_servico,
        "OS REF": os_ref_clean,
        "FORNECEDOR": fornecedor,
        "TIPO LENTE": tipo_lente,
        "QUALIDADE": qualidade,
        "LENTE": lente,
        "VALOR VENDA": valor_venda,
        "VLR LENTE + TRAT.": valor_lente,
        "Arm.": custo_armacao,
        "Mont.": custo_montagem,
        "Exame": custo_exame,
        "Custo Total": custo_total,
        "MKP": markup,
        "%": margem,
        "VENDEDOR": vendedor,
        "CLIENTE": cliente_clean,
        "DATA DA VENDA": data_venda_formatada,
        "ENTREGA": data_entrega_formatada,
        "DATA PEDIDO": data_pedido_formatada,
        "DATA LENTE": data_lente_formatada,
        "MONTAGEM": data_montagem_formatada,
        "RETIRADA": data_retirada_formatada,
        "N° PEDIDO": numero_pedido,
        "OBSERVAÇÃO / MOTIVO": observacao,
        "O.S ANTIGA / REF ARMAÇÃO": os_antiga,
        "IsActive?": is_active,
        "user": user,
        "modified": modified
    }
    # Criando um DataFrame
    df_form = pd.DataFrame([form_data])

    return df_form
