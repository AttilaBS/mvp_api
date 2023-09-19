from pydantic import BaseModel, validator
from typing import Optional, List
from model.reminder import Reminder
from model import Session
from datetime import datetime
import re


class ReminderSchema(BaseModel):
    '''
        Define como um novo lembrete a ser persistido deve ser.
    '''
    name: str = 'Trocar o óleo do carro'
    description: str = 'trocar o óleo a cada 10 mil km no Moraes AutoCenter'
    due_date: str = '2023-09-20T00:00:00.000Z'
    send_email: Optional[bool] = False
    email: Optional[str]
    recurring: Optional[bool] = False

    @validator('name', allow_reuse = True)
    def validator_name(cls, v):
        if not len(v) > 0:
            raise ValueError('O nome não pode ser vazio!')
        if re.search('[0-9]', v):
            raise ValueError('O nome do lembrete não pode conter números')
        return v
    
    @validator('description', allow_reuse = True)
    def validator_description(cls, v):
        if not len(v) > 0:
            raise ValueError('A descrição não pode ser vazia!')
        return v


class ReminderUpdateSchema(BaseModel):
    '''
        Define como um lembrete a ser atualizado pode ser salvo.
    '''
    id: int = 1
    name: Optional[str] = 'Ir no dentista'
    name_normalized: str = 'ir no dentista'
    description: Optional[str] = 'Marcar o retorno da consulta'
    due_date: Optional[datetime] = '2023-10-20T00:00:00.000Z'
    send_email: Optional[bool] = True
    email: Optional[str] = 'emaildeexemplo@email.com'
    recurring: Optional[bool] = False
    updated_at = datetime.now()

    @validator('name', allow_reuse = True)
    def validator_name(cls, v):
        if not len(v) > 0:
            raise ValueError('O nome não pode ser vazio!')
        if re.search('[0-9]', v):
            raise ValueError('O nome do lembrete não pode conter números')
        return v
    
    @validator('description')
    def validator_description(cls, v):
        if not len(v) > 0:
            raise ValueError('A descrição não pode ser vazia!')
        return v


class ReminderSearchSchema(BaseModel):
    '''
        Define como será a busca de lembrete apenas pelo id.
    '''
    id: int


class ReminderSearchByNameSchema(BaseModel):
    '''
        Define como será a busca de lembrete apenas pelo nome.
    '''
    name: str


class ReminderDeleteSchema(BaseModel):
    '''
        Define como será o retorno após a remoção de um lembrete.
    '''
    message: str
    name: str


class RemindersListSchema(BaseModel):
    '''
        Define como a listagem de lembretes será retornada.
    '''
    reminders:List[ReminderSchema]


class ReminderViewSchema(BaseModel):
    '''
        Define como será a visualização de um lembrete.
    '''
    id: int
    name: str
    name_normalized: str
    description: str
    due_date: datetime
    email: Optional[str]
    send_email: Optional[bool]
    recurring: Optional[bool]


class EmailSentSchema(BaseModel):
    '''
        Define como será a resposta ao enviar um email de lembrete.
    '''
    message: str
    name: str

def show_reminder(reminder: Reminder):
    '''
        Retorna a representação de um lembrete seguindo o esquema definido
        em ReminderViewSchema.
    '''
    return {
        'id': reminder.id,
        'name': reminder.name,
        'name_normalized': reminder.name_normalized,
        'description': reminder.description,
        'due_date': reminder.due_date,
        'send_email': reminder.send_email,
        'email': reminder.email_relationship[0].email,
        'recurring': reminder.recurring
    }

def show_reminders(reminders: List[Reminder]):
    '''
        Retorna a representação do lembrete seguindo o esquema definido
        em ReminderViewSchema.
    '''
    result = []
    for reminder in reminders:
        result.append({
            'id': reminder.id,
            'name': reminder.name,
            'name_normalized': reminder.name_normalized,
            'description': reminder.description,
            'due_date': reminder.due_date,
            'send_email': reminder.send_email,
            'email': reminder.email_relationship[0].email,
            'recurring': reminder.recurring
        })
    return {'reminders': result}
