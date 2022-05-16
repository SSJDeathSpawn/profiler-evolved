from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import logging
    from concurrent.futures import Future

from logging_module.custom_logging import get_logger
from graphics.plot import add_plot, update_ds, get_plot


class Server(object):
    """Class handling the server side operations"""

    _header: int = 256
    _format: str = 'utf-8'
    _disconnect_msg: str = '!DISCONNECT'

    def __init__(self: Server, host: str = '', port: int = 2000) -> Server:
        self.logger: logging.Logger = get_logger('server')
        
        self.host: str = host
        self.port: int = port
        self.address: tuple[str, int] = (self.host, self.port)

        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)

        self.executor: ThreadPoolExecutor = ThreadPoolExecutor()
        self.connections: list[Future] = []

        self.running: bool = True

        self.logger.info(f'starting server')

    def shutdown(self: Server) -> None:
        """Shuts down the server"""

        self.running = False
        for connection in self.connections:
            connection.result()
        self.socket.close()

    def runserver(self: Server) -> None:
        """Runs the server"""

        self.socket.listen()
        self.logger.info(f'server is listening at {self.host}:{self.port}')

        try:
            while self.running:
                conn, addr = self.socket.accept()

                # msg = conn.recv(Server._header)
                # self.logger.info(f'{addr}: {msg.decode(Server._format)}')

                self.connections.append(self.executor.submit(self.handle_client, conn, addr))
                self.logger.info(f'{addr} connected')
                self.logger.info(f'active connections: {len(self.connections)}')
        except KeyboardInterrupt:
            self.logger.info(f'shutting down server')
            self.shutdown()

    def handle_client(self: Server, conn: socket.socket, addr: str) -> None:
        """Handles a client"""

        title = ''
        ds = None

        while self.running:
            msg = conn.recv(Server._header).decode(Server._format)


            if msg == Server._disconnect_msg:
                break

            elif len(msg.split(' ')) != 2:
                conn.send('!ERROR invalid message'.encode(Server._format))
                continue

            first, second = msg.split(' ')
            

            try:
                number = float(first)

            except ValueError:
                if title:
                    self.logger.warning(f'Already have title')
                    conn.send('!ERROR unneeded starter'.encode(Server._format))
                    continue
                try:
                    if not isinstance(first, str):
                        raise ValueError
                    title = first
                    initial = float(second)
                except [ValueError, IndexError]:
                    conn.send('!ERROR invalid starter'.encode(Server._format))
                    continue
                else:
                    ds = add_plot(title, (0, 50), (0, 5), initial)
                    conn.send('!SUCCESS'.encode(Server._format))

            else:
                if not title:
                    self.logger.warning(f'Unknown plot')
                    conn.send('!ERROR needed starter'.encode(Server._format))
                    continue
                try:
                    step = int(second)
                except ValueError:
                    self.logger.warning(f'{msg} is not a number')
                    conn.send('!ERROR invalid update'.encode(Server._format))
                else:
                    update_ds(title, ds, number, step)
                    conn.send('!SUCCESS'.encode(Server._format))

        conn.close()
        self.logger.info(f'{addr} disconnected')
    