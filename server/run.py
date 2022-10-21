"""Модуль запуска для сервера"""
from argparse import ArgumentParser
from asyncio import get_event_loop, set_event_loop
from sys import argv

from quamash import QEventLoop
from PyQt5.QtWidgets import QApplication

from server.server_config import PORT, DB_PATH
from server.ui.windows import ServerMonitorWindow
from server.utils.server_proto import ChatServerProtocol


class ConsoleServerApp:
    """Класс раннер сервера"""

    def __init__(self, parsed_args, db_path):
        self.args = parsed_args
        self.db_path = db_path
        self.ins = None

    def main(self):
        """главный метод класса-раннера"""
        connections = {}
        users = {}
        loop = get_event_loop()

        self.ins = ChatServerProtocol(self.db_path, connections, users)
        coro = loop.create_server(lambda: self.ins, self.args['addr'], self.args['port'])
        server = loop.run_until_complete(coro)

        print('Server on {} : {}'.format(*server.sockets[0].getsockname()))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


class GuiServerApp:
    """Класс раннера сервера с графическим интерфейсом"""
    def __init__(self, parsed_args, db_path):
        self.args = parsed_args
        self.db_path = db_path
        self.ins = None

    def main(self):
        """Главный метод"""
        connections = {}
        users = {}

        self.ins = ChatServerProtocol(self.db_path, connections, users)

        app = QApplication(argv)
        loop = QEventLoop(app)
        set_event_loop(loop)
        wnd = ServerMonitorWindow()
        wnd.show()

        with loop:
            coro = loop.create_server(lambda: self.ins, self.args['addr'], self.args['port'])
            server = loop.run_until_complete(coro)
            print('Server on {} : {}'.format(*server.sockets[0].getsockname()))

            try:
                loop.run_forever()
            except KeyboardInterrupt:
                pass
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()


def parse_and_run():
    """Осуществляет парсинг аргументов и запускает сервер"""

    def parse_args():
        """Парсит аргументы"""
        parser = ArgumentParser(description='Server settings')
        parser.add_argument('--addr', default='127.0.0.1', type=str)
        parser.add_argument('--port', default=PORT, type=int)
        parser.add_argument('--nogui', action='store_true')

        return vars(parser.parse_args())

    args = parse_args()

    if args['nogui']:
        # Запускаем консольный сервер
        app = ConsoleServerApp(args, DB_PATH)
        app.main()
    else:
        app = GuiServerApp(args, DB_PATH)
        app.main()


if __name__ == '__main__':
    parse_and_run()
