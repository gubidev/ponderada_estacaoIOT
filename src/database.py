import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'dados.db')

def get_db_connection():
    
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=5000')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS leituras (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            temperatura REAL    NOT NULL,
            umidade     REAL    NOT NULL,
            pressao     REAL,
            timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.close()

def inserir_leitura(temperatura, umidade, pressao=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO leituras (temperatura, umidade, pressao)
        VALUES (?, ?, ?)
    ''', (temperatura, umidade, pressao))
    conn.commit()
    id_novo = cursor.lastrowid
    conn.close()
    return id_novo

def listar_leituras(limite=50):
    conn = get_db_connection()
    leituras = conn.execute('SELECT * FROM leituras ORDER BY timestamp DESC LIMIT ?', (limite,)).fetchall()
    conn.close()
    return [dict(ix) for ix in leituras]

def buscar_leitura(id):
    conn = get_db_connection()
    leitura = conn.execute('SELECT * FROM leituras WHERE id = ?', (id,)).fetchone()
    conn.close()
    return dict(leitura) if leitura else None

def atualizar_leitura(id, temperatura, umidade, pressao=None):
    conn = get_db_connection()
    conn.execute('''
        UPDATE leituras SET temperatura = ?, umidade = ?, pressao = ?
        WHERE id = ?
    ''', (temperatura, umidade, pressao, id))
    conn.commit()
    conn.close()

def deletar_leitura(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM leituras WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def calcular_estatisticas():
    conn = get_db_connection()
    row = conn.execute('''
        SELECT
            AVG(temperatura) AS media_temp,
            MIN(temperatura) AS min_temp,
            MAX(temperatura) AS max_temp,
            AVG(umidade)     AS media_umid,
            MIN(umidade)     AS min_umid,
            MAX(umidade)     AS max_umid,
            AVG(pressao)     AS media_pressao,
            MIN(pressao)     AS min_pressao,
            MAX(pressao)     AS max_pressao,
            COUNT(*)         AS total
        FROM leituras
    ''').fetchone()
    conn.close()
    return dict(row) if row else {}
