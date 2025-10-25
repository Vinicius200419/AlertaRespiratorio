import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Alerta:
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY não encontrada no ambiente (.env)")
        self.remetente = "vinialvesbatista04@gmail.com" 

    def enviar_email(self, destino, temp, cidade, doenca_nome):
        assunto = f"⚠️ Alerta: Temperatura fora do ideal para {doenca_nome}"
        corpo = (
            f"A temperatura atual em {cidade} é {temp:.1f}°C, "
            f"o que está fora da faixa ideal para a sua condição ({doenca_nome}). "
            "Cuide-se e evite exposição ao clima adverso!"
        )

        message = Mail(
            from_email=self.remetente,
            to_emails=destino,
            subject=assunto,
            plain_text_content=corpo
        )

        try:
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            print(f"✅ E-mail enviado para {destino}, status {response.status_code}")
            self.salvar_log(destino, cidade, temp, doenca_nome)
        except Exception as e:
            print(f"❌ Erro ao enviar e-mail para {destino}: {e}")

    def salvar_log(self, destino, cidade, temp, doenca):
        with open("log_alertas.txt", "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now()}] Enviado para {destino} | {cidade} | {doenca} | {temp:.1f}°C\n")
