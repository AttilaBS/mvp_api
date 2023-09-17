import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib

load_dotenv('../.env')


class EmailClient():

    def __init__(
        self,
        name: str,
        description: str,
        due_date: str,
        email_receiver: str,
        subject: str = 'Aviso de Lembrete',
        email_sender: str = os.environ.get('EMAIL_SENDER'),
        email_password: str = os.environ.get('EMAIL_PASSWORD')):
        self.name = name
        self.description = description
        self.due_date = due_date
        self.email_receiver = email_receiver
        self.subject = subject
        self.email_sender = email_sender
        self.email_password = email_password

    def prepare_and_send_email(self) -> None:
        '''
            Function to create the email and send it.
        '''
        em = EmailMessage()
        em.set_content(f'''
                Olá usuário(a), este é um email automatizado para avisar
                que o lembrete nome:  {self.name}, de descrição: 
                {self.description}, e com data final: {self.due_date},
                está próximo à data estipulada.

                Atenciosamente,
                Aplicativo Lembretes
            ''')
        em.add_alternative(f'''\
         <!DOCTYPE html>
            <html>
                <body>
                    <h1 style="color:#dd8888;">Lembrete:</h1>
                        <div><p>Olá usuário(a), este é um email automatizado
                           para avisar </br> que o lembrete nome: <strong>{self.name}</strong> 
                           </br> de descrição: <strong>{self.description}</strong>,
                           e com data final: <strong>{self.due_date}</strong>,
                           </br> está próximo à data estipulada.</p>
                            <p>Atenciosamente,</p>
                            <p>Aplicativo Lembretes</p>
                        </div>
                </body>
            </html>
        ''', subtype = 'html')
        em['From'] = self.email_sender
        em['To'] = self.email_receiver
        em['Subject'] = self.subject
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(self.email_sender, self.email_password)
            smtp.sendmail(self.email_sender, self.email_receiver, em.as_string())
