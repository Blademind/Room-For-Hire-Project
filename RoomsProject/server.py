import _thread
import pickle
import time
from socket import *
import select
import threading

class Server:
    def __init__(self):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(('127.0.0.1', 50001))
        self.server.listen(5)
        self.readables = [self.server]
        self.__BUF = 1024
        self.__PORT = 50000
        self.__rooms = []
        threading.Thread(target=self.listen).start()

    def listen(self):
        while 1:
            read, write, ex = select.select(self.readables, [], [])
            for sock in read:
                if sock == self.server:
                    client, addr = self.server.accept()
                    print(f'{addr} Connected')
                    self.readables.append(client)
                else:
                    try:
                        data = sock.recv(self.__BUF)
                    except:
                        print(f'{addr} Disconnected')
                        self.readables.remove(sock)
                        break
                    if not data:
                        break
                    try:
                        room = pickle.loads(data)
                        if room in self.__rooms:
                            raise ValueError
                        self.addroom(room)
                    except:
                        sock.send('Already taken'.encode())

    def addroom(self, room):
        self.__rooms.append(room)

    def getrooms(self):
        print(self.__rooms)


print('initializing')
s = Server()
