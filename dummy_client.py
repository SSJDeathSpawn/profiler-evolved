from __future__ import annotations

import socket
from random import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import logging

from logging_module.custom_logging import get_logger


class Client(object):
    """Dummy client"""

    _header: int = 256
    _format: str = 'utf-8'
    _disconnect_msg: str = '!DISCONNECT'

    def __init__(self: Client, host: str, port: int) -> Client:
        self.logger: logging.Logger = get_logger('client')

        self.host: str = host
        self.port: int = port
        self.address: tuple[str, int] = (self.host, self.port)

        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)

    def recv(self: Client) -> None:
        """Receives a message"""

        self.logger.info(f'message received: {self.socket.recv(Client._header)}')

    def send_init(self: Client, title: str) -> None:
        """Creates a new plot"""

        self.socket.send(f'{title} 0.5'.encode(Client._format))
        self.recv()

    def update_plot(self: Client) -> None:
        """Update the plot"""

        self.socket.send(f'{random()} 1'.encode(Client._format))
        self.recv()
