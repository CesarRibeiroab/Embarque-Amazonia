import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Caminhos dinâmicos baseados no diretório atual do script (compatível com qualquer máquina/SO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'embarque.db')
schema_path = os.path.join(BASE_DIR, 'schema.sql')
seed_path = os.path.join(BASE_DIR, 'seed.sql')

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
