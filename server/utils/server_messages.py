"""Конструктор сообщений от сервера"""
from datetime import datetime


class JimServerMessage:
    """Класс, содержащий сообщения по протоколу JIM"""

    def probe(self, sender, status='Are you there?'):
        """Формирование сообщения проверки присутствия"""
        data = {
            'action': 'probe',
            'time': datetime.now().timestamp(),
            'type': 'status',
            'user': {
                'account_name': sender,
                'status': status
            }
        }
        return data

    def response(self, code=None, error=None):
        """Формирование сообщения-ответа от сервера"""

        _data = {
            'action': 'response',
            'code': code,
            'time': datetime.now().timestamp(),
            'error': error
        }

        return _data
