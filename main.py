import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3

# Função para formatar e extrair a data em formato 'dd/mm'
def formatar_data(data_str):
    try:
        if 'a' in data_str and "às" not in data_str:
            datas = data_str.split("a")
            datas_formatadas = [datetime.strptime(data.strip(), '%d de %b').strftime('%d/%m') for data in datas]
            return " a ".join(datas_formatadas)
        
        elif "às" in data_str:
            data_formatada = datetime.strptime(data_str, '%A, %d de %b às %H:%M')
            return data_formatada.strftime('%d/%m às %H:%M')
        
        return "SEM DATA"
    
    except Exception as e:
        return "SEM DATA"

def extrair_horario(data_str):
    if not data_str:  # Verifica se a string é vazia ou None
        return "SEM HORÁRIO"
    
    if "às" in data_str:  # Verifica se "às" está presente na string
        partes = data_str.split("às", 1)  # Divide apenas na primeira ocorrência de "às"
        if len(partes) > 1:  # Verifica se há uma segunda parte após "às"
            return partes[1].strip()  # Remove espaços extras e retorna o horário
    
    return "SEM HORÁRIO"  # Caso não contenha "às"
    

# Função para determinar o tipo de evento com base no título
def determinar_tipo(titulo):
    titulo = titulo.lower()
    if "teatro" in titulo:
        return "Teatro"
    elif "musical" in titulo:
        return "Teatro Musical"
    elif "festival" in titulo:
        return "Festival"
    else:
        return "Teatro/Outro"

# Função para preencher com formato padrão quando não houver data ou horário
def preencher_com_padrao(data, horario):
    if data == "SEM DATA":
        data = "25/12 a 31/12"
    if horario == "SEM HORÁRIO":
        horario = "00:00"
    return data, horario

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('banco_de_dados_sympla.db')
cursor = conn.cursor()

# Função para inserir um evento
def inserir_evento(nome, tipo):
    cursor.execute('''
    INSERT INTO eventos (nome, tipo) 
    VALUES (?, ?);
    ''', (nome, tipo))
    conn.commit()
    return cursor.lastrowid  # Retorna o id do evento recém-inserido

# Função para inserir dados de um evento
def inserir_dados_evento(id_evento, data, localizacao):
    cursor.execute('''
    INSERT INTO dados_eventos (id_evento, data, localizacao) 
    VALUES (?, ?, ?);
    ''', (id_evento, data, localizacao))
    conn.commit()

# Função para inserir metadados de um evento
def inserir_metadado(id_evento, metadado):
    cursor.execute('''
    INSERT INTO metadados (id_evento, metadado) 
    VALUES (?, ?);
    ''', (id_evento, metadado))
    conn.commit()

# Definir a URL e headers
url = 'https://www.sympla.com.br/eventos'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

# Realizar a requisição
requisicao = requests.get(url, headers=headers)
site = BeautifulSoup(requisicao.text, "html.parser")

# Encontrar todos os eventos
eventos = site.find_all("a", class_="sympla-card")

for evento in eventos:
    # Extrair título
    titulo_evento = evento.find("h3", class_="pn67h18")
    titulo_evento = titulo_evento.get_text() if titulo_evento else "Título não encontrado"
    
    # Extrair localização (substituindo a descrição)
    localizacao_evento = evento.find("p", class_="pn67h1a")
    localizacao_evento = localizacao_evento.get_text() if localizacao_evento else "Localização não encontrada"
    
    # Extrair link
    link_evento = evento.get('href')
    
    # Extrair data e horário
    data_hora = evento.find("div", class_="qtfy413 qtfy414")
    data = "SEM DATA"
    horario = "SEM HORÁRIO"
    
    if data_hora:
        data_text = data_hora.get_text().strip()
        data = formatar_data(data_text) 
        horario = extrair_horario(data_text)
    
    # Preencher com valores padrão, caso não haja data ou horário
    data, horario = preencher_com_padrao(data, horario)
    
    # Determinar o tipo do evento
    tipo_evento = determinar_tipo(titulo_evento)
    
    # Inserir os dados nas tabelas do banco de dados
    id_evento = inserir_evento(titulo_evento, tipo_evento)
    inserir_dados_evento(id_evento, data, localizacao_evento)
    if horario != "SEM HORÁRIO":
        inserir_metadado(id_evento, f'Horário: {horario}')
    else:
        inserir_metadado(id_evento, 'Sem Horário')

    # Imprimir as informações (opcional)
    print(f"Título: {titulo_evento}")
    print(f"Localização: {localizacao_evento}")
    print(f"Link: {link_evento}")
    print(f"Data: {data}")
    print(f"Horário: {horario}")
    print(f"Tipo: {tipo_evento}")
    print("-" * 50)

# Fechar a conexão
conn.close()

print("Dados extraídos e inseridos com sucesso!")
