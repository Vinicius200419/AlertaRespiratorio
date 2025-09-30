import sqlite3
import threading
import time
import os
from flask import Flask, request, redirect, url_for, send_file

import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

app = Flask(__name__)

OWM_API_KEY = os.getenv("OWM_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

DB = 'usuarios.db'

# Temperaturas ideais por doença (°C)
doencas_temperaturas = {
    'asma': (20, 25),
    'rinite': (18, 24),
    'bronquite': (20, 25),
    'dpoc': (20, 24),
    'sinusite': (20, 24),
    'infec_respiratoria_viral': (20, 22),
    'pneumonia': (20, 24),
    'fibrose_pulmonar': (21, 25),
    'apneia_do_sono': (20, 22),
    'hipersensibilidade_pneumonitis': (20, 24),
}

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            cidade TEXT NOT NULL,
            doenca TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def enviar_email(destino, temp, cidade, doenca_nome):
    assunto = f'Alerta: Temperatura fora do ideal para {doenca_nome}'
    corpo = (f'A temperatura atual em {cidade} é {temp:.1f}°C, '
             f'o que está fora da faixa ideal para a sua condição ({doenca_nome}). '
             'Cuide-se e evite exposição ao clima adverso!')
    message = Mail(
        from_email='vinialvesbatista04@gmail.com',
        to_emails=destino,
        subject=assunto,
        plain_text_content=corpo
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"E-mail enviado para {destino}, status {response.status_code}")
    except Exception as e:
        print(f"Erro ao enviar e-mail para {destino}: {e}")

def checar_temperaturas():
    while True:
        print("Iniciando verificação automática de temperaturas...")
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('SELECT email, cidade, doenca FROM usuarios')
        usuarios = c.fetchall()
        conn.close()

        for user in usuarios:
            email, cidade, doenca = user
            params = {
                'q': cidade,
                'appid': OWM_API_KEY,
                'units': 'metric',
                'lang': 'pt'
            }
            try:
                resp = requests.get(base_url, params=params)
                data = resp.json()
                if resp.status_code != 200:
                    print(f"Erro ao buscar temperatura para {cidade}.")
                    continue
                temp = data['main']['temp']
                temp_min, temp_max = doencas_temperaturas[doenca]
                if temp < temp_min or temp > temp_max:
                    enviar_email(email, temp, cidade, doenca.replace('_', ' ').capitalize())
                else:
                    print(f"Temperatura OK para {email} - {cidade} - {doenca}")
            except Exception as e:
                print(f"Erro ao verificar usuário {email}: {e}")
        
        time.sleep(120)  # espera 2 minutos

@app.route('/static.css')
def css():
    return send_file("static.css")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        cidade = request.form['cidade']
        doenca = request.form['doenca']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('INSERT INTO usuarios (email, cidade, doenca) VALUES (?, ?, ?)', (email, cidade, doenca))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    with open("form.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

if __name__ == '__main__':
    init_db()
    # Inicia a thread de checagem automática
    thread = threading.Thread(target=checar_temperaturas, daemon=True)
    thread.start()
    app.run(debug=True)
