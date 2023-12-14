# --- CONEXOES COM O GSHEETS ---
import pandas as pd
import streamlit as st
# pip install st-gsheets-connection
from streamlit_gsheets import GSheetsConnection

# --- UPDATE DE INFORMAÇÕES ---
# Abordagem é melhor para fazer um append do que utilizar a conexão padrão do Streamlit
# Pela conexão padrão seria necessário fazer um append do DataFrame inteiro com o registro que se quer adicionar
import os
from dotenv import load_dotenv    # pip install python-dotenv
import gspread


# --- AUXILIARES ---
import constants

# --- CONEXAO VIA GSPREAD ---
# Parte utilizada para update de Dados (somente) ---
# Carregando a variavel de ambiente
load_dotenv(".env")
SPREADSHEET_STR = os.getenv("GSHEETS_NOME_PLANILHA")

# --- CONEXAO PADRAO DO STREAMLIT ---
# Criando uma conexão com o Google Sheets
conn = st.connection(name="gsheets", type=GSheetsConnection)


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def load_data(tabela=constants.TABELAS_GSHEETS[0]):
    '''Cria uma conexão com a planilha e retorna um dataframe com base na tabela especificada.
    Parametros:
    tabela (str) nome da tabela (default='Formulario')
    '''
    # # Criando a conexão com Google Sheets
    # conn = st.connection(name="gsheets", type=GSheetsConnection)

    # Lendo a planilha especificada no parametro da função
    df = conn.read(worksheet=tabela)  # , ttl=0)
    # Retirando os registros em branco
    df = df.dropna(how='all')
    # Criando uma cópia
    df = df.copy()

    return df


def get_store_by_user():
    # Retendo nome do usuário logado
    user_name = st.session_state["name"]
    # Dividindo a string usando o separado "_"
    parts = user_name.split('_')
    # Pegar a parte após o primeiro "_"
    store = [parts[1] if len(parts) > 1 else user_name]

    return store


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_headers_list(tabela):
    # Retorna um dataframe com base no nome da planilha
    df = load_data(tabela)
    headers_list = df.columns.to_list()

    return headers_list


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_form_fields(exclude_extra_cols=False):
    # Chamando a função para retornar uma lista com todos os cabeçalhos
    header_list = get_headers_list(tabela=constants.TABELAS_GSHEETS[0])

    if exclude_extra_cols:
        # Lista com os cabeçalhos a excluir
        cols_to_exclude = ["IsActive?", "user", "modified"]
        # List comprehension p/ retornar uma lista somente com os cabeçalhos desejados
        filtered_headers = [col for col in header_list if col not in cols_to_exclude]
    else:
        filtered_headers = header_list

    return filtered_headers


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_options_list(tabela):
    '''Retorna uma lista com as opções de acordo com a tabela auxiliar especificada.'''

    # Chamando a função para retornar um dataframe com base no nome da planilha
    df = load_data(tabela)
    # filtrando o dataframe pelo nome da tabela/coluna
    # # nome da tabela e coluna são os mesmos, facilitando o filtro
    options_list = df[tabela].tolist()

    return options_list


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_vendors_options_list(loja):
    '''Retorna uma lista com as opções de vendedores baseado na loja escolhida.'''

    # Chamando a função para retornar um dataframe com base no nome da planilha 'VENDEDOR'
    df = load_data(tabela='VENDEDOR')
    # Filtrar o dataframe de vendedores com base na loja escolhida
    df_filtered = df[df['LOJA'] == loja]
    # Transformando em uma lista
    vendors_options_list = df_filtered['VENDEDOR'].tolist()

    return vendors_options_list


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_quality_options_list(tipo_lente):
    '''Retorna uma lista com as opções de vendedores baseado na loja escolhida.'''

    # Chamando a função para retornar um dataframe com base no nome da planilha 'QUALIDADE'
    df = load_data(tabela='QUALIDADE')
    # Filtrar o dataframe de vendedores com base na loja escolhida
    df_filtered = df[df['TIPO LENTE'] == tipo_lente]
    # Transformando em uma lista
    quality_options_list = df_filtered['QUALIDADE'].tolist()

    return quality_options_list


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_mandatory_fields():
    '''Retorna uma lista de campos obrigatorios de acordo com a Planilha OBRIGATORIOS'''

    # Carrega os dados da planilha OBRIGATORIOS
    df_mandatory = load_data(tabela="OBRIGATORIOS")
    # Ajusta a coluna para uma lista
    df_mandatory = df_mandatory["OBRIGATORIOS"].tolist()

    return df_mandatory


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_unique_orders():
    '''Retorna uma lista de valores unicos da coluna 'OS' da planilha 'Formulario'.'''

    # Carrega os dados da planilha Formulario
    df = load_data(tabela="Formulario")

    # Filtrando somente os registros ativos
    df_filtered = df[(df['IsActive?'] == 1) |
                     (df['IsActive?'] == "VERDADEIRO") |
                     (df['IsActive?'] == True)]
    
    # Obtendo a loja logada
    loja_logada = get_store_by_user()
    
    # Filtrando somente os registros da loja logada
    df_filtered = df_filtered[ (df_filtered['LOJA'] == loja_logada[0]) ]
    
    # Obtem os valores unicos da coluna 'OS'
    # Incluida ordenação de forma ascendente
    unique_orders = df_filtered['OS'].sort_values(ascending=True).unique()

    return unique_orders


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_unique_orders_ref(unique_orders):
    '''Retorna uma lista de valores unicos da coluna 'OS Ref' da planilha 'Formulario'.'''

    # Carrega os dados da planilha Formulario
    df = load_data(tabela="Formulario")

    # Filtrando somente os registros ativos
    df_filtered = df[(df['IsActive?'] == 1) |
                     (df['IsActive?'] == "VERDADEIRO") |
                     (df['IsActive?'] == True)]

    # Filtra somente as OS passadas no parametro e retorna somente a coluna 'OS REF'
    df_filtered = df_filtered[df_filtered['OS'] == unique_orders]['OS REF'].unique()

    return df_filtered


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_unique_clients():
    '''Retorna uma lista de clientes únicos da planilha 'Formulario'.'''

    # Carrega os dados da planilha Formulario
    df = load_data(tabela="Formulario")

    # Retorna uma lista dos clientes unicos
    unique_clients = df['CLIENTE'].unique()

    return unique_clients


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def get_df_by_orders(unique_orders, unique_orders_ref):
    '''Filtra o Dataframe original de acordo com os parametros de Ordem de Serviço passados.
        Utilizado no formulario de Atualização.'''

    # Importando o Database
    df = load_data(tabela="Formulario")

    # Filtra o dataframe de acordo com os parametros
    #   Via filtro padrão do Pandas
    df_filtered = df[(df['OS'] == unique_orders) &
                     (df['OS REF'] == unique_orders_ref)]

    # Filtrando somente os registros ativos
    df_filtered = df_filtered[(df_filtered['IsActive?'] == 1) |
                              (df_filtered['IsActive?'] == "VERDADEIRO") |
                              (df_filtered['IsActive?'] == True)]

    # #  Via query SQL
    # sql = f'SELECT * FROM "Formulario" WHERE "OS" = {unique_orders} AND "OS REF" = {unique_orders_ref}'
    # df_filtered = conn.query(sql=sql, ttl=0)

    return df_filtered


@st.cache_data(ttl=constants.TIME_TO_LIVE)
def insert_record_by_df_update(dataframe, tabela=constants.TABELAS_GSHEETS[0]):
    '''Insere um registro na planilha do GSheets.
    Parâmetros:
    - dataframe (pd.DataFrame): DataFrame contendo os dados a serem inseridos.
    - tabela (str): Nome da tabela (default='Formulario').
    '''
    # Conecta ao Google Sheets
    # conn = st.connection(name="gsheets", type=GSheetsConnection)
    # DataFrame existente
    existing_df = load_data(tabela=tabela)
    # Fazendo um append no DataFrame existente com novos registros (parametro dataframe)
    updated_df = pd.concat([existing_df, dataframe], ignore_index=True)
    # Inserir registro (atualiza o registro concatenando com o existente)
    conn.update(worksheet=tabela, data=updated_df)
    # # Limpa o cache
    # st.cache_data.clear()


def insert_new_row(dataframe, worksheet=constants.TABELAS_GSHEETS[0]):
    '''Insere uma nova linha na planilha utilizando gspread.'''

    # --- GERANDO CONEXAO/AUTORIZAÇÃO ---
    # Carregando as credenciais do segredos do streamlit
    gcp_service_account_info = st.secrets["connections"]["gsheets"]
    # Buscando autorização via gspread com a variavel dos segredos
    gc = gspread.service_account_from_dict(gcp_service_account_info)
    # Abrir a planilha desejada
    spreadsheet = gc.open(SPREADSHEET_STR)
    # Buscar a aba desejada
    worksheet = spreadsheet.worksheet(worksheet)
    # Transformando os valores em uma lista
    rows_to_insert = dataframe.values.tolist()
    # Retendo o primeiro registro
    # rows_to_insert  = rows_to_insert [0]

    # Iterando sobre cada registro
    # Apenas por precaução (teoricamente só teria 01)
    for row in rows_to_insert:
        # Inserindo o registro
        worksheet.append_row(row)


def change_dtypes(dataframe):
    # Convertendo os dados de procura ('OS' e 'OS REF')
    dataframe['OS'] = dataframe['OS'].astype(float)
    dataframe['OS REF'] = dataframe['OS REF'].astype(str)
    # # Convertendo dado de insercao
    # dataframe['IsActive?'] = dataframe['IsActive?'].astype(bool)
    # Fazendo uma copia
    dataframe = dataframe.copy()

    return dataframe


def check_record_exist(record, tabela=constants.TABELAS_GSHEETS[0]):
    '''Retorna True/False caso exista registro com a mesma OS e OS REF.'''

    # Importando a base
    df = load_data(tabela="Formulario")

    # Valores procurados
    os_record = record['OS'][0]
    os_ref_record = record['OS REF'][0]

    # Filtra o dataframe de acordo com os parametros
    df_filtered = df[(df["OS"] == os_record) & (df["OS REF"] == os_ref_record)]

    # Numero de registros com a mesma OS e OS REF
    n_matches = len(df_filtered)

    # Se encontrado registros correspondentes
    if n_matches > 0:
        # Exibe mensagem final
        st.error(
            '''Não foi possível incluir o cadastro pois já consta o número desta OS.''')
        # Exibe a mensagem com os números
        if n_matches > 1:
            st.warning(
                f'''Foram encontrados {n_matches} registros referente a OS {os_record} e OS REF {os_ref_record}.''')
        else:
            st.warning(
                f'''Foi encontrado {n_matches} registro referente a OS {os_record} e OS REF {os_ref_record}.''')

        # Exibe os registros iguais
        # st.dataframe(match_records)
        st.dataframe(df_filtered.iloc[:, :-3])

        return True
    else:
        return False


def change_record_status(df_to_change, tabela=constants.TABELAS_GSHEETS[0]):
    '''Altera a coluna 'is_active? para False (coluna flag).'''

    # Carregando a base de dados existente
    existing_df = load_data(tabela)

    # Forçando a conversão para String (evita erro na comparação)
    existing_df['OS REF'] = existing_df['OS REF'].astype(str)

    # Fazendo uma cópia do registro
    record = df_to_change.copy()
    # Valores procurados
    os_record = record['OS'][0]
    os_ref_record = record['OS REF'][0]

    # Filtra o dataframe de acordo com os parametros
    record_to_change = existing_df[(existing_df["OS"] == os_record) & (
        existing_df["OS REF"] == str(os_ref_record))]
    index_to_change = record_to_change.index

    # Localizando o registro específico na base e alterando o status
    existing_df.loc[index_to_change, 'IsActive?'] = "FALSO"

    # Atualizando a planilha com o DataFrame modificado
    conn.update(worksheet=tabela, data=existing_df)


def exclude_record(df_to_change, tabela=constants.TABELAS_GSHEETS[0]):
    '''Altera a coluna 'is_active? para False (coluna flag).'''

    # Carregando a base de dados existente
    existing_df = load_data(tabela)

    # Resetando o índice para garantir que os DataFrames tenham o mesmo índice
    existing_df = existing_df.reset_index(drop=True)

    # Forçando a conversão para String (evita erro na comparação)
    existing_df['OS REF'] = existing_df['OS REF'].astype(str)

    # Fazendo uma cópia do registro
    record = df_to_change.copy()
    # Resetando o índice para garantir que os DataFrames tenham o mesmo índice
    record = record.reset_index(drop=True)

    # Valores procurados
    os_record = record["OS"][0]
    os_ref_record = record['OS REF'][0]

    # Filtra o dataframe de acordo com os parametros
    record_to_change = existing_df[(existing_df["OS"] == os_record) &
                                   (existing_df["OS REF"] == str(os_ref_record))]

    index_to_change = record_to_change.index

    # Localizando o registro específico na base e alterando o status
    existing_df.loc[index_to_change, 'IsActive?'] = "FALSO"

    # Atualizando a planilha com o DataFrame modificado
    conn.update(worksheet=tabela, data=existing_df)
