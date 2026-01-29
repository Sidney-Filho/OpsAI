import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar cliente Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Exemplo: Inserir dados
def inserir_utilizador(nome, email):
    data = supabase.table('utilizadores').insert({
        "nome": nome,
        "email": email
    }).execute()
    return data

# Exemplo: Ler dados
def obter_utilizadores():
    response = supabase.table('utilizadores').select("*").execute()
    return response.data

# Exemplo: Atualizar dados
def atualizar_utilizador(id, novo_nome):
    data = supabase.table('utilizadores').update({
        "nome": novo_nome
    }).eq('id', id).execute()
    return data

# Exemplo: Deletar dados
def deletar_utilizador(id):
    data = supabase.table('utilizadores').delete().eq('id', id).execute()
    return data