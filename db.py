import sqlite3

DB = "usuarios.db"  # ajuste para o nome/caminho do seu banco

conn = sqlite3.connect(DB)
c = conn.cursor()

# apaga todos os registros da tabela usuarios
c.execute("DELETE FROM usuarios;")

# reseta o autoincremento (opcional)
c.execute("DELETE FROM sqlite_sequence WHERE name='usuarios';")

conn.commit()
conn.close()

print("Todos os dados da tabela 'usuarios' foram apagados.")
