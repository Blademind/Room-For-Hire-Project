import _thread
import datetime
import pickle
import socket
import time
from socket import *
import select
import threading
import sqlite3
import os
import ssl

"""
Server by Alon Levy
"""

file = __file__


class Server:
    def __init__(self):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server = ssl.wrap_socket(self.server, server_side=True, keyfile='privkey.pem', certfile='certificate.pem')
        self.server.bind(('192.168.1.197', 50000))
        self.server.listen(5)
        self.readables = [self.server]
        self.writeables = [self.server]
        self.BUF = 8192
        self.PORT = 50000
        self.rooms = []
        self.occ = []
        self.conn = sqlite3.connect('Databases/database.db')
        self.conn.cursor().execute('CREATE TABLE IF NOT EXISTS Registered(Fullname TEXT, Email TEXT, Gender TEXT,'
                            ' Country TEXT, Password TEXT);')
        self.conn.cursor().execute('CREATE TABLE IF NOT EXISTS Offered(RoomName TEXT,By TEXT, Coordinates TEXT,'
                             ' Price INT, First TEXT, Last TEXT, ImagePath TEXT, RATING INT);')
        self.conn.cursor().execute('CREATE TABLE IF NOT EXISTS Bought(RoomName TEXT, '
                             'Buyer TEXT, First TEXT, Last TEXT, RATING INT);')
        self.conn.close()
        self.lst = os.listdir('Images/')
        threading.Thread(target=self.listen).start()
        print('___SUCCESS___')

    def sendfile(self, sock):
        filename = 'Databases/database.db'
        with open(filename, 'rb') as txt:
            length = os.path.getsize(filename)
            send = pickle.dumps(length)
            sock.send(send)
            s = 0
            while s != length:
                    data = txt.read(self.BUF)
                    s += len(data)
                    sock.send(data)

    def getfile(self, sock, name):
        sock.settimeout(None)
        data = sock.recv(self.BUF)
        img = pickle.loads(data)
        s = 0
        with open(f'Images/{name}', 'wb') as txt:
            while s != img:
                data2 = sock.recv(self.BUF)
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
                    self.sendimages(client,)
                else:
                    try:
                        data = sock.recv(self.BUF)
                    except ConnectionResetError:
                        print(f'{sock.getpeername()} Disconnected')
                        self.readables.remove(sock)
                        self.writeables.remove(sock)
                        break
                    if not data:
                        print('123')
                        break
                    try:
                        datacontent = data.decode()
                    except:
                        datacontent = ""
                    if 'ADD' in datacontent:
                        values = datacontent[4:].split(', ')
                        self.getfile(sock, values[6])
                        self.conn2 = sqlite3.connect('Databases/database.db')
                        cursor = self.conn2.cursor()
                        cursor.execute(
                            'INSERT INTO Offered (RoomName, By, Coordinates,'
                            ' Price, First, Last, ImagePath) VALUES (?,?,?,?,?,?,?)',
                            (values[0], values[5], values[1], values[2], values[3], values[4], values[6]))
                        self.conn2.commit()
                        self.conn2.close()
                        _thread.start_new_thread(self.broadcast_files, (sock,))
                    elif datacontent == 'CRED':
                        data = sock.recv(self.BUF)
                        try:
                            data = pickle.loads(data)
                            if type(data) == list and len(data) == 5:  # register detected
                                self.registeruser(data)
                            elif type(data) == list and len(data) == 2:  # login detected
                                room, ret, specific_order = self.loginuser(data)
                                sock.send(pickle.dumps(ret))
                                _thread.start_new_thread(self.user_rate, (ret, sock, specific_order))

                            sock.send(f'Success {data[0]}'.encode())
                        except Exception as e:
                            print(e)
                            sock.send('Error'.encode())
                    elif datacontent == 'BUY':
                        data = sock.recv(self.BUF)
                        data = pickle.loads(data)
                        self.conn2 = sqlite3.connect('Databases/database.db')
                        self.conn2.cursor().execute('INSERT INTO Bought(RoomName, Buyer, First, Last)  '
                                              'VALUES(?,?,?,?)',
                                       (data[0], data[len(data) - 1], data[4], data[5]))
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
                        self.conn = sqlite3.connect('Databases/database.db')
                        self.conn.cursor().execute(f'DELETE FROM Bought WHERE RoomName=? AND Buyer=?;', (data[0], data[len(data) - 1]))
                        self.conn.commit()
                        self.conn.close()

    def broadcast_files(self, ignore):
        self.lst = os.listdir('Images/')
        for sock in self.writeables:
            if sock != self.server and sock != ignore:
                sock.send('FILES'.encode())
                sock.send(pickle.dumps(os.listdir('Images/')))
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
                self.sendfile(sock)

    def user_rate(self, rec, sock, specific_order):
        sock.settimeout(None)
        print(specific_order)
        for order in range(len(rec)):
            dur = datetime.datetime.strptime(rec[order][5], '%d/%m/%Y')
            if datetime.datetime.today() >= dur and specific_order[order][4] is None:
                sock.send('RATE'.encode())
                time.sleep(0.1)
                sock.send(pickle.dumps(rec[order]))
                rating = pickle.loads(sock.recv(self.BUF))
                self.conn = sqlite3.connect('Databases/database.db')
                self.conn.cursor().execute(f'UPDATE Bought SET RATING={rating} WHERE RoomName="{rec[order][0]}"')
                self.conn.commit()
                self.conn.close()
                self.update_total_rating(rec[order][0])

    def update_total_rating(self, name):
        self.conn = sqlite3.connect('Databases/database.db')
        all_rates = self.conn.cursor().execute('SELECT RATING FROM Bought WHERE RoomName=?', (name,)).fetchall()
        subtotal = 0
        for rate in all_rates:
            subtotal += rate[0]
        self.conn.cursor().execute(f'UPDATE Offered SET RATING=? WHERE RoomName=?', (subtotal / len(all_rates), name))
        self.conn.commit()
        self.conn.close()

    def loginuser(self, cred):
        self.conn = sqlite3.connect('Databases/database.db')
        cursor = self.conn.cursor().execute('SELECT * FROM Registered WHERE Email=? AND Password=?',
                                             (cred[0], cred[1]))
        self.conn.commit()
        data = cursor.fetchone()
        if len(data) == 0:
            raise ValueError
        cursor = self.conn.cursor().execute(f'SELECT * FROM Bought WHERE Buyer="{cred[0]}"')
        all = cursor.fetchall()
        self.conn.close()
        ret = []
        for i in all:
            cursor2 = self.conn2.cursor().execute(f'SELECT * FROM Offered WHERE RoomName="{i[0]}"')
            rec = cursor2.fetchone()
            rec = list(rec)
            rec[4], rec[5] = i[2], i[3]
            ret.append(rec)
        return data, ret, all

    def registeruser(self, cred):
        self.conn = sqlite3.connect('Databases/database.db')
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
                    s += len(data)
                    sock.send(data)
        _thread.start_new_thread(self.sendfile, (sock,))


if __name__ == '__main__':
    print('___INITIALIZING___')
    s = Server()
