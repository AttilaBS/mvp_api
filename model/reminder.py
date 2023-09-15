from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
#from unidecode import unidecode


from model import Base
from model import Email


class Reminder(Base):
    __tablename__ = 'reminder'

    id = Column('pk_reminder', Integer, primary_key = True)
    name = Column(String(60), unique = True)
    description = Column(String(255))
    interval = Column(Integer)
    send_email = Column(Boolean, unique = False, default = False)
    recurring = Column(Boolean, unique = False, default = True)
    created_at = Column(DateTime, default = datetime.now())
    updated_at = Column(DateTime, default = None)
    #relationship
    email_relationship = relationship('Email')

    def __init__(
        self,
        name:str,
        description:str, 
        interval:int,
        send_email:bool = False,
        recurring:bool = True,
        created_at:Union[DateTime, None] = None,
        updated_at:Union[DateTime, None] = None):
        self.name = name
        self.description = description
        self.interval = interval
        self.send_email = send_email
        self.recurring = recurring

        if not created_at:
            self.created_at = created_at
        if not updated_at:
            self.updated_at = updated_at
    
    def insert_email(self, email:Email):
        '''
            Adiciona um email a um lembrete.
        '''
        self.email_relationship.append(email)
