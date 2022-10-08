"""Константы для конфигурации сервера"""
from pathlib import Path

HOME = str(Path.home())

PORT = 14908
ENCODING = 'utf-8'

DB_PROTOCOL = 'sqlite:///'
DB_NAME = '/client_contacts.db'
DB_PATH = DB_PROTOCOL + HOME + DB_NAME
