from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Reminder
from model import Session
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title = 'Reminder API', version = '1.0.0')
app = OpenAPI(__name__, info = info)
CORS(app)

# tags
documentation_tag = Tag(name = 'Documentação', description = 'Seleção de documentação: Swagger')
reminder_tag = Tag(name = 'Lembrete', description = 'Adição, edição, visualização e remoção de lembretes')

#rota home
@app.get('/', tags = [documentation_tag])
def documentation():
    '''
        Redireciona para /openapi, tela que permite a escolha do estilo
        de documentação.
    '''
    return redirect('/openapi')

#rota create
@app.post('/create', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema,
                     '409': ErrorSchema,
                     '400': ErrorSchema})
def create(form: ReminderSchema):
    '''
        Persiste um novo lembrete na base de dados, retornando sua
        visualização.
    '''
    reminder = Reminder(
        name = form.name,
        description = form.description,
        interval = form.interval,
        send_email = form.send_email,
        recurring = form.recurring)

    logger.debug(f'Adicionando um lembrete de nome: {reminder.name}')
    try:
        session = Session()
        session.add(reminder)
        logger.debug(f'adicionei reminder')
        session.commit()
        logger.debug(f'Adicionando lembrete de nome: {reminder.name}')
        return show_reminder(reminder), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = 'Lembrete de mesmo nome já salvo na base :/'
        logger.warning(f'Erro ao adicionar lembrete {reminder.name}, {error_msg}')
        return {'mensagem': error_msg}, 409

    except Exception as error:
        error_msg = 'Ocorreu um erro ao salvar o lembrete na base'
        logger.warning(f'{error_msg} : {error}')
        return {'mensagem': error_msg}, 400

@app.get('/reminder', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema, '404': ErrorSchema})
def get_reminder(query: ReminderSearchSchema):
    '''
        Exibe o lembrete requisitado, buscado pelo id.
    '''
    reminder_id = query.id
    logger.info(f"Coletando dados sobre o lembrete #{reminder_id}")
    
    session = Session()
    reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
    logger.info(f'reminder: {reminder.name}')

    if not reminder:
        error_msg = 'O lembrete buscado não existe.'
        logger.warning(f"Erro ao buscar lembrete '{reminder_id}', {error_msg}")
        return {"message": error_msg}, 404
    
    logger.debug(f"Lembrete econtrado: '{reminder.name}'")
    return show_reminder(reminder), 200

@app.get('/reminder', tags = [reminder_tag],
        responses = {'200': ReminderViewSchema, '404': ErrorSchema})
def get_reminder_name(query: ReminderSearchByNameSchema):
    '''
        Exibe o lembrete requisitado, buscado pelo nome.
    '''
    reminder_name = query.name
    logger.info(f'Coletando dados sobre o lembrete #{reminder_name}')
    
    session = Session()
    reminder = session.query(Reminder).filter(Reminder.name == reminder_name).first()
    logger.info(f'reminder: {reminder.name}')

    if not reminder:
        error_msg = 'O lembrete buscado não existe.'
        logger.warning(f"Erro ao buscar lembrete '{reminder_name}', {error_msg}")
        return {"message": error_msg}, 404
    
    logger.debug(f"Lembrete econtrado: '{reminder.name}'")
    return show_reminder(reminder), 200

@app.get('/reminders', tags = [reminder_tag],
         responses = {'200': RemindersListSchema, '404': ErrorSchema})
def get_all_reminders():
    '''
        Retorna todos os lembretes salvos no banco.
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
        Atualiza um lembrete a partir do nome.
    '''
    session = Session()
    reminder = session.query(Reminder).filter(Reminder.id == form.id).first()

    logger.debug(f'Alterando um lembrete de nome: {reminder.name}')
    try:
        reminder.name = form.name or reminder.name
        reminder.description = form.description or reminder.description
        reminder.interval = form.interval or reminder.interval
        reminder.send_email = form.send_email or reminder.send_email
        reminder.recurring = form.recurring or reminder.recurring
        session.commit()
        logger.debug(f'Lembrete atualizado, nome: {reminder.name}')
        return show_reminder(reminder), 200

    except Exception as error:
        error_msg = 'Ocorreu um erro ao salvar o lembrete na base'
        logger.info(f'{error_msg} : {error}')
        return {'mensagem': error_msg}, 400

@app.delete('/delete', tags = [reminder_tag],
            responses = {'200': ReminderDeleteSchema, '404': ErrorSchema})
def delete_reminder(query: ReminderSearchByNameSchema):
    '''
        Remove um lembrete a partir do nome informado.
    '''
    reminder_name = query.name
    logger.debug(f"Deletando dados do lembrete #{reminder_name}")

    session = Session()
    was_deleted = session.query(Reminder).filter(Reminder.name == reminder_name).delete()
    session.commit()

    if was_deleted:
        logger.debug(f'Lembrete #{reminder_name} removido com sucesso.')
        return {'message': 'Lembrete removido', 'nome': reminder_name}
    
    error_msg = 'Lembrete não encontrado :/'
    logger.warning(f"Erro ao deletar lembrete #'{reminder_name}', {error_msg}")
    return {'message': error_msg}, 404

if __name__ == '__main__':
    app.run(debug=True)