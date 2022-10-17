"""Главный клиентский модуль"""
from asyncio import Protocol, CancelledError
from binascii import hexlify
from hashlib import pbkdf2_hmac
from sys import stdout

from client.utils.client_messages import JimClientMessage
from client.utils.mixins import ConvertMixin, DbInterfaceMixin


class ChatClientProtocol(Protocol, ConvertMixin, DbInterfaceMixin):
    """Главный клиентский класс"""
    def __init__(self, db_path, loop, username=None, password=None, gui_instance=None, **kwargs):
        super().__init__(db_path)
        self.user = username
        self.password = password
        self.jim = JimClientMessage()

        self.conn_is_open = False
        self.loop = loop
        self.sockname = None
        self.transport = None
        self.output = None

    def connection_made(self, transport) -> None:
        self.sockname = transport.get_extra_info('sockname')
        self.transport = transport
        self.send_auth(self.user, self.password)
        self.conn_is_open = True

    def send_auth(self, user, password):
        """Отправляет сообщение об аутентификации на сервер"""
        if user and password:
            self.transport.write(self._dict_to_bytes(self.jim.auth(user, password)))

    def data_received(self, data: bytes) -> None:
        """Получает данные от сервера и выводит сообщение в консоль или GUI"""
        msg = self._bytes_to_dict(data)
        if msg:
            try:
                if msg['action'] == 'probe':
                    self.transport.write(self._dict_to_bytes(self.jim.presence(
                        self.user, status=f'Подключение от {self.sockname[0]}:{self.sockname[1]}')))
                elif msg['action'] == 'response':
                    if msg['code'] == 200:
                        pass
                    elif msg['code'] == 402:
                        self.connection_lost(CancelledError)
                    else:
                        self.output(msg)
            except Exception as err:
                print(err)

    async def get_from_console(self):
        """Осуществляет вывод поступающих данных в консоль"""
        while not self.conn_is_open:
            pass
        self.output = self.output_to_console
        self.output(f'{self.user} подключен к {self.sockname[0]}:{self.sockname[1]}\n')

        while True:
            content = await self.loop.run_in_executor(None, input)

    def output_to_console(self, data):
        """Печатает данные в консоли"""
        _data = data
        stdout.write(_data)


class ClientAuth(ConvertMixin, DbInterfaceMixin):
    """Класс для аутентификации клиента"""
    def __init__(self, db_path, username=None, password=None):
        super().__init__(db_path)
        self.username = username
        self.password = password

    def authenticate(self):
        """Метод аутентификации, который проверяет пользователя в БД"""
        if self.username and self.password:
            usr = self.get_client_by_username(self.username)
            dk = pbkdf2_hmac('sha256', self.password.encode('utf-8'), 'salt'.encode('utf-8'), 100000)
            hashed_password = hexlify(dk)

            if usr:
                if hashed_password == usr.password:
                    self.add_client_history(self.username)
                    return True
                else:
                    return False
            else:
                print('new user')
                self.add_client(self.username, hashed_password)
                self.add_client_history(self.username)
                return True
        return False
