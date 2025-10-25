import sqlite3

DB = "usuarios.db"  

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("DELETE FROM usuarios;")

c.execute("DELETE FROM sqlite_sequence WHERE name='usuarios';")

conn.commit()
conn.close()

print("Todos os dados da tabela 'usuarios' foram apagados.")
