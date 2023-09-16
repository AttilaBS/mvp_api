import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib

load_dotenv('../.env')


class EmailClient():

    def __init__(
        self,
        body: object,
        email_receiver: object,
        subject: str = 'Aviso de Lembrete',
        email_sender: str = os.environ.get('EMAIL_SENDER'),
        email_password: str = os.environ.get('EMAIL_PASSWORD')):
        self.body = body
        self.email_receiver = email_receiver
        self.subject = subject
        self.email_sender = email_sender
        self.email_password = email_password

    def prepare_and_send_email(self):
        em = EmailMessage()
        em['From'] = self.email_sender
        em['To'] = self.email_receiver
        em['Subject'] = self.subject
        em.set_content(self.body)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(self.email_sender, self.email_password)
            smtp.sendmail(self.email_sender, self.email_receiver, em.as_string())
