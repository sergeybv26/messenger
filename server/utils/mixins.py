"""Миксины для приложения"""
import json

from server.database.controller import ClientMessages
from server.database.models import CBase
from server.server_config import ENCODING


class DbInterfaceMixin:
    """Миксин для операций с базой данных"""

    def __init__(self, db_path):
        self._cm = ClientMessages(db_path, CBase, echo=False)

    def add_client(self, username, password, info=None):
        """Добавление клиента"""
        return self._cm.add_client(username, password, info)

    def get_client_by_username(self, username):
        """Получение клиента по имени"""
        return self._cm.get_client_by_username(username)

    def add_client_history(self, client_username, ip_addr='8.8.8.8'):
        """Добавление истории клиента"""
        return self._cm.add_client_history(client_username, ip_addr)

    def set_user_online(self, client_username):
        """У пользователя устанавливает статус онлайн"""
        return self._cm.set_user_online(client_username)


class ConvertMixin:
    """Миксин для конвертации сообщений"""

    def _dict_to_bytes(self, msg_dict):
        """
        Преобразование словаря в байты
        :param msg_dict: словарь
        :return: bytes
        """
        if isinstance(msg_dict, dict):
            json_message = json.dumps(msg_dict)
            byte_message = json_message.encode(ENCODING)
            return byte_message
        raise TypeError

    def _bytes_to_dict(self, msg_bytes):
        """
        Получение словаря из байтов
        :param msg_bytes: сообщение в виде байтов
        :return: словарь сообщения
        """
        if isinstance(msg_bytes, bytes):
            json_message = msg_bytes.decode(ENCODING)
            message = json.loads(json_message)
            if isinstance(message, dict):
                return message
        raise TypeError
