import pickle
import time
from socket import *
from tkinter import *
import threading


class Client:
    def __init__(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.__BUF = 1024
        self.__ADDR = ('127.0.0.1', 50001)

    def connect(self):
        self.client.connect(self.__ADDR)
        threading.Thread(target=self.main).start()
        threading.Thread(target=self.listen).start()

    def listen(self):
        while 1:
            data = self.client.recv(self.__BUF)
            print(data.decode())

    def main(self):
        while 1:
            room = int(input('Room?: '))
            try:
                self.client.send(pickle.dumps(room))
            except:
                pass


print('initializing')
c = Client()
c.connect()