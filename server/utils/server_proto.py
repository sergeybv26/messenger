"""Главный серверный модуль"""
from asyncio import Protocol
from binascii import hexlify
from hashlib import pbkdf2_hmac

from server.utils.mixins import ConvertMixin, DbInterfaceMixin
from server.utils.server_messages import JimServerMessage


class ChatServerProtocol(Protocol, ConvertMixin, DbInterfaceMixin):
    """Главный серверный класс"""
    def __init__(self, db_path, connections, users):
        super().__init__(db_path)
        self.connections = connections
        self.users = users
        self.jim = JimServerMessage()
        self.user = None
        self.transport = None

    def connection_made(self, transport) -> None:
        self.connections[transport] = {
            'peername': transport.get_extra_info('peername'),
            'username': '',
            'transport': transport
        }
        self.transport = transport

    def authenticate(self, username, password):
        """Аутентификация пользователя"""
        # Проверяем наличие пользователя в базе
        if username and password:
            usr = self.get_client_by_username(username)
            hash_str = pbkdf2_hmac('sha256', password.encode('utf-8'), 'salt'.encode('utf-8'), 100000)
            hashed_password = hexlify(hash_str)
            if usr:
                # Пользователь существует
                if hashed_password == usr.password:
                    # Делаем запись в историю входов
                    self.add_client_history(username)
                    return True
                else:
                    return False
            else:
                # Добавляем нового пользователя
                print('new user')
                self.add_client(username, hashed_password)
                # Делаем запись в историю входов
                self.add_client_history(username)
                return True
        return False

    def data_received(self, data: bytes) -> None:
        _data = self._bytes_to_dict(data)
        if _data:
            try:
                if _data['action'] == 'presence':
                    if _data['user']['account_name']:
                        response_msg = self.jim.response(code=200)
                        self.transport.write(self._dict_to_bytes(response_msg))
                    else:
                        response_msg = self.jim.response(code=500, error='wrong presence msg')
                        self.transport.write(self._dict_to_bytes(response_msg))
                elif _data['action'] == 'authenticate':
                    if self.authenticate(
                        _data['user']['account_name'],
                        _data['user']['password']
                    ):
                        if _data['user']['account_name'] not in self.users:
                            self.user = _data['user']['account_name']
                            self.connections[self.transport]['username'] = self.user
                            self.users[_data['user']['account_name']] = self.connections[self.transport]
                            self.set_user_online(_data['user']['account_name'])
                        response_msg = self.jim.probe(self.user)
                        self.users[_data['user']['account_name']]['transport'].write(self._dict_to_bytes(response_msg))
                    else:
                        response_msg = self.jim.response(code=402, error='wrong login/password')
                        self.transport.write(self._dict_to_bytes(response_msg))
            except Exception as err:
                response_msg = self.jim.response(code=500, error=err)
                self.transport.write(self._dict_to_bytes(response_msg))
        else:
            response_msg = self.jim.response(code=403, error='Вы отправили сообщение без данных')
            self.transport.write(self._dict_to_bytes(response_msg))
