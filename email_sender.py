import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading
from dotenv import load_dotenv

load_dotenv()

class EmailSender:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.user = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS") # Aici trebuie 'App Password', nu parola normală
        self.admin_email = os.getenv("EMAIL_ADMIN")

    def send_report_thread(self, reported_text):
        """Lansează trimiterea în fundal pentru a nu bloca aplicația"""
        if not self.user or not self.password:
            print("⚠️ EROARE: Credențialele email lipsesc din .env")
            return
        
        # Pornim thread-ul
        thread = threading.Thread(target=self._send, args=(reported_text,), daemon=True)
        thread.start()

    def _send(self, reported_text):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.user
            msg['To'] = self.admin_email
            msg['Subject'] = "⚠️ REPORT: Mesaj AI Raportat"

            body = f"""
            <h3>Raport Utilizator (Feedback)</h3>
            <p>Un utilizator a semnalat acest mesaj ca fiind incorect:</p>
            <blockquote style="background: #ffe6e6; padding: 15px; border-left: 5px solid #ff0000; color: #333;">
                {reported_text}
            </blockquote>
            <p>Verifică logica AI.</p>
            """
            
            # MODIFICARE MAJORĂ: Adăugat 'utf-8' pentru suport limba română
            msg.attach(MIMEText(body, 'html', 'utf-8'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls() # Securizează conexiunea
            server.login(self.user, self.password)
            server.send_message(msg)
            server.quit()
            print("✅ Email de raportare trimis cu succes.")
            
        except smtplib.SMTPAuthenticationError:
            print("❌ Eroare Autentificare: Verifică dacă folosești 'App Password', nu parola de login.")
        except Exception as e:
            print(f"❌ Eroare generală trimitere email: {e}")