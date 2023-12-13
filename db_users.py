# --- CONEXOES COM O DATABASE USUARIO (DETA) ---
import os
import streamlit as st
from dotenv import load_dotenv              # pip install python-dotenv
from deta import Deta                       # pip install deta
import streamlit_authenticator as stauth    # pip install streamlit-authenticator


# --- AUTENTICAÇÃO DO DATABASE ---
# Carregando a variavel de ambiente
# load_dotenv(".streamlit/secrets.toml")
load_dotenv(".env")

# Obtendo chave e nome do Database
DETA_KEY = os.getenv("DETA_KEY")
DB_NAME = os.getenv("DB_NAME")

# Inicializando com a chave do Database
deta = Deta(DETA_KEY)
# Conectando com o Database
db = deta.Base(DB_NAME)


# --- FUNÇÕES DO DATABASE USUARIO ---
def get_all_db_users():
    '''Retorna todos os usuários do Database de Usuarios.'''

    # Chamada para retornar todos os usuarios do database
    users = fetch_all_users()
    # Retorna usuarios, nomes e senhas
    usernames = [user["key"] for user in users]
    names = [user["name"] for user in users]
    passwords = [user["password"] for user in users]
    # Gera hash das senhas
    hashed_passwords = stauth.Hasher(passwords).generate()

    return names, usernames, hashed_passwords


def insert_user(username, name, password):
    '''Insere um novo usuário no Database.'''
    return db.put({"key": username, "name": name, "password": password})


def fetch_all_users():
    '''Retorna um dicionario com todos os usuários.'''
    res = db.fetch()
    return res.items


def get_user(username):
    '''Retorna o usuário pelo nome do usuário. 
       Caso não encontre retorna None.'''
    return db.get(username)


def update_user(username, updates):
    '''Se o item for atualizado, retorna None.
       Caso contrário  gera uma exceção'''
    return db.update(updates, username)


def delete_user(username):
    '''Sempre retorna None, mesmo se a chave não existir.'''
    return db.delete(username)


