import _thread
import pickle
import socket
from socket import *
import select
import threading
import sqlite3
import os

"""
Server by Alon Levy
"""

file = __file__


class Server:
    def __init__(self):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(('127.0.0.1', 50000))
        self.server.listen(5)
        self.readables = [self.server]
        self.writeables = [self.server]
        self.BUF = 4096
        self.PORT = 50000
        self.rooms = []
        self.occ = []
        threading.Thread(target=self.listen).start()
        self.conn = sqlite3.connect('Databases/users.db')
        self.conn2 = sqlite3.connect('Databases/create.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Registered(Fullname TEXT, Email TEXT, Gender TEXT,'
                            ' Country TEXT, LastOrder TEXT, Password TEXT);')
        self.cursor2 = self.conn2.cursor()
        self.cursor2.execute('CREATE TABLE IF NOT EXISTS Offered(RoomName TEXT,By TEXT, Coordinates TEXT,'
                             ' Price INT, LendTime TEXT, ImagePath TEXT Bought BIT, Buyer TEXT);')
        self.conn.close()
        self.conn2.close()
        print('___SUCCESS___')

    def sendcords(self, sock):
        with open('Databases/create.db', 'rb') as txt:
            len = os.path.getsize('Databases/create.db')
            send = pickle.dumps(len)
            sock.send(send)
            while 1:
                data = txt.read(self.BUF)
                if not data:
                    break
                sock.send(data)

    def getfile(self, sock, name):
        data = sock.recv(self.BUF)
        img = pickle.loads(data)
        with open(f'{os.path.dirname(file)}/Images/{name}', 'wb') as txt:
            s = 0
            while s < img:
                data2 = sock.recv(self.BUF)
                if not data2: break
                txt.write(data2)
                s += len(data2)

    def listen(self):
        while 1:
            read, write, ex = select.select(self.readables, self.writeables, [])
            for sock in read:
                if sock == self.server:
                    client, addr = self.server.accept()
                    print(f'{addr} Connected')
                    self.readables.append(client)
                    self.writeables.append(client)
                    _thread.start_new_thread(self.sendcords, (client,))
                else:
                    try:
                        data = sock.recv(self.BUF)
                    except:
                        print(f'{sock.getpeername()} Disconnected')
                        self.readables.remove(sock)
                        break
                    if not data:
                        break
                    try:
                        datacontent = data.decode()
                    except:
                        datacontent = ""
                    if 'ADD' in datacontent:
                        values = datacontent[4:].split(', ')
                        _thread.start_new_thread(self.getfile, (sock, values[5]))
                        self.conn2 = sqlite3.connect('Databases/create.db')
                        cursor = self.conn2.cursor()
                        cursor.execute(
                            'INSERT INTO Offered (RoomName, By, Coordinates,'
                            ' Price, LendTime, ImagePath Bought, Buyer) VALUES (?,?,?,?,?,?,0,"None")',
                            (values[0], values[4], values[1], values[2], values[3], values[5]))
                        self.conn2.commit()
                        self.conn2.close()
                        # with open('cords.txt', 'a') as txt:
                        #     txt.write(f'{data.decode()[4:]}\n')
                    elif datacontent == 'CRED':
                        data = sock.recv(self.BUF)
                        try:
                            data = pickle.loads(data)
                            if type(data) == list and len(data) == 5:  # register detected
                                self.registeruser(data)
                            elif type(data) == list and len(data) == 2:  # login detected
                                data = self.loginuser(data)
                            sock.send(f'Success {data[0][1]}'.encode())
                        except:
                            sock.send('Error'.encode())
                    elif datacontent == 'BUY':
                        data = sock.recv(self.BUF)
                        data = pickle.loads(data)
                        self.conn2 = sqlite3.connect('Databases/create.db')
                        cursor = self.conn2.cursor()
                        cursor.execute(f'UPDATE Offered SET Bought=?, Buyer=? WHERE Coordinates=?', (1, data[1], data[2]))
                        self.conn2.commit()
                        self.conn2.close()
                    elif datacontent == 'OCC':
                        data = sock.recv(self.BUF)
                        data = pickle.loads(data)
                        self.occ.append(data)

    def loginuser(self, cred):
        self.conn = sqlite3.connect('Databases/users.db')
        cursor2 = self.conn.cursor().execute(f'SELECT * FROM Registered WHERE Email=? AND Password=?',
                                             (cred[0], cred[1]))
        self.conn.commit()
        data = cursor2.fetchall()
        if len(data) == 0:
            raise ValueError
        self.conn.close()
        return data

    def registeruser(self, cred):
        self.conn = sqlite3.connect('Databases/users.db')
        cursor = self.conn.cursor()
        cursor2 = self.conn.cursor().execute(f'SELECT * FROM Registered WHERE Email=?', (cred[2],))
        self.conn.commit()
        data = cursor2.fetchall()
        if len(data) != 0:
            raise ValueError
        cursor.execute(
            'INSERT INTO Registered (Fullname, Email, Gender, Country, LastOrder, Password) VALUES (?,?,?,?,0,?)',
            (cred[0], cred[1], cred[2], cred[3], cred[4]))
        self.conn.commit()
        self.conn.close()

    def addroom(self, room):
        self.rooms.append(room)

    def removeroom(self, room):
        self.rooms.remove(room)

    def getrooms(self):
        print(self.rooms)


if __name__ == '__main__':
    print('___INITIALIZING___')
    s = Server()
