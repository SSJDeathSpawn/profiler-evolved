from threading import Thread
from networking.server import Server

server = Server('localhost')

thread = Thread(target=server.runserver)
thread.start()
