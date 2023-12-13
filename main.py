# --- PAGINA PRINCIPAL ---
import streamlit as st
import streamlit_authenticator as stauth        # pip install streamlit-authenticator

# def main():

# --- CONFIGURAÇÃO INICIAL DO APP ---
# Necessario no topo do script
st.set_page_config(page_title="Formulário Videre",
                   page_icon="https://oticasvidere.com.br/wp-content/uploads/2023/09/Group-636.png",
                   layout="wide",
                   initial_sidebar_state="expanded")


# --- AUXILIARES ---
import consultas
import utils
import forms
import db_connection
import db_users
import constants
import links


# --- AUTENTICAÇÃO DE LOGIN USUÁRIO ---
# Chamada da função para retornar todos os usuários do database
names, usernames, hashed_passwords = db_users.get_all_db_users()

authenticator = stauth.Authenticate(names=names, usernames=usernames, passwords=hashed_passwords,
                                    cookie_name="login_videre", 
                                    cookie_expiry_days=constants.COOKIE_EXPIRY_DAYS,
                                    key="login_videre")

name, authentication_status, username = authenticator.login(
    form_name="Login", location='main')

st.write('name session', st.session_state['name'])
st.write('username session', st.session_state['username'])

# Verificações da autenticação
if authentication_status == None:
    st.warning("Digite seu Usuário e Senha.")

if authentication_status == False:
    st.error("Usuário ou senha inválidos")

# --- USUARIO AUTENTICADO ---
if authentication_status:

    # --- ESTILIZAÇÃO CSS ---
    # Faz a leitura do arquico style.css (estiliza os Cards)
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style', unsafe_allow_html=True)

    # --- MENU LATERAL ---
    with st.sidebar:

        # Botao de Logout
        logout_button = authenticator.logout("Sair", location='sidebar')

        # Exibe o logotipo no sidebar
        st.image(image=constants.URL_LOGO)

        # TESTE
        # Username
        st.write("name", name)
        st.write("username", username)
        
       
        # # Botão de Limpeza de Cache
        # cache_button = st.button(label="Atualizar Base", key="atualizar_base", on_click=st.cache_data.clear())

        # Exibe um titulo
        st.title("Sistema de Cadastro")
        # Incluindo radio buttons para escolha do usuário
        choice = st.selectbox(label="Navegação", options=constants.MENU_LATERAL)
        
        # # incluindo informações sobre a aplicação
        # st.info("Esta aplicação permite adicionar cadastros, fazer atualizações, e realizar consultas aos registros de vendas da Videre.")

    # Verificando qual a opção escolhida no sidebar
    # --- 01. CADASTRO NOVO REGISTRO ---
    if choice == constants.MENU_LATERAL[0]:

        # Criando o Formulário de Cadastro
        submit_button = forms.create_register_form()

        if submit_button:

            # Limpando o cache para retornar a base mais atualizada
            st.cache_data.clear()

            # Função para retornar os campos obrigatórios
            validacao_obrigatorios = utils.validate_mandatory_fields()

            # ---EXPANSORES ---
            with st.expander("Campos Obrigatórios"):
                # Retorna um resumo dos campos e valores preenchidos com respectivo status
                fields_summary = utils.mandatory_fields_summary()

            # ---Resumo dos Custos--- #
            with st.expander("Resumo"):
                # Retorna um resumo com KPIs básicos e Custos discriminados
                values_fields_summary = utils.values_fields_summary()

            if validacao_obrigatorios:
                # Cria um Dataframe com o registro
                df_form = utils.create_dataframe_from_session()

                # Verifica se já existe algum registro com a OS e OS REF
                record_exist = db_connection.check_record_exist(df_form)

                # Caso não exista registro com mesma OS e OS REF
                if not record_exist:
                    # Insere o registro
                    with st.expander(label="Registro Adicionado"):
                        # Mostra DataFrame ao usuário (omitindo as 03 ultimas colunas)
                        st.dataframe(df_form.iloc[:, :-3])
                        # Insere novo registro via lib gspread
                        new_record = db_connection.insert_new_row(df_form)

                    # Exibe mensagem
                    st.success(body="Registro efetuado com sucesso.")

    # --- 02. ATUALIZAR CADASTRO ---
    if choice == constants.MENU_LATERAL[1]:

        # Criando o Formulário de Cadastro
        result = forms.create_update_form()

        # Verifica se a função retornou algo
        if result is not None:

            # Desempacota os valores retornados na função
            submit_button, df_from = result

            if submit_button:

                # Limpando o cache para retornar a base mais atualizada
                st.cache_data.clear()

                # Função para retornar os campos obrigatórios
                validacao_obrigatorios = utils.validate_mandatory_fields()

                # ---EXPANSORES ---
                with st.expander("Campos Obrigatórios"):
                    # Retorna um resumo dos campos e valores preenchidos com respectivo status
                    fields_summary = utils.mandatory_fields_summary()

                # ---Resumo dos Custos--- #
                with st.expander("Resumo"):
                    # Retorna um resumo com KPIs básicos e Custos discriminados
                    values_fields_summary = utils.values_fields_summary()

                with st.expander("Alterações"):

                    # Cria um Dataframe com o registro atualizado (TO)
                    df_to = utils.create_dataframe_from_session()

                    # Cria um Dataframe de comparação das alterações (FROM/TO)
                    df_is_equal = utils.create_comparison_df(df_from=df_from, df_to=df_to)

                # Se houver alguma alteração a ser feita
                if not df_is_equal:
                    # Se os campos obrigatórios foram preenchidos
                    if validacao_obrigatorios:
                        # Altera o status do registro anterior para False
                        updated_record = db_connection.change_record_status(df_from)
                        # Insere o registro atualizado
                        new_record = db_connection.insert_new_row(df_to)
                        # Exibe mensagem
                        st.success("Registro atualizado com sucesso.")
                else:  # Se não houver alteração
                    st.warning("Não foi alterado nenhum campo do registro original.")

            # # Reseta a sessao para verificação dos campos do formulario
            # utils.reset_session_state()

    # --- 03. EXCLUIR CADASTRO ---
    if choice == constants.MENU_LATERAL[2]:

        # Criando o Formulário de Cadastro
        result = forms.create_exclusion_form()

        # Verifica se a função retornou algo
        if result is not None:

            # Desempacota os valores retornados na função
            submit_button, df_from = result

            if submit_button:

                # Limpando o cache para retornar a base mais atualizada
                st.cache_data.clear()

                # Altera o status do registro anterior para False
                exclude_record = db_connection.exclude_record(df_from)

                # Exibe mensagem
                st.success("Registro excluído com sucesso.")

    # --- 04. CONSULTAR CADASTROS ---
    if choice == constants.MENU_LATERAL[3]:

        # Limpando o cache para retornar a base mais atualizada
        # st.cache_data.clear()

        consultas = consultas.create_queries()


    # # --- 05. LINKS UTEIS ---
    if choice == constants.MENU_LATERAL[4]:

        # Adiciona a pagina de links uteis
        useful_links = links.create_useful_links()




# if __name__ == '__main__':
#     main()
