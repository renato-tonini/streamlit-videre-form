import streamlit as st


# --- CONFIG GERAL ---
PAGE_TITLE = "Links Uteis"
DESCRICAO = "Clique nos links abaixo para ser direcionado ao site:"

# --- LINKS ---
LINKS_SITES = {
    "Site Videre": "https://oticasvidere.com.br/",
    "Fornecedor X": "https://www.registrobase.com.br/app.rb/", 
}


# --- FUNÇÃO DE LINKS UTEIS ---
def create_useful_links():
    '''Cria a pagina de links uteis.'''

    # --- INÍCIO PAGINA ---
    st.header(body=PAGE_TITLE)
    st.markdown(DESCRICAO)

    # Iterando sobre o dicionário de links
    for index, (page_name, page_link) in enumerate(LINKS_SITES.items()):
        # Hyperlink - Ajustada a config pelo arquivo .css
        st.write(f"[{page_name}]({page_link})")

    