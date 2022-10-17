"""Конструктор сообщений от клиента"""
from datetime import datetime


class JimClientMessage:
    """Класс с сообщениями клиента"""
    def auth(self, username, password):
        """
        Сообщение авторизации
        :param username: Имя пользователя
        :param password: Пароль
        :return: Словарь с сообщением к серверу
        """
        data = {
            'action': 'authenticate',
            'time': datetime.now().timestamp(),
            'user': {
                'account_name': username,
                'password': password
            }
        }

        return data

    def presence(self, sender, status='Yep, I am here!'):
        """
        Сообщение о присутствии, которое уведомляет сервер о том, что клиент подключен к сети
        :param sender: Имя пользователя
        :param status: Произвольное сообщение от пользователя
        :return: Словарь с сообщением к серверу
        """
        data = {
            'action': 'presence',
            'time': datetime.now().timestamp(),
            'type': 'status',
            'user': {
                'account_name': sender,
                'status': status
            }
        }

        return data
