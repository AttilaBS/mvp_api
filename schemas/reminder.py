from pydantic import BaseModel, validator
from typing import Optional, List
from model.reminder import Reminder
from model import Session
import re


class ReminderSchema(BaseModel):
    '''
        Define como um novo lembrete a ser persistido deve ser.
    '''
    name: str = 'Trocar o óleo do carro'
    description: str = 'trocar o óleo a cada 10 mil km no Moraes AutoCenter'
    interval: int = 180
    send_email: Optional[bool]
    recurring: Optional[bool]

    @validator('name')
    def validator_name(cls, v):
        if not len(v) > 0:
            raise ValueError('O nome não pode ser vazio!')
        session = Session()
        reminder = session.query(Reminder).filter(Reminder.name == v).first()
        if reminder:
            raise ValueError('Já existe um lembrete de mesmo nome')
        return v
    
    @validator('description')
    def validator_description(cls, v):
        if not len(v) > 0:
            raise ValueError('A descrição não pode ser vazia!')
        return v


class ReminderUpdateSchema(BaseModel):
    '''
        Define como um lembrete a ser atualizado pode ser salvo.
    '''
    id: int
    name: Optional[str]
    description: Optional[str]
    interval: Optional[int]
    send_email: Optional[bool]
    recurring: Optional[bool]

    @validator('name')
    def validator_name(cls, v):
        if not len(v) > 0:
            raise ValueError('O nome não pode ser vazio!')
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
    name: str = 'teste'


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
    id: int = 1
    name: str = 'Trocar o óleo do carro'
    description: str = 'trocar o óleo a cada 10 mil km no Moraes AutoCenter'
    interval: int = 180
    send_email: Optional[bool]
    recurring: Optional[bool]


def show_reminder(reminder: Reminder):
    '''
        Retorna a representação de um lembrete seguindo o esquema definido
        em ReminderViewSchema.
    '''
    return {
        '1-id': reminder.id,
        '2-nome': reminder.name,
        '3-descrição': reminder.description,
        '4-intervalo': reminder.interval,
        '5-enviar email': reminder.send_email,
        '6-recorrente': reminder.recurring
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
            'nome': reminder.name,
            'descrição': reminder.description,
            'intervalo': reminder.interval,
            'enviar email': reminder.send_email,
            'recorrente': reminder.recurring
        })
    return {'lembretes': result}
