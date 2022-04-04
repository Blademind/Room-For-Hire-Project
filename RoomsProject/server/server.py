import _thread
import pickle
import socket
import time
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
        self.conn = sqlite3.connect('Databases/users.db')
        self.conn2 = sqlite3.connect('Databases/create.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS Registered(Fullname TEXT, Email TEXT, Gender TEXT,'
                            ' Country TEXT, Password TEXT);')
        self.cursor2 = self.conn2.cursor()
        self.cursor2.execute('CREATE TABLE IF NOT EXISTS Offered(RoomName TEXT,By TEXT, Coordinates TEXT,'
                             ' Price INT, First TEXT, Last TEXT, ImagePath TEXT, Bought BIT, Buyer TEXT, RATING INT);')
        self.conn.close()
        self.conn2.close()
        self.lst = os.listdir('Images/')
        threading.Thread(target=self.listen).start()
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
        with open(f'Images/{name}', 'wb') as txt:
            s = 0
            while s != img:
                data2 = sock.recv(self.BUF)
                if not data2: break
                txt.write(data2)
                s += len(data2)

    def timer(self, row):
        time.sleep(60)
        if row in self.occ:
            self.occ.remove(row)

    def listen(self):
        while 1:
            read, write, ex = select.select(self.readables, self.writeables, [])
            for sock in read:
                if sock == self.server:
                    client, addr = self.server.accept()
                    print(f'{addr} Connected')
                    client.send(pickle.dumps(self.lst))
                    self.readables.append(client)
                    self.writeables.append(client)
                    _thread.start_new_thread(self.sendimages, (client,))
                else:
                    try:
                        data = sock.recv(self.BUF)
                    except:
                        print(f'{sock.getpeername()} Disconnected')
                        self.readables.remove(sock)
                        self.writeables.remove(sock)
                        break
                    if not data:
                        break
                    try:
                        datacontent = data.decode()
                    except:
                        datacontent = ""
                    if 'ADD' in datacontent:
                        values = datacontent[4:].split(', ')
                        _thread.start_new_thread(self.getfile, (sock, values[6]))
                        self.conn2 = sqlite3.connect('Databases/create.db')
                        cursor = self.conn2.cursor()
                        cursor.execute(
                            'INSERT INTO Offered (RoomName, By, Coordinates,'
                            ' Price, First, Last, ImagePath, Bought, Buyer) VALUES (?,?,?,?,?,?,?,0,"None")',
                            (values[0], values[5], values[1], values[2], values[3], values[4], values[6]))
                        self.conn2.commit()
                        self.conn2.close()
                        _thread.start_new_thread(self.broadcast_files, ())
                    elif datacontent == 'CRED':
                        data = sock.recv(self.BUF)
                        try:
                            data = pickle.loads(data)
                            if type(data) == list and len(data) == 5:  # register detected
                                self.registeruser(data)
                            elif type(data) == list and len(data) == 2:  # login detected
                                room, rec = self.loginuser(data)
                                sock.send(pickle.dumps(rec))
                            sock.send(f'Success {data[0]}'.encode())
                        except Exception as e:
                            print(e)
                            sock.send('Error'.encode())
                    elif datacontent == 'BUY':
                        data = sock.recv(self.BUF)
                        data = pickle.loads(data)
                        self.conn2 = sqlite3.connect('Databases/create.db')
                        cursor = self.conn2.cursor()
                        cursor.execute(f'UPDATE Offered SET Bought=?, Buyer=?, First=?, Last=? WHERE Coordinates=?',
                                       (1, data[len(data) - 1], data[4], data[5], data[2]))
                        self.conn2.commit()
                        self.conn2.close()
                    elif datacontent == 'OCC':
                        data = sock.recv(self.BUF)
                        data = pickle.loads(data)
                        if data not in self.occ:
                            self.occ.append(data)
                            _thread.start_new_thread(self.timer, (data,))
                        else:
                            sock.send('DESTROY'.encode())
                    elif datacontent == 'REM':
                        data = sock.recv(self.BUF)
                        data = pickle.loads(data)
                        if data in self.occ:
                            self.occ.remove(data)
                    elif datacontent == 'UPDATE':
                        data = sock.recv(self.BUF)
                        data = pickle.loads(data)
                        self.conn = sqlite3.connect('Databases/create.db')
                        self.conn.cursor().execute(f'UPDATE Offered SET Bought=0 WHERE RoomName={data[0]}')
                        self.conn.commit()
                        self.conn.close()

    def broadcast_files(self):
        for sock in self.writeables:
            if sock != self.server:
                sock.send('FILES'.encode())
                for name in self.lst:
                    with open(f'Images/{name}', 'rb') as txt:
                        length = os.path.getsize(f'Images/{name}')
                        send = pickle.dumps(length)
                        s = 0
                        sock.send(send)
                        while s != length:
                            data = txt.read(self.BUF)
                            sock.send(data)
                            s += len(data)
                    time.sleep(0.01)
                    self.sendcords(sock)

    def loginuser(self, cred):
        self.conn = sqlite3.connect('Databases/users.db')
        cursor2 = self.conn.cursor().execute(f'SELECT * FROM Registered WHERE Email=? AND Password=?',
                                             (cred[0], cred[1]))
        self.conn.commit()
        data = cursor2.fetchone()
        if len(data) == 0:
            raise ValueError
        self.conn.close()
        self.conn2 = sqlite3.connect('Databases/create.db')
        cursor2 = self.conn2.cursor().execute(f'SELECT * FROM Offered WHERE Bought=1 AND Buyer="{cred[0]}"')
        rec = cursor2.fetchall()
        self.conn2.close()
        return data, rec

    def registeruser(self, cred):
        self.conn = sqlite3.connect('Databases/users.db')
        cursor = self.conn.cursor()
        cursor2 = self.conn.cursor().execute(f'SELECT * FROM Registered WHERE Email=?', (cred[2],))
        self.conn.commit()
        data = cursor2.fetchall()
        if len(data) != 0:
            raise ValueError
        cursor.execute(
            'INSERT INTO Registered (Fullname, Email, Gender, Country, Password) VALUES (?,?,?,?,?)',
            (cred[0], cred[1], cred[2], cred[3], cred[4]))
        self.conn.commit()
        self.conn.close()

    def addroom(self, room):
        self.rooms.append(room)

    def removeroom(self, room):
        self.rooms.remove(room)

    def getrooms(self):
        print(self.rooms)

    def sendimages(self, sock):
        for name in self.lst:
            with open(f'Images/{name}', 'rb') as txt:
                length = os.path.getsize(f'Images/{name}')
                send = pickle.dumps(length)
                s = 0
                sock.send(send)
                while s != length:
                    data = txt.read(self.BUF)
                    sock.send(data)
                    s += len(data)
            time.sleep(0.01)
        self.sendcords(sock)


if __name__ == '__main__':
    print('___INITIALIZING___')
    s = Server()
