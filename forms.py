# --- CRIAÇÃO DOS FORMULARIOS ---

import pandas as pd
import streamlit as st

# --- AUXILIARES ---
import constants
import utils
import db_connection


# --- CONSTANTES FORMULARIOS ---
# Constante para indicar os campos obrigatórios
OBRIGATORIO = " (*)"
HELP = "Campo Obrigatório"


# --- CHAVES DOS FORMULARIOS ---
# Dicionario com as 'chave/valor' dos formularios
FORMS_KEY = {
    1: "Cadastro",
    2: "Atualização",
    3: "Exclusão",
    4: "Consulta"
}


# --- VALORES MAXIMOS ---
# Dicionario com os valores máximos dos campos numéricos
VALORES_MAXIMOS = {
    'VALOR VENDA': 5000.,
    'VALOR LENTE': 500.
}

# --- CABECALHOS DO FORMULARIO ---
# Chamando a função para obter os cabeçalhos da Planilha Formulario
header_list = db_connection.get_form_fields(exclude_extra_cols=False)


# --- DEFININDO AS OPÇÕES (SELECT BOX)---
# Chamando as funções com base na constante referente ao nome da planilha
# opcoes_lojas = db_connection.get_options_list(tabela=constants.TABELAS_GSHEETS[1])
# opcoes_lojas = db_connection.get_store_by_user()

opcoes_tipo = db_connection.get_options_list(tabela=constants.TABELAS_GSHEETS[2])
opcoes_fornecedor = db_connection.get_options_list(tabela=constants.TABELAS_GSHEETS[3])
opcoes_tipo_lente = db_connection.get_options_list(tabela=constants.TABELAS_GSHEETS[4])
opcoes_lente = db_connection.get_options_list(tabela=constants.TABELAS_GSHEETS[6])


# --- NOVO CADASTRO ---
def create_register_form():
    '''Retorna um formulário de INCLUSÃO de registros com os respectivos campos.'''

    # ---TITULOS---
    st.header(body="Formulário de Cadastro")
    st.write("Preencha os campos abaixo para realizar um novo cadastro:")

    # --- EXPANSOR LOJA/TIPO LENTE (DROPDOWNS CONDICIONAIS) ---
    # Necessário retirar do Formulario os condicionais para reter os valores destes
    with st.expander("Selecione as opções abaixo:", expanded=True):
        
        # Retem a Loja baseado no usuário do login
        opcoes_lojas = db_connection.get_store_by_user()

        # Separada a LOJA para funcionar a seleção condicional com o VENDEDOR
        loja = st.selectbox(label=header_list[0] + OBRIGATORIO, options=opcoes_lojas,
                            placeholder="Escolha a Loja", index=0, help=HELP, key=header_list[0], disabled=True)

        # Separada a TIPO LENTE para funcionar a seleção condicional com o QUALIDADE
        tipo_lente = st.selectbox(label=header_list[5] + OBRIGATORIO, options=opcoes_tipo_lente,
                                  placeholder="Escolha o tipo de Lente", index=None, help=HELP, key=header_list[5])

    # --- INICIALIZANDO O FORMULARIO ---
    with st.form(key=FORMS_KEY[1], clear_on_submit=False):

        # Inicio dos Campos
        tipo = st.selectbox(label=header_list[1] + OBRIGATORIO, options=opcoes_tipo,
                            placeholder="Escolha o Tipo de Transação", index=None, help=HELP, key=header_list[1])

        ordem_servico = st.number_input(label=header_list[2] + OBRIGATORIO, value=None,
                                        placeholder="Insira o número da Ordem de Serviço", min_value=0, help=HELP, key=header_list[2])

        ordem_servico_ref = st.text_input(label=header_list[3] + OBRIGATORIO, value=None,
                                          placeholder="Insira a Ordem de Serviço Ref", help=HELP, key=header_list[3])

        fornecedor = st.selectbox(label=header_list[4] + OBRIGATORIO, options=opcoes_fornecedor,
                                  placeholder="Escolha qual o Fornecedor", index=None, help=HELP, key=header_list[4])

        # --- FILTRO QUALIDADE ---
        if tipo_lente:
            # Retorna uma lista com a opçoes de qualidade de acordo com a lente escolhida
            opcoes_qualidade = db_connection.get_quality_options_list(
                tipo_lente)
            # Selectbox com as opções da lente escolhida
            qualidade = st.selectbox(label=header_list[6], options=opcoes_qualidade,
                                     placeholder="Escolha a Qualidade da Lente", index=None, key=header_list[6])

        lente = st.selectbox(label=header_list[7] + OBRIGATORIO, options=opcoes_lente,
                             placeholder="Escolha a Qualidadde da Lente", index=None, help=HELP,  key=header_list[7])

        # Valores numericos
        valor_venda = st.number_input(label=header_list[8] + OBRIGATORIO, step=1., value=None, placeholder="Insira o valor da venda",
                                      format="%0.2f", min_value=0., max_value=VALORES_MAXIMOS['VALOR VENDA'], help=HELP, key=header_list[8])

        valor_lente = st.number_input(label=header_list[9] + OBRIGATORIO, step=1., value=None, placeholder="Insira o valor da lente",
                                      format="%0.2f", min_value=0., max_value=VALORES_MAXIMOS['VALOR LENTE'], help=HELP, key=header_list[9])

        # --- RADIO BUTTONS ---
        armacao = st.radio(label="Incluir Custo de Armação?" + OBRIGATORIO,
                           options=['Sim', 'Não'], index=None, help=HELP, key=header_list[10], horizontal=True)

        montagem = st.radio(label="Incluir Custo de Montagem?" + OBRIGATORIO,
                            options=['Sim', 'Não'], index=None, help=HELP, key=header_list[11], horizontal=True)

        exame = st.radio(label="Incluir Custo de Exame?" + OBRIGATORIO,
                         options=['Sim', 'Não'], index=None, help=HELP, key=header_list[12], horizontal=True)

        # --- FILTRO VENDEDOR ---
        # Chamando a função para retornar um dataframe com base no nome da planilha 'VENDEDOR'
        if loja:
            # Retorna uma lista de vendedores desta loja
            opcoes_vendedor = db_connection.get_vendors_options_list(loja)
            # Utiliza as opções da loja selecionada para incluir somente vendedores da respectiva loja
            vendedor = st.selectbox(label=header_list[16] + OBRIGATORIO, options=opcoes_vendedor,
                                    placeholder="Escolha o Vendedor", index=None, help=HELP, key=header_list[16])

        cliente = st.text_input(label=header_list[17] + OBRIGATORIO, value=None,
                                placeholder="Insira o nome completo do cliente", help=HELP, key=header_list[17])

        # --- DATAS ---
        # Coluna para a 1a Seção de Datas
        col1, col2 = st.columns(2)
        # Campos Seção 01
        data_venda = col1.date_input(
            label=header_list[18], format=constants.DATE_FORMAT, key=header_list[18])

        data_entrega = col2.date_input(
            label=header_list[19], format=constants.DATE_FORMAT, value=None, key=header_list[19])

        # Coluna para a 2a Seção de Datas
        col3, col4 = st.columns(2)
        # Campos Seção 02
        data_pedido = col3.date_input(
            label=header_list[20], format=constants.DATE_FORMAT, value=None, key=header_list[20])
        data_lente = col4.date_input(
            label=header_list[21], format=constants.DATE_FORMAT, value=None, key=header_list[21])

        # Coluna para a 3a Seção de Datas
        col5, col6 = st.columns(2)
        # Campos Seção 03
        data_montagem = col5.date_input(
            label=header_list[22], format=constants.DATE_FORMAT, value=None, key=header_list[22])
        data_retirada = col6.date_input(
            label=header_list[23], format=constants.DATE_FORMAT, value=None, key=header_list[23])

        # Demais Campos
        numero_pedido = st.number_input(label=header_list[24], value=None,
                                        placeholder="Insira o número do pedido", min_value=0, key=header_list[24])

        os_antiga = st.text_input(label=header_list[26],
                                  placeholder="Insira a OS  Antiga", key=header_list[26])

        observacao = st.text_area(label=header_list[25], height=20,
                                  placeholder="Insira suas observações aqui", key=header_list[25])

        # Campo obrigatorio
        mandatory = st.markdown("<p style='font-size: 13px;'> <em>* Campos obrigatórios</em> </p>",
                                unsafe_allow_html=True)

        # --- SUBMIT BUTTON ---
        submit_button = st.form_submit_button("Submeter Cadastro")

    return submit_button


# --- ATUALIZAÇÃO ---
def create_update_form():
    '''Retorna um formulário de ATUALIZAÇÃO de registros com os respectivos campos.'''

    # ---TITULOS---
    st.header(body="Atualização de Cadastro")

    # # --- EXPANSOR TODOS REGISTROS ---
    # with st.expander(label="Registros atuais"):
    #     # Carrega os registros atuais
    #     df = db_connection.load_data()
    #     # Mostra em um dataframe
    #     st.dataframe(df)

    # --- EXPANSOR SELEÇÃO OS ---
    with st.expander(label="Ordem de Serviço:", expanded=True):

        # Retem a Loja baseado no usuário do login
        opcoes_lojas = db_connection.get_store_by_user()
        loja = st.selectbox(label=header_list[0] + OBRIGATORIO, options=opcoes_lojas, index=0,
                            placeholder="Escolha a Loja", help=HELP, key=header_list[0], disabled=True)
        
        # Retorna os valores unicos das OSs com base na Loja do Login
        opcoes_ordem_servico = db_connection.get_unique_orders()

        ordem_servico = st.selectbox(label=header_list[2] + OBRIGATORIO, placeholder="Escolha a Ordem de Serviço desejada", index=None,
                                     help=HELP, options=opcoes_ordem_servico, key=header_list[2])
        
        # Retorna os valores unicos das OS Ref baseado na OS selecionada com base na Loja do Login
        opcoes_ordem_servico_ref = db_connection.get_unique_orders_ref(ordem_servico)
        ordem_servico_ref = st.selectbox(label=header_list[3] + OBRIGATORIO, placeholder="Escolha a Ordem de Serviço Ref desejada", index=None,
                                         help=HELP, options=opcoes_ordem_servico_ref, key=header_list[3])

        if ordem_servico and ordem_servico_ref:

            # Filtra o Dataframe de acordo com a Ordem de Serviço ('OS' e 'OS REF')
            df_from = db_connection.get_df_by_orders(loja=opcoes_lojas[0], unique_orders=ordem_servico, unique_orders_ref=ordem_servico_ref)

            # Mostrando o Registro (omite as 03 ultimas colunas do usuario)
            st.write("Registro:")
            st.dataframe(df_from.iloc[:, :-3])

            registro_tipo_lente = df_from['TIPO LENTE'].values
            idx_tipo_lente = opcoes_tipo_lente.index(registro_tipo_lente[0])
            tipo_lente = st.selectbox(label=header_list[5] + OBRIGATORIO, options=opcoes_tipo_lente, index=idx_tipo_lente,
                                      placeholder="Escolha o tipo de Lente", help=HELP, key=header_list[5])

            # --- INICIALIZANDO O FORMULARIO ---
            with st.form(key=FORMS_KEY[2], clear_on_submit=False):

                # --- INICIO DOS CAMPOS ---

                # Busca o índice do registro p/ default dos dropdowns
                registro_tipo = df_from['TIPO'].values
                idx_tipo = opcoes_tipo.index(registro_tipo[0])
                tipo = st.selectbox(label=header_list[1] + OBRIGATORIO, options=opcoes_tipo, index=idx_tipo,
                                    placeholder="Escolha o tipo de Lente", help=HELP, key=header_list[1])

                registro_fornecedor = df_from['FORNECEDOR'].values
                idx_fornecedor = opcoes_fornecedor.index(
                    registro_fornecedor[0])
                fornecedor = st.selectbox(label=header_list[4] + OBRIGATORIO, options=opcoes_fornecedor, index=idx_fornecedor,
                                          placeholder="Escolha qual o Fornecedor", help=HELP, key=header_list[4])

                registro_lente = df_from['LENTE'].values
                idx_lente = opcoes_lente.index(registro_lente[0])
                lente = st.selectbox(label=header_list[7] + OBRIGATORIO, options=opcoes_lente, index=idx_lente,
                                     placeholder="Escolha a qualidade da Lente", help=HELP,  key=header_list[7])

                # Valores numericos
                registro_valor_venda = df_from['VALOR VENDA'].values
                valor_venda = st.number_input(label=header_list[8] + OBRIGATORIO, step=1., value=float(registro_valor_venda[0]),
                                              placeholder="Insira o valor da venda", format="%0.2f",
                                              min_value=0., max_value=VALORES_MAXIMOS['VALOR VENDA'], help=HELP, key=header_list[8])

                registro_valor_lente = df_from['VLR LENTE + TRAT.'].values
                valor_lente = st.number_input(label=header_list[9] + OBRIGATORIO, step=1., value=float(registro_valor_lente[0]),
                                              placeholder="Insira o valor da lente", format="%0.2f",
                                              min_value=0., max_value=VALORES_MAXIMOS['VALOR LENTE'], help=HELP, key=header_list[9])

                # --- FILTRO QUALIDADE ---
                # Retorna uma lista de qualidade das lentes
                opcoes_qualidade = db_connection.get_quality_options_list(
                    tipo_lente)
                # Registro do Tipo de Lente
                registro_tipo_lente = df_from['TIPO LENTE'].values
                # Verifica se o Tipo de Lente escolhido é igual ao do registro
                if tipo_lente == registro_tipo_lente[0]:

                    # Se Multifocal precisa transformar em float
                    if tipo_lente == "MULTIFOCAL":
                        registro_qualidade = float(df_from['QUALIDADE'].values)
                        # Busca o indice dentre as opções pelo registro atual
                        idx_qualidade = opcoes_qualidade.index(
                            registro_qualidade)
                    else:
                        registro_qualidade = df_from['QUALIDADE'].values
                        # Busca o indice dentre as opções pelo registro atual
                        idx_qualidade = opcoes_qualidade.index(
                            registro_qualidade[0])

                    qualidade = st.selectbox(label=header_list[6], options=opcoes_qualidade, index=idx_qualidade,
                                             placeholder="Escolha a qualidade da Lente", key=header_list[6])

                else:  # Alterada a qualidade atual - Retira o parametro de indice
                    qualidade = st.selectbox(label=header_list[6], options=opcoes_qualidade, index=None,
                                             placeholder="Escolha a qualidade da Lente", key=header_list[6])


                # --- RADIO BUTTONS ---

                # --- CUSTO ARMACAO ---
                idx_armacao = ["Sim" if x > 0 else "Não" for x in df_from['Arm.'].values]
                # Ajustando strings de Sim/Não para 0/1 (base options)
                default_armacao = 0 if "Sim" in idx_armacao else 1
                armacao = st.radio(label="Incluir Custo de Armação?" + OBRIGATORIO, index=default_armacao,
                                   options=['Sim', 'Não'],  help=HELP, key=header_list[10], horizontal=True)
                # --- CUSTO MONTAGEM ---
                idx_montagem = ["Sim" if x >
                                0 else "Não" for x in df_from['Mont.'].values]
                default_montagem = 0 if "Sim" in idx_montagem else 1
                montagem = st.radio(label="Incluir Custo de Montagem?" + OBRIGATORIO, index=default_montagem,
                                    options=['Sim', 'Não'],  help=HELP, key=header_list[11], horizontal=True)
                # --- CUSTO EXAME ---
                idx_exame = ["Sim" if x >
                             0 else "Não" for x in df_from['Exame'].values]
                default_exame = 0 if "Sim" in idx_exame else 1
                exame = st.radio(label="Incluir Custo de Exame?" + OBRIGATORIO, index=default_exame,
                                 options=['Sim', 'Não'],  help=HELP, key=header_list[12], horizontal=True)

                # --- FILTRO VENDEDOR ---
                # Retorna uma lista de vendedores desta loja
                opcoes_vendedor = db_connection.get_vendors_options_list(loja)
                # Valor do Vendedor no registro atual
                registro_vendedor = df_from['VENDEDOR'].values
                # Registro Loja
                registro_loja = df_from['LOJA'].values
                # Verifica se a loja escolhida é igual ao do registro
                if loja == registro_loja[0]:
                    # Busca o indice dentre as opções pelo registro atual
                    idx_vendedor = opcoes_vendedor.index(registro_vendedor[0])
                    vendedor = st.selectbox(label=header_list[16] + OBRIGATORIO, options=opcoes_vendedor, index=idx_vendedor,
                                            placeholder="Escolha o Vendedor", help=HELP, key=header_list[16])
                else:  # Loja diferente do registro atual
                    # Limpa o selectbox e coloca as opções da nova loja preenchida
                    vendedor = st.selectbox(label=header_list[16] + OBRIGATORIO, options=opcoes_vendedor, index=None,
                                            placeholder="Escolha o Vendedor", help=HELP, key=header_list[16])

                # --- CLIENTE ---
                registro_cliente = df_from['CLIENTE'].values
                cliente = st.text_input(label=header_list[17] + OBRIGATORIO, value=registro_cliente[0],
                                        placeholder="Insira o nome completo do cliente", help=HELP, key=header_list[17])

                # --- DATAS ---
                # Coluna para a 1a Seção de Datas
                col1, col2 = st.columns(2)
                # Campos Seção 01
                # Necessário alguns tratamentos nas Datas
                # --- DATA VENDA ---
                val_data_venda = df_from['DATA DA VENDA'].values
                val_data_venda = pd.to_datetime(
                    val_data_venda, format='%d/%m/%Y', errors='coerce')
                val_data_venda = [val_data_venda[0]
                                  if not pd.isnull(val_data_venda[0]) else None]
                # Input
                data_venda = col1.date_input(label=header_list[18], value=val_data_venda[0],
                                             format=constants.DATE_FORMAT, key=header_list[18])
                # --- DATA ENTREGA ---
                val_data_entrega = df_from['ENTREGA'].values
                val_data_entrega = pd.to_datetime(
                    val_data_entrega, format='%d/%m/%Y', errors='coerce')
                val_data_entrega = [val_data_entrega[0] if not pd.isnull(
                    val_data_entrega[0]) else None]
                # Input
                data_entrega = col2.date_input(label=header_list[19], value=val_data_entrega[0],
                                               format=constants.DATE_FORMAT, key=header_list[19])

                # Coluna para a 2a Seção de Datas
                col3, col4 = st.columns(2)
                # Campos Seção 02
                # Necessário alguns tratamentos nas Datas
                # --- DATA PEDIDO ---
                val_data_pedido = df_from['DATA PEDIDO'].values
                val_data_pedido = pd.to_datetime(
                    val_data_pedido, format='%d/%m/%Y', errors='coerce')
                val_data_pedido = [val_data_pedido[0] if not pd.isnull(
                    val_data_pedido[0]) else None]
                # Input
                data_pedido = col3.date_input(label=header_list[20], value=val_data_pedido[0],
                                              format=constants.DATE_FORMAT,  key=header_list[20])
                # --- DATA LENTE ---
                val_data_lente = df_from['DATA LENTE'].values
                val_data_lente = pd.to_datetime(
                    val_data_lente, format='%d/%m/%Y', errors='coerce')
                val_data_lente = [val_data_lente[0]
                                  if not pd.isnull(val_data_lente[0]) else None]
                # Input
                data_lente = col4.date_input(label=header_list[21], value=val_data_lente[0],
                                             format=constants.DATE_FORMAT, key=header_list[21])

                # Coluna para a 3a Seção de Datas
                col5, col6 = st.columns(2)
                # Campos Seção 03
                # Necessário alguns tratamentos nas Datas
                # --- DATA MONTAGEM ---
                val_data_montagem = df_from['MONTAGEM'].values
                val_data_montagem = pd.to_datetime(
                    val_data_montagem, format='%d/%m/%Y', errors='coerce')
                val_data_montagem = [val_data_montagem[0] if not pd.isnull(
                    val_data_montagem[0]) else None]
                # Input
                data_montagem = col5.date_input(label=header_list[22], value=val_data_montagem[0],
                                                format=constants.DATE_FORMAT, key=header_list[22])
                # --- DATA RETIRADA ---
                val_data_retirada = df_from['RETIRADA'].values
                val_data_retirada = pd.to_datetime(
                    val_data_retirada, format='%d/%m/%Y', errors='coerce')
                val_data_retirada = [val_data_retirada[0] if not pd.isnull(
                    val_data_retirada[0]) else None]
                # Input
                data_retirada = col6.date_input(label=header_list[23], value=val_data_retirada[0],
                                                format=constants.DATE_FORMAT, key=header_list[23])

                # # Demais Campos
                val_numero_pedido = df_from['N° PEDIDO'].values
                val_numero_pedido = [val_numero_pedido[0] if not pd.isnull(
                    val_numero_pedido[0]) else None]
                numero_pedido = st.number_input(label=header_list[24], value=val_numero_pedido[0],
                                                placeholder="Insira o número do pedido", min_value=0, key=header_list[24])

                val_os_antiga = df_from['O.S ANTIGA / REF ARMAÇÃO'].values
                val_os_antiga = [val_os_antiga[0]
                                 if not pd.isnull(val_os_antiga[0]) else None]
                os_antiga = st.text_input(label=header_list[26], value=val_os_antiga[0],
                                          placeholder="Insira a OS Antiga", key=header_list[26])

                val_observacao = df_from['O.S ANTIGA / REF ARMAÇÃO'].values
                val_observacao = [val_observacao[0]
                                  if not pd.isnull(val_observacao[0]) else None]
                observacao = st.text_area(label=header_list[25], height=20, value=val_observacao[0],
                                          placeholder="Insira suas observações aqui", key=header_list[25])

                # Campo obrigatorio
                mandatory = st.markdown("<p style='font-size: 13px;'> <em>* Campos obrigatórios</em> </p>",
                                        unsafe_allow_html=True)

                # --- SUBMIT BUTTON ---
                submit_button = st.form_submit_button("Atualizar Cadastro")

            return submit_button, df_from


# --- EXCLUSÃO ---
def create_exclusion_form():
    '''Retorna um formulário de EXCLUSÃO de registros com os respectivos campos.'''

    # ---TITULOS---
    st.header(body="Exclusão de Cadastro")

    # # --- EXPANSOR TODOS REGISTROS ---
    # with st.expander(label="Registros atuais"):
    #     # Carrega os registros atuais
    #     df = db_connection.load_data()
    #     # Mostra em um dataframe
    #     st.dataframe(df)

    # --- EXPANSOR SELEÇÃO OS ---
    with st.expander(label="Ordem de Serviço:", expanded=True):

        # Retorna os valores unicos das OSs
        opcoes_ordem_servico = db_connection.get_unique_orders()
        ordem_servico = st.selectbox(label=header_list[2] + OBRIGATORIO, placeholder="Escolha a Ordem de Serviço desejada", index=None,
                                     help=HELP, options=opcoes_ordem_servico, key=header_list[2])
        # Retorna os valores unicos das OS Ref baseado na OS selecionada
        opcoes_ordem_servico_ref = db_connection.get_unique_orders_ref(ordem_servico)
        ordem_servico_ref = st.selectbox(label=header_list[3] + OBRIGATORIO, placeholder="Escolha a Ordem de Serviço Ref desejada", index=None,
                                         help=HELP, options=opcoes_ordem_servico_ref, key=header_list[3])

        if ordem_servico and ordem_servico_ref:

            # Filtra o Dataframe de acordo com a Ordem de Serviço ('OS' e 'OS REF')
            df_from = db_connection.get_df_by_orders(unique_orders=ordem_servico, unique_orders_ref=ordem_servico_ref)


            # Mostrando o Registro (omite as 03 ultimas colunas do usuario)
            st.write("Registros:")
            st.dataframe(df_from.iloc[:, :-3])

            # # --- INICIALIZANDO O FORMULARIO ---
            with st.form(key=FORMS_KEY[3], clear_on_submit=False):

                # --- INICIO DOS CAMPOS ---
                registro_loja = df_from['LOJA'].values
                idx_loja = opcoes_lojas.index(registro_loja[0])
                loja = st.selectbox(label=header_list[0] + OBRIGATORIO, options=registro_loja, index=0, 
                                    disabled=True, key=header_list[0])

                registro_tipo_lente = df_from['TIPO LENTE'].values
                idx_tipo_lente = opcoes_tipo_lente.index(registro_tipo_lente[0])
                tipo_lente = st.selectbox(label=header_list[5] + OBRIGATORIO, options=registro_tipo_lente, index=0, 
                                          disabled=True, key=header_list[5])

                # Busca o índice do registro p/ default dos dropdowns
                registro_tipo = df_from['TIPO'].values
                idx_tipo = opcoes_tipo.index(registro_tipo[0])
                tipo = st.selectbox(label=header_list[1] + OBRIGATORIO, options=registro_tipo, index=0, 
                                    disabled=True, key=header_list[1])

                registro_fornecedor = df_from['FORNECEDOR'].values
                idx_fornecedor = opcoes_fornecedor.index(registro_fornecedor[0])
                fornecedor = st.selectbox(label=header_list[4] + OBRIGATORIO, options=registro_fornecedor, index=0, 
                                          disabled=True, key=header_list[4])

                registro_lente = df_from['LENTE'].values
                idx_lente = opcoes_lente.index(registro_lente[0])
                lente = st.selectbox(label=header_list[7] + OBRIGATORIO, options=registro_lente, index=0, 
                                     disabled=True, key=header_list[7])

                # --- VALORES NUMERICOS ---
                registro_valor_venda = df_from['VALOR VENDA'].values
                valor_venda = st.number_input(label=header_list[8] + OBRIGATORIO, value=float(registro_valor_venda[0]), 
                                              disabled=True, key=header_list[8])

                registro_valor_lente = df_from['VLR LENTE + TRAT.'].values
                valor_lente = st.number_input(label=header_list[9] + OBRIGATORIO, value=float(registro_valor_lente[0]),
                                              disabled=True, key=header_list[9])



                registro_qualidade = df_from['QUALIDADE'].values
                qualidade = st.selectbox(label=header_list[6], options=registro_qualidade, index=0,
                                         disabled=True, key=header_list[6])

                # --- CUSTOS ADICIONAIS ---
                registro_armacao = df_from['Arm.'].values
                custo_armacao = st.number_input(label="Custo Armação", value=float(registro_armacao[0]),
                                              disabled=True, key=header_list[10])
                

                registro_montagem = df_from['Mont.'].values
                custo_armacao = st.number_input(label="Custo Montagem", value=float(registro_montagem[0]),
                                              disabled=True, key=header_list[11])
                registro_exame = df_from['Exame'].values
                custo_armacao = st.number_input(label="Custo Exame", value=float(registro_exame[0]),
                                              disabled=True, key=header_list[12])
                
                registro_vendedor = df_from['VENDEDOR'].values
                vendedor = st.selectbox(label=header_list[16] + OBRIGATORIO, options=registro_vendedor, index=0,
                                            disabled=True, key=header_list[16])

                registro_cliente = df_from['CLIENTE'].values
                cliente = st.text_input(label=header_list[17] + OBRIGATORIO, value=registro_cliente[0],
                                        disabled=True,  key=header_list[17])

                # --- DATAS ---
                # Coluna para a 1a Seção de Datas
                col1, col2 = st.columns(2)
                # Datas de Venda e Entrega
                val_data_venda = df_from['DATA DA VENDA'].values
                val_data_venda = [val_data_venda[0] if not pd.isnull(val_data_venda[0]) else None]
                data_venda = col1.text_input(label=header_list[18], value=val_data_venda[0],
                                             disabled=True, key=header_list[18])
                
                val_data_entrega = df_from['ENTREGA'].values
                val_data_entrega = [val_data_entrega[0] if not pd.isnull(val_data_entrega[0]) else None]
                data_entrega = col2.text_input(label=header_list[19], value=val_data_entrega[0],
                                              disabled=True, key=header_list[19])

                # Coluna para a 2a Seção de Datas
                col3, col4 = st.columns(2)
                # Datas do Pedido e Lente
                val_data_pedido = df_from['DATA PEDIDO'].values
                val_data_pedido = [val_data_pedido[0] if not pd.isnull(val_data_pedido[0]) else None]
                data_pedido = col3.text_input(label=header_list[20], value=val_data_pedido[0],
                                              disabled=True, key=header_list[20])
                
                val_data_lente = df_from['DATA LENTE'].values
                val_data_lente = [val_data_lente[0] if not pd.isnull(val_data_lente[0]) else None]
                data_lente = col4.text_input(label=header_list[21], value=val_data_lente[0],
                                             disabled=True, key=header_list[21])

                # Coluna para a 3a Seção de Datas
                col5, col6 = st.columns(2)
                # Datas de Montagem e Retirada

                val_data_montagem = df_from['MONTAGEM'].values
                val_data_montagem = [val_data_montagem[0] if not pd.isnull(val_data_montagem[0]) else None]
                data_montagem = col5.text_input(label=header_list[22], value=val_data_montagem[0],
                                               disabled=True, key=header_list[22])

                val_data_retirada = df_from['RETIRADA'].values
                val_data_retirada = [val_data_retirada[0] if not pd.isnull(val_data_retirada[0]) else None]
                data_retirada = col6.text_input(label=header_list[23], value=val_data_retirada[0],
                                                disabled=True,  key=header_list[23])

                # Demais Campos
                val_numero_pedido = df_from['N° PEDIDO'].values
                val_numero_pedido = [val_numero_pedido[0] if not pd.isnull(val_numero_pedido[0]) else None]
                numero_pedido = st.number_input(label=header_list[24], value=val_numero_pedido[0],
                                                disabled=True, key=header_list[24])
              
                val_os_antiga = df_from['O.S ANTIGA / REF ARMAÇÃO'].values
                val_os_antiga = [val_os_antiga[0] if not pd.isnull(val_os_antiga[0]) else None]
                os_antiga = st.text_input(label=header_list[26], value=val_os_antiga[0],
                                          disabled=True, key=header_list[26])

                val_observacao = df_from['O.S ANTIGA / REF ARMAÇÃO'].values
                val_observacao = [val_observacao[0] if not pd.isnull(val_observacao[0]) else None]
                observacao = st.text_area(label=header_list[25], height=20, value=val_observacao[0],
                                          disabled=True, key=header_list[25])

                # --- SUBMIT BUTTON ---
                submit_button = st.form_submit_button("Excluir Cadastro")

            return submit_button, df_from
