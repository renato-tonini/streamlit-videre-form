# --- CONSTANTES ---

# --- GERAL ---
# Icones do App
URL_LOGO = "https://oticasvidere.com.br/wp-content/uploads/2023/09/Camada_1logo.png"
URL_LOGO_PAGE_ICON = "https://oticasvidere.com.br/wp-content/uploads/2023/09/Group-636.png"


# --- COOKIES ---
COOKIE_EXPIRY_DAYS = 1 / 24 # 01 hora


# --- CORES ---
# Videre
AZUL_VIDERE = "#220750"     # AZUL LOGO
VERMELHO_VIDERE = "#FF563A" # VERMELHO LETRA LOGO

# Streamlit
FUNDO_STREAMLIT = "#F0F2F6"     # CINZA
SELETORES_STREAMLIT = "#FF4B4B" # VERMELHO

# Plotly
PALETA_GRAFICOS_OP01 = ['#220750', '#00377E', '#008AB2', '#00B2BD', '#6FD8C6']
PALETA_GRAFICOS_OP02 = ['#FF4B4B', '#F63278', '#D738A0', '#525ECF', '#0067CB']

# --- STREAMLIT ---
MENU_LATERAL = ['Novo cadastro', 'Atualizar cadastro',
                'Deletar cadastro', 'Consultar Cadastros', 'Links Uteis']

# --- TABELAS PLANILHA GSHEETS ---
TABELAS_GSHEETS = ['Formulario', 'LOJA', 'TIPO',
                   'FORNECEDOR', 'TIPO LENTE', 'QUALIDADE',
                   "LENTE", 'VENDEDOR', 'OBRIGATORIOS']

# --- DATA PADRÃO ---
DATE_FORMAT = 'DD/MM/YYYY'

# --- TEMPO CACHE ---
# Tempo de cache para as funções em segundos
TIME_TO_LIVE = 10 * 60 # 10 minutos


# --- CUSTOS FIXOS ---
# Dicionario com os valores padrão para cálculo de custo
VALORES_PADRAO = {"Arm.": 35, "Mont.": 10, "Exame": 35}