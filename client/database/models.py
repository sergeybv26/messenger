"""
Описание моделей базы данных
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

CBase = declarative_base()


class Client(CBase):
    """
    Таблица с клиентами
    """
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    info = Column(String(255), default='')
    online_status = Column(Boolean, default=False)


class History(CBase):
    """
    Таблица с историей входов пользователей
    """
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.now(), nullable=False)
    ip_addr = Column(String(255))
    client_id = Column(Integer, ForeignKey('client.id'))
    client = relationship('Client', backref=backref('history', order_by=client_id))
