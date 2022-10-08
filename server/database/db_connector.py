"""Коннектор для работы с базой данных"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DataAccessLayer:
    """Предоставляет доступ к базе данных"""

    def __init__(self, conn_string, base, echo=False):
        self.engine = None
        self.Session = None
        self.session = None
        self.conn_string = conn_string
        self.echo = echo
        self.Base = base

    def connect(self):
        """Создает класс-сессию в привязке к движку"""

        self.engine = create_engine(self.conn_string, echo=self.echo)
        self.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
