from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from sqlalchemy.exc import IntegrityError
from model import Reminder, Email, EmailClient
from model import Session
from logger import logger
from schemas import *
from flask_cors import CORS
from datetime import datetime


info = Info(title = 'Reminder API', version = '1.0.0')
app = OpenAPI(__name__, info = info)
CORS(app)

# tags
documentation_tag = Tag(name = 'Documentação', description = 'Seleção de documentação: Swagger')
reminder_tag = Tag(name = 'Lembrete', description = 'Adição, edição, visualização individual ou geral e remoção de lembretes')
email_tag = Tag(name = 'Envio de Email', description = 'Envia um email de lembrete caso a data estipulada no lembrete esteja próxima')

@app.get('/', tags = [documentation_tag])
def documentation():
    '''
        Redireciona para openapi, com a documentação das rotas da API.
    '''
    return redirect('/openapi')

@app.post('/create', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema,
                     '409': ErrorSchema,
                     '400': ErrorSchema})
def create(form: ReminderSchema):
    '''
        Persiste um novo lembrete no banco de dados.
    '''
    reminder = Reminder(
        name = form.name,
        description = form.description,
        due_date = datetime.strptime(form.due_date, "%Y-%m-%dT%H:%M:%S.%fZ"),
        send_email = form.send_email,
        recurring = form.recurring)

    logger.debug(f'Adicionando um lembrete de nome: {reminder.name}')
    try:
        reminder.insert_email(Email(form.email))
        session = Session()
        session.add(reminder)
        session.commit()
        logger.debug(f'Adicionado lembrete de nome: {reminder.name}')

        return show_reminder(reminder), 200

    except IntegrityError:
        error_msg = 'Lembrete de mesmo nome já salvo na base :/'
        logger.warning(f'Erro ao adicionar lembrete {reminder.name}, {error_msg}')

        return {'mensagem': error_msg}, 409

    except Exception as error:
        error_msg = 'Ocorreu um erro ao salvar o lembrete na base'
        logger.warning(f'{error_msg} : {error}')
        logger.debug(f'{error_msg} : {error}')

        return {'mensagem': error_msg}, 400

@app.get('/reminder', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema, '404': ErrorSchema})
def get_reminder(query: ReminderSearchSchema):
    '''
        Retorna o lembrete buscado pelo id.
    '''
    reminder_id = query.id
    logger.info(f"Coletando dados sobre o lembrete #{reminder_id}")
    
    try:
        session = Session()
        reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
        logger.info(f'reminder: {reminder.name}')
    except:
        error_msg = 'O lembrete buscado não existe.'
        logger.warning(f"Erro ao buscar lembrete '{reminder_id}', {error_msg}")

        return {"message": error_msg}, 404
    logger.debug(f"Lembrete econtrado: '{reminder.name}'")

    return show_reminder(reminder), 200

@app.get('/reminder_name', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema, '404': ErrorSchema})
def get_reminder_name(query: ReminderSearchByNameSchema):
    '''
        Retorna o lembrete buscado pelo nome.
    '''
    reminder_name = query.name
    logger.info(f'Coletando dados sobre o lembrete #{reminder_name}')
    try:
        session = Session()
        reminder = session.query(Reminder).filter(Reminder.name == reminder_name).first()
        logger.info(f'reminder: {reminder.name}')
    except:
        error_msg = 'O lembrete buscado não existe.'
        logger.warning(f"Erro ao buscar lembrete '{reminder_name}', {error_msg}")

        return {"message": error_msg}, 404
    
    logger.debug(f"Lembrete encontrado: '{reminder.name}'")
    return show_reminder(reminder), 200

@app.get('/reminders', tags = [reminder_tag],
         responses = {'200': RemindersListSchema, '404': ErrorSchema})
def get_all_reminders():
    '''
        Retorna todos os lembretes salvos no banco de dados.
    '''
    logger.debug(f'Retornando todos os lembretes')
    session = Session()
    reminders = session.query(Reminder).all()

    if not reminders:
        return {'Lembretes': []}, 200
    
    logger.debug(f'%d lembretes encontrados' % len(reminders))
    return show_reminders(reminders), 200

@app.put('/update', tags = [reminder_tag],
         responses = {'200': ReminderViewSchema, '404': ErrorSchema})
def update(form: ReminderUpdateSchema):
    '''
        Atualiza um lembrete pelo id.
    '''
    session = Session()
    reminder = session.query(Reminder).filter(Reminder.id == form.id).first()

    logger.debug(f'Alterando um lembrete de nome: {reminder.name}')
    try:
        reminder.name = form.name or reminder.name
        reminder.description = form.description or reminder.description
        reminder.due_date = form.due_date or reminder.due_date
        reminder.send_email = form.send_email or reminder.send_email
        reminder.email_relationship[0].email = form.email or reminder.email_relationship[0].email
        reminder.recurring = form.recurring or reminder.recurring
        reminder.updated_at = datetime.now()

        session.commit()
        logger.debug(f'Lembrete atualizado, nome: {reminder.name}')
        return show_reminder(reminder), 200

    except Exception as error:
        error_msg = 'Ocorreu um erro ao salvar o lembrete na base'
        logger.info(f'{error_msg} : {error}')
        return {'mensagem': error_msg}, 400

@app.delete('/delete', tags = [reminder_tag],
            responses = {'200': ReminderDeleteSchema, '404': ErrorSchema})
def delete_reminder(query: ReminderSearchSchema):
    '''
        Remove um lembrete pelo id.
    '''
    reminder_id = query.id
    logger.debug(f"Deletando dados do lembrete #{reminder_id}")

    session = Session()
    try:
        session.query(Email).filter(Email.reminder == reminder_id).delete()
        reminder_query = session.query(Reminder).filter(Reminder.id == reminder_id)
        reminder = reminder_query.first()
        reminder_query.delete()
        session.commit()
    except:
        error_msg = 'Lembrete não encontrado :/'
        logger.warning(f"Erro ao deletar lembrete #'{reminder_id}', {error_msg}")
        return {'message': error_msg}, 404
    else:
        logger.debug(f'Lembrete #{reminder_id} removido com sucesso.')
        return {'message': 'Lembrete removido', 'nome': reminder.name}

@app.get('/send_email', tags = [email_tag],
         responses = {'200': EmailSentSchema, '404': ErrorSchema})
def validate_send_email(query: ReminderSearchSchema):
    '''
        Esta rota envia um email com as informações do lembrete, ao email cadastrado.
        Lembrete a 1 dia ou menos de alcançar o due_date.
    '''
    session = Session()
    reminder = session.query(Reminder).filter(Reminder.id == query.id).first()
    send_email: bool = reminder.validate_email_before_send()

    if send_email:
        email_receiver = reminder.email_relationship[0].email
        due_date_adjusted = reminder.due_date.strftime("%d/%m/%Y")
        email_client = EmailClient(
            f'''
                Olá usuário(a), este é um email automatizado para avisar
                que o lembrete nome:  {reminder.name}, de descrição: 
                {reminder.description}, e com data final: {due_date_adjusted},
                está próximo à data estipulada.

                Atenciosamente,
                Aplicativo Lembretes
            ''',
            email_receiver
        )
        try:
            email_client.prepare_and_send_email()
            return {'message': f'Email enviado para o destinatário: {email_receiver}'}, 200
        except Exception as error:
            logger.warning(f'Erro ao validar e enviar email para lembrete#{reminder.id}, erro : {error}')
            return {'message': 'Ocorreu um erro ao enviar o email.'}, 404
    else:
        if not reminder.email_relationship[0].email:
            return {'message': f'O lembrete não possui email cadastrado'}, 200
        if not reminder.send_email:
            return {'message': f'O usuário optou por não receber email.'}, 200
        return {'message': f'A data do lembrete é {reminder.due_date} e, portanto, superior à 1 dia a data atual'}, 200
