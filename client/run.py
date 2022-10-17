"""Модуль запуска для клиента"""
from argparse import ArgumentParser
from asyncio import get_event_loop

from client.client_config import PORT, DB_PATH
from client.utils.client_proto import ClientAuth, ChatClientProtocol


class ConsoleClientApp:
    """Класс консольного клиента"""
    def __init__(self, parsed_args, db_path):
        self.args = parsed_args
        self.db_path = db_path
        self.ins = None

    def main(self):
        """Главный метод"""
        loop = get_event_loop()
        auth = ClientAuth(db_path=self.db_path)
        while True:
            usr = self.args['user'] or input('Введите имя пользователя: ')
            password = self.args['password'] or input('Введите пароль: ')
            auth.username = usr
            auth.password = password
            is_auth = auth.authenticate()
            if is_auth:
                break
            print('Неверный логин или/и пароль!')

        tasks = []
        client_ = ChatClientProtocol(db_path=self.db_path,
                                     loop=loop,
                                     username=usr,
                                     password=password)

        try:
            coro = loop.create_connection(lambda: client_, self.args['addr'], self.args['port'])
            transport, protocol = loop.run_until_complete(coro)
        except ConnectionRefusedError:
            print('Error. Wrong server')
            exit(1)

        try:
            task = loop.create_task(client_.get_from_console())
            tasks.append(task)
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            pass
        except Exception as err:
            print(err)
        finally:
            loop.close()


def parse_and_run():
    """Осуществляет парсинг аргументов и запускает клиент"""
    def parse_args():
        """Парсит аргументы"""
        parser = ArgumentParser(description='Client settings')
        parser.add_argument('--user', default='user1', type=str)
        parser.add_argument('--password', default='123', type=str)
        parser.add_argument('--addr', default='127.0.0.1', type=str)
        parser.add_argument('--port', default=PORT, type=int)
        parser.add_argument('--nogui', action='store_true')
        return vars(parser.parse_args())

    args = parse_args()

    if args['nogui']:
        app = ConsoleClientApp(args, DB_PATH)
        app.main()


if __name__ == '__main__':
    parse_and_run()
