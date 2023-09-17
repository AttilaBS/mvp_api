from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from model import Base
from model import Email

from logger import logger


class Reminder(Base):
    __tablename__ = 'reminder'

    id = Column('pk_reminder', Integer, primary_key = True)
    name = Column(String(60), unique = True)
    description = Column(String(255))
    due_date = Column(DateTime)
    send_email = Column(Boolean, unique = False, default = False)
    recurring = Column(Boolean, unique = False, default = False)
    created_at = Column(DateTime, default = datetime.now())
    updated_at = Column(DateTime, default = None)
    # relationship with table email
    email_relationship = relationship('Email')

    def __init__(
        self,
        name: str,
        description: str,
        due_date: Union[DateTime, None] = None,
        send_email: bool = False,
        recurring: bool = False,
        created_at: Union[DateTime, None] = None,
        updated_at: Union[DateTime, None] = None):
        self.name = name
        self.description = description
        self.due_date = due_date
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

    def validate_email_before_send(self) -> bool:
        '''
            Function to validate if send_email is True, and if there is
            an email related to the reminder and if due_date is equal
            or less than 24 hours from now.
        '''
        if self.send_email and self.email_relationship[0].email:
            due_date = self.due_date
            start_date = self.updated_at if self.updated_at else self.created_at
            delta = due_date - start_date
            if (delta.days <= 1):
                return True
        return False
