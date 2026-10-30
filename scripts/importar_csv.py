import os
from dotenv import load_dotenv
import pandas as pd
import mysql.connector
from deep_translator import GoogleTranslator

# Carrega as variáveis do .env
load_dotenv()

colunas = ['id_filme', 'título', 'ano_lançamento', 'gêneros', 'diretor', 'language', 'description']
df = pd.read_csv('IMDb_filmes_Brasil.csv', sep=';', usecols=colunas, encoding='utf-8')

df = df.rename(columns={
    'título': 'titulo',
    'ano_lançamento': 'ano_lancamento',
    'gêneros': 'generos',
    'language': 'idioma',
    'description': 'descricao'
})

# CORREÇÃO 1: Substituir o ';' por ',' nos textos
df['titulo'] = df['titulo'].str.replace(';', ',')
df['generos'] = df['generos'].str.replace(';', ',')

# Trocar valores vazios por nulos
df = df.where(pd.notnull(df), None)

# CORREÇÃO 2: Traduzir os títulos para Português
print("Traduzindo os títulos... Isso pode levar cerca de 1 a 3 minutos. Aguarde!")
tradutor = GoogleTranslator(source='auto', target='pt')

def traduzir_texto(texto):
    if not texto: return texto
    try:
        return tradutor.translate(texto)
    except:
        return texto # Se der erro na rede, mantém o original

df['titulo'] = df['titulo'].apply(traduzir_texto)

# Conectar ao banco
conexao = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD') or '', 
    database=os.getenv('DB_NAME')
)
cursor = conexao.cursor()

# Limpar os 846 filmes antigos antes de colocar os novos para não duplicar
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("TRUNCATE TABLE filmes;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

# Inserir os filmes corrigidos
sql = "INSERT INTO filmes (id_filme, titulo, ano_lancamento, generos, diretor, idioma, descricao) VALUES (%s, %s, %s, %s, %s, %s, %s)"
valores = df.values.tolist()

cursor.executemany(sql, valores)
conexao.commit()

print(f"{cursor.rowcount} filmes corrigidos, traduzidos e importados com sucesso!")

cursor.close()
conexao.close()