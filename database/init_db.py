import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
db_path = 'd:/Users/Kzar/Documents/Faculdade/Projeto Integrado II/database/embarque.db'
schema_path = 'd:/Users/Kzar/Documents/Faculdade/Projeto Integrado II/database/schema.sql'
seed_path = 'd:/Users/Kzar/Documents/Faculdade/Projeto Integrado II/database/seed.sql'

# Limpar arquivo prévio para reinicialização limpa
if os.path.exists(db_path):
    os.remove(db_path)

con = sqlite3.connect(db_path)
cur = con.cursor()

with open(schema_path, 'r', encoding='utf-8') as f:
    cur.executescript(f.read())

with open(seed_path, 'r', encoding='utf-8') as f:
    cur.executescript(f.read())

con.commit()

print("BANCO DE DADOS EXECUTADO COM SUCESSO!")
count_loc = cur.execute("SELECT COUNT(*) FROM localidade").fetchone()[0]
count_mod = cur.execute("SELECT COUNT(*) FROM modal").fetchone()[0]
count_trechos = cur.execute("SELECT COUNT(*) FROM trecho").fetchone()[0]

print(f"Registros carregados da base:")
print(f"  - Localidades: {count_loc}")
print(f"  - Modais (Domínio Regional): {count_mod} (todos os 10 modais cadastrados)")
print(f"  - Trechos: {count_trechos}")

# Listar os 10 modais
print("\nModais cadastrados:")
for m in cur.execute("SELECT id, codigo, nome, categoria FROM modal ORDER BY id").fetchall():
    print(f"  [{m[0]}] {m[2]} ({m[3]}) - código: {m[1]}")

con.close()
