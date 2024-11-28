import sqlite3


conn = sqlite3.connect('banco_de_dados_sympla.db')
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL
);
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS dados_eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_evento INTEGER,
    data TEXT,
    localizacao TEXT,
    FOREIGN KEY(id_evento) REFERENCES eventos(id)
);
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS metadados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_evento INTEGER,
    metadado TEXT,
    FOREIGN KEY(id_evento) REFERENCES eventos(id)
);
''')


conn.commit()
conn.close()

print("Banco de dados e tabelas criados com sucesso! :3")
