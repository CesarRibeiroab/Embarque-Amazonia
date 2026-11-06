import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
db_path = 'd:/Users/Kzar/Documents/Faculdade/Projeto Integrado II/database/embarque.db'
schema_path = 'd:/Users/Kzar/Documents/Faculdade/Projeto Integrado II/database/schema.sql'
seed_path = 'd:/Users/Kzar/Documents/Faculdade/Projeto Integrado II/database/seed.sql'

con = sqlite3.connect(db_path)
cur = con.cursor()

with open(schema_path, 'r', encoding='utf-8') as f:
    cur.executescript(f.read())

with open(seed_path, 'r', encoding='utf-8') as f:
    cur.executescript(f.read())

con.commit()

print("BANCO DE DADOS EXECUTADO COM SUCESSO!")
tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tabelas criadas:")
for t in tables:
    print(f"  - {t[0]}")

count_trechos = cur.execute("SELECT COUNT(*) FROM trecho").fetchone()[0]
count_loc = cur.execute("SELECT COUNT(*) FROM localidade").fetchone()[0]
count_mod = cur.execute("SELECT COUNT(*) FROM modal").fetchone()[0]
print(f"\nRegistros inseridos: {count_loc} localidades, {count_mod} modais, {count_trechos} trechos.")

# Test query
print("\nConsulta de teste (Trechos saindo de Belém):")
rows = cur.execute("""
    SELECT t.id, o.nome, d.nome, m.nome, t.duracao_estimada_minutos, t.tarifa_base_reais, t.data_ultima_atualizacao
    FROM trecho t
    JOIN localidade o ON t.origem_id = o.id
    JOIN localidade d ON t.destino_id = d.id
    JOIN modal m ON t.modal_id = m.id
    WHERE t.origem_id = 1
""").fetchall()

for r in rows:
    print(f"  Trecho {r[0]}: {r[1]} -> {r[2]} | {r[3]} | {r[4]} min | R$ {r[5]:.2f} | Atualizado: {r[6]}")

con.close()
