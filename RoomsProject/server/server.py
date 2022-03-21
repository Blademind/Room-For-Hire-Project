import pickle
import time
from socket import *
import select
import threading
import sqlite3

"""
Server by Alon Levy
"""
class Server:
    def __init__(self):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(('127.0.0.1', 50000))
        self.server.listen(5)
        self.readables = [self.server]
        self.__BUF = 1024
        self.__PORT = 50000
        self.__rooms = []
        threading.Thread(target=self.listen).start()
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Registered(Fullname TEXT, Email TEXT, Gender TEXT,'
                              ' country TEXT, LastOrder TEXT, Password TEXT);')
        self.conn.close()
        print('___SUCCESS___')

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
                        print(f'{sock.getpeername()} Disconnected')
                        self.readables.remove(sock)
                        break
                    if not data:
                        break
                    try:
                        data = pickle.loads(data)
                        if type(data) == list:
                            self.registeruser(data)
                        sock.send('Success'.encode())
                    except:
                        sock.send('Already taken'.encode())

    def registeruser(self, cred):
        self.conn = sqlite3.connect('users.db')
        cursor = self.conn.cursor()
        cursor2 = self.conn.cursor().execute(f'SELECT * FROM Registered WHERE Email=?', (cred[2],))
        self.conn.commit()
        data = cursor2.fetchall()
        if len(data) != 0:
            raise ValueError
        cursor.execute('INSERT INTO Registered (Fullname, Email, Gender, country, LastOrder, Password) VALUES (?,?,?,?,0,?)', (cred[0],cred[1],cred[2],cred[3],cred[4]))
        self.conn.commit()
        self.conn.close()

    def addroom(self, room):
        self.__rooms.append(room)

    def removeroom(self, room):
        self.__rooms.remove(room)

    def getrooms(self):
        print(self.__rooms)


if __name__ == '__main__':
    print('___INITIALIZING___')
    s = Server()
