import datetime
import pickle
import re
import shutil
import time
import tkinter.messagebox
from socket import *
from tkinter import *
import _thread
import sqlite3
from tkintermapview import TkinterMapView
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from tkcalendar import DateEntry
import ssl

"""
Client by Alon Levy
This aims to allow user interaction of which
he can personalize and buy rooms.
"""

file = __file__


class Client:
    def __init__(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.BUF = 1024
        self.ADDR = ('192.168.1.197', 50000)  # where to connect
        self.client.connect(self.ADDR)
        self.client = ssl.wrap_socket(self.client, server_side=False, keyfile='privkey.pem', certfile='certificate.pem')

        self.images = pickle.loads(self.client.recv(self.BUF))
        self.getimage()
        self.recorders = []
        self.server = self.client.getpeername()
        _thread.start_new_thread(self.listen, ())
        self.__user = ['Guest', None]
        print('___SUCCESS___')
        self.main()

    def getfile(self):
        data = self.client.recv(self.BUF)
        img = pickle.loads(data)
        with open(f'Databases/database.db', 'wb') as txt:
            s = 0
            while s != img:
                data2 = self.client.recv(self.BUF)
                if not data2: break
                txt.write(data2)
                s += len(data2)

    def getimage(self):
        for name in self.images:
            data = self.client.recv(self.BUF)
            img = pickle.loads(data)
            s = 0
            with open(f'Images/{name}', 'wb') as txt:
                while s != img:
                    data2 = self.client.recv(self.BUF)
                    txt.write(data2)
                    s += len(data2)
        self.getfile()

    def listen(self):
        while 1:
            data = self.client.recv(self.BUF)
            if not data:
                break
            try:
                datacontent = data.decode()
                print(datacontent)
                if datacontent == 'FILES':
                    self.images = pickle.loads(self.client.recv(self.BUF))
                    self.getimage()
                elif 'Success' in datacontent:
                    self.log1.config(text='Logout', command=self.logout)
                    self.recent = Button(self.root,
                                         command=self.orders, text='Recent orders', font=('Helvetica', 11),
                                         cursor='hand2',
                                         bg='#252221', fg='lightgray', activebackground='lightgray',
                                         activeforeground='#252221')
                    self.recent.grid(column=2, row=0, sticky=W)
                    self.reg1.grid_forget()
                    self.__user[0] = data.decode()[8:]
                    self.__user[1] = self.__attempt
                    self.user1.config(text=f'Welcome,\n{self.__user[0]}')
                elif datacontent == 'DESTROY':
                    self.root3.destroy()
                elif datacontent == 'RATE':
                    data = pickle.loads(self.client.recv(self.BUF))
                    self.rating(data[0])
            except:
                self.recorders = pickle.loads(data)

    def rating(self, name):
        rate = Tk()
        var = IntVar()
        rate.config(bg='lightgray')
        lb3 = Label(rate, text=f'How did you like your stay at {name}?', font=("Helvetica", 15), bg='#252221', fg='lightgray')
        lb3.pack(fill=BOTH)
        scale = Scale(rate, from_=1, to=10, bg='#252221', orient=HORIZONTAL, fg='lightgray')
        scale.pack(fill=BOTH,pady=10)
        submit = Button(rate, text='Submit', command=lambda: [self.rate(scale), rate.destroy()], bg='#252221',
                     fg='lightgray', activebackground='lightgray', activeforeground='#252221', padx=10,
                        cursor='hand2')
        submit.pack(pady=10, side=RIGHT)

        no = Button(rate, text='No vote', command=lambda: [self.client.send(pickle.dumps(0)), rate.destroy()], bg='#252221', fg='lightgray', activebackground='lightgray',
                    activeforeground='#252221', padx=10, cursor='hand2')  # Destroy popup window
        no.pack(pady=10, side=RIGHT)
        self.midwin(rate, 350, 150)
        rate.mainloop()

    def rate(self, scale):
        self.client.send(pickle.dumps(scale.get()))
        print(f'SENT {scale.get()}')

    def orders(self):
        if len(self.recorders) != 0:
            self.root5 = Tk()
            orders1 = Listbox(self.root5, font=('Helvetica', 12), bg='#CCCCCC')
            for row in self.recorders:
                orders1.insert(END, row[0])
            orders1.grid()

            close = Button(self.root5,
                           command=self.root5.destroy, text='Close', width=15, font=('Helvetica', 11),
                           cursor='hand2',
                           bg='#252221', fg='lightgray', activebackground='lightgray',
                           activeforeground='#252221')
            close.grid()
            orders1.bind('<Double-1>', lambda event: self.details(self.recorders[orders1.curselection()[0]]))
        else:
            tkinter.messagebox.showinfo(message='You have not placed any order')

    def details(self, line):
        self.root4 = Tk()
        self.root4.config(bg='#252221')
        f = ('Helvetica', 14)
        right_frame = Frame(self.root4, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame, text="Price", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame, text="From", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)
        Label(right_frame, text="Until", bg='#CCCCCC', font=f).grid(row=3, column=0, sticky=W, pady=10)
        Label(right_frame, text="Where", bg='#CCCCCC', font=f).grid(row=4, column=0, sticky=W, pady=10)
        Label(right_frame, text="Recipient", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)
        cord = line[2].split(' ')
        price = Label(right_frame, text=f'{line[3]}', font=f, bg='#CCCCCC')
        when = Label(right_frame, text=f'{line[4]}', font=f, bg='#CCCCCC')
        until = Label(right_frame, text=f'{line[5]}', font=f, bg='#CCCCCC')

        self.where = Label(right_frame, text=f'{format(float(cord[0]), ".2f"), format(float(cord[1]), ".2f")}', font=f,
                           bg='#CCCCCC')
        self.recipient = Label(right_frame, text=f'{line[1]}', font=f, bg='#CCCCCC')
        close = Button(right_frame,
                       command=self.root4.destroy,
                       text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')

        price.grid(row=1, column=1, pady=10, padx=20)
        when.grid(row=2, column=1, pady=10, padx=20)
        until.grid(row=3, column=1, pady=10, padx=20)
        self.where.grid(row=4, column=1, pady=10, padx=20)
        self.recipient.grid(row=5, column=1, pady=10, padx=20)
        close.grid(row=6, column=1, pady=10, padx=20)
        t = datetime.datetime.strptime(line[4], '%d/%m/%Y')
        if t > datetime.datetime.today():
            cancel = Button(right_frame,
                            command=lambda: [self.cancel(line), self.root4.destroy(),self.root5.destroy(), self.orders()],
                            text='Cancel', width=15, font=('Helvetica', 11), cursor='hand2',
                            bg='#252221', fg='lightgray', activebackground='lightgray',
                            activeforeground='#252221')
            cancel.grid(row=6, column=0, pady=10, padx=20)

        right_frame.grid()
        self.root4.mainloop()

    def cancel(self, line):
        self.conn = sqlite3.connect('Databases/database.db')
        self.conn.cursor().execute(f'DELETE FROM Bought WHERE RoomName=? AND Buyer=?;', (line[0], self.__user[0]))
        self.conn.commit()
        self.conn.close()
        self.recorders.remove(line)
        line = list(line)
        line.append(self.__user[0])
        self.client.send('UPDATE'.encode())
        self.client.send(pickle.dumps(line))

    def main(self):
        self.root = Tk()
        self.root.config(bg='lightgray')
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.reg1 = Button(self.root, command=self.register, text='Register', font=('Helvetica', 11), cursor='hand2',
                           bg='#252221', fg='lightgray', activebackground='lightgray', activeforeground='#252221')
        self.reg1.grid(column=0, row=0)
        self.log1 = Button(self.root, command=self.login, text='Login', font=('Helvetica', 11), cursor='hand2',
                           bg='#252221', fg='lightgray', activebackground='lightgray',
                           activeforeground='#252221')
        self.log1.grid(column=1, row=0, sticky=W)
        self.user1 = Label(self.root, text=f'Welcome,\n{self.__user[0]}', font=('Helvetica', 12),
                           bg='#252221', fg='lightgray', activebackground='lightgray',
                           activeforeground='#252221')
        self.user1.grid(column=5, row=0, sticky=E)
        findroom = Button(self.root, command=self.worldrooms, width=25, height=2,
                          text='Find a Room', font=('Helvetica', 14),
                          cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                          activeforeground='#252221')
        findroom.grid(row=1, column=2, pady=10, padx=20)

        addroom = Button(self.root, command=self.addroom, width=25, height=2,
                         text='Add a Room', font=('Helvetica', 14),
                         cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                         activeforeground='#252221')
        addroom.grid(row=2, column=2, pady=20, padx=20)
        close = Button(self.root, command=lambda: self.pop(self.root), text='Close', font=('Helvetica', 11),
                       cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        close.grid(row=3, column=5, sticky=E)
        # menus
        menu = Menu(self.root)
        filemenu = Menu(menu, tearoff=0)
        filemenu.add_command(label='Help')
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=lambda: self.pop(self.root))
        menu.add_cascade(label="More", menu=filemenu)
        self.root.config(menu=menu, bg='lightgray')
        self.midwin(self.root, 900, 500)
        self.root.mainloop()

    def searchplace(self, *args):
        self.map.set_address(self.message.get())
        self.message.delete(0, END)

    def worldrooms(self):
        self.root2 = Toplevel()
        self.root2.bind('<Return>', self.searchplace)
        self.root2.config(bg='lightgray')
        self.root2.geometry('800x600')
        self.map = TkinterMapView(self.root2, width=800, height=550, corner_radius=0)
        self.map.set_address('Israel')
        self.map.set_zoom(7)
        self.map.pack(fill=BOTH)
        conn = sqlite3.connect('Databases/database.db')
        cursor = conn.cursor().execute('SELECT * FROM Offered')
        self.all = cursor.fetchall()
        conn.close()
        for row in self.all:
            self.cord = row[2].split(' ')
            if row[7] != 1:
                mindate = row[4].split('/')
                maxdate = row[5].split('/')
                mindate = datetime.datetime(int(mindate[2]),int(mindate[1]), int(mindate[0]))
                maxdate = datetime.datetime(int(maxdate[2]),int(maxdate[1]), int(maxdate[0]))
                img = ImageTk.PhotoImage(Image.open(f'Images/{row[6]}').resize((300, 200)))
                self.map.set_marker(float(self.cord[0]), float(self.cord[1]), image=img, marker_color_circle="black",
                                    marker_color_outside="gray40", text=row[0], command=lambda here=row: self.askroomtk(here, mindate, maxdate))

        self.message = Entry(self.root2, bg='lightgray', fg='#252221',
                             font=("Helvetica", 15, 'bold'), width=60)  # user entry, sent to server
        self.message.pack(pady=10, side=LEFT)
        self.close2 = Button(self.root2, command=self.root2.destroy, text='Close', font=('Helvetica', 11),
                             cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                             activeforeground='#252221')
        self.close2.pack(pady=10, side=RIGHT)
        self.search = Button(self.root2, command=self.searchplace, text='Search', font=('Helvetica', 11),
                             cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                             activeforeground='#252221')
        self.search.pack(pady=10, side=RIGHT)
        self.midwin(self.root2, 800, 600)
        self.root2.mainloop()

    def askroomtk(self, row, mindate, maxdate):
        for i in self.all:
            if i[2].split(' ')[0] == str(row.position[0]) and i[2].split(' ')[1] == str(row.position[1]):
                self.row = i
                break
        self.root3 = Toplevel()
        self.root3.config(bg='#252221')
        self.client.send('OCC'.encode())
        self.client.send(pickle.dumps(self.row))
        f = ('Helvetica', 14)
        right_frame = Frame(self.root3, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame, text="Price", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame, text="From", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)
        Label(right_frame, text="Until", bg='#CCCCCC', font=f).grid(row=3, column=0, sticky=W, pady=10)
        Label(right_frame, text="Check-in", bg='#CCCCCC', font=f).grid(row=4, column=0, sticky=W, pady=10)
        Label(right_frame, text="Check-out", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)

        cord = self.row[2].split(' ')
        price = Label(right_frame, text=f'{self.row[3]}', font=f, bg='#CCCCCC')
        when = Label(right_frame, text=f'{self.row[4]}', font=f, bg='#CCCCCC')
        until = Label(right_frame, text=f'{self.row[5]}', font=f, bg='#CCCCCC')
        if self.row[len(self.row) - 1] is not None:
            Label(right_frame, text="Rating", bg='#CCCCCC', font=f).grid(row=6, column=0, sticky=W, pady=10)
            rating = Label(right_frame, text=f'{self.row[len(self.row) - 1]} / 10', font=f, bg='#CCCCCC')
            rating.grid(row=6, column=1, pady=10, padx=20)

        self.where = Label(right_frame, text=f'{format(float(cord[0]), ".2f"), format(float(cord[1]), ".2f")}', font=f,
                           bg='#CCCCCC')
        self.recipient = Label(right_frame, text=f'{self.row[1]}', font=f, bg='#CCCCCC')
        self.timer = Label(right_frame, font=('Helvetica', 12),
                           bg='#252221', fg='lightgray', activebackground='lightgray',
                           activeforeground='#252221')
        self.timer.grid(column=8, row=0, sticky=E)
        self.duration1 = DateEntry(right_frame, font=f, locale='en_IL', date_pattern='dd/mm/yyyy',
                                   mindate=mindate, maxdate=maxdate, showweeknumbers=0)
        self.duration2 = DateEntry(right_frame, font=f, locale='en_IL', date_pattern='dd/mm/yyyy',
                                   mindate=mindate, maxdate=maxdate, showweeknumbers=0)
        proceed = Button(right_frame,
                         width=15, text='Proceed', command=self.askroom, font=('Helvetica', 11), cursor='hand2',
                         bg='#252221', fg='lightgray',
                         activebackground='lightgray',
                         activeforeground='#252221')
        close = Button(right_frame,
                       command=lambda: [self.removeinst(self.row),
                                        self.root3.destroy()], text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        price.grid(row=1, column=1, pady=10, padx=20)
        when.grid(row=2, column=1, pady=10, padx=20)
        until.grid(row=3, column=1, pady=10, padx=20)
        self.where.grid(row=4, column=1, pady=10, padx=20)
        self.recipient.grid(row=5, column=1, pady=10, padx=20)
        self.duration1.grid(row=4, column=1, pady=10)
        self.duration2.grid(row=5, column=1, pady=10)
        close.grid(row=7, column=1, pady=10, padx=10)
        proceed.grid(row=7, column=0, pady=10, padx=10)
        right_frame.grid()
        self.update_clock(60)
        self.root3.mainloop()

    def removeinst(self, row):
        self.client.send('REM'.encode())
        self.client.send(pickle.dumps(row))

    def askroom(self):
        if self.__user[0] == 'Guest':
            self.guestmail()
        elif self.duration1.get_date() <= self.duration2.get_date():
            conn = sqlite3.connect('Databases/database.db')
            cursor = conn.cursor().execute('SELECT First, Last FROM Bought WHERE RoomName=?', (self.row[0],))
            dates = cursor.fetchall()
            final_dates1 = []
            final_dates2 = []
            flag = True
            for date in dates:
                start = datetime.datetime.strptime(date[0], '%d/%m/%Y')
                finish = datetime.datetime.strptime(date[1], '%d/%m/%Y')
                while start <= finish:
                    final_dates1.append(start.date())
                    start += datetime.timedelta(days=1)
            start = self.duration1.get_date()
            finish = self.duration2.get_date()
            while start <= finish:
                final_dates2.append(start)
                start += datetime.timedelta(days=1)
            for i in final_dates2:
                if i in final_dates1:
                    flag = False
                    break
            if flag:
                conn.cursor().execute('INSERT INTO Bought(RoomName, Buyer, First, Last)  '
                                      'VALUES(?,?,?,?)',
                                      (self.row[0], self.__user[0], self.duration1.get_date().strftime('%d/%m/%Y'),
                                       self.duration2.get_date().strftime('%d/%m/%Y')))
                conn.commit()
                conn.close()
                self.row = list(self.row)
                self.recorders.append(self.row)
                self.row[4], self.row[5] = self.duration1.get_date().strftime(
                    '%d/%m/%Y'), self.duration2.get_date().strftime('%d/%m/%Y')
                self.row.append(self.__user[0])
                self.client.send('BUY'.encode())
                self.client.send(pickle.dumps(self.row))
                self.root3.destroy()
                self.row = None
            else:
                tkinter.messagebox.showinfo(message='The selected date is taken')
            self.removeinst(self.row)

    def guestmail(self):
        self.root6 = Tk()
        self.root6.config(bg='#252221')
        f = ('Helvetica', 14)
        self.right_frame2 = Frame(self.root6, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(self.right_frame2, text="Email", bg='#CCCCCC', font=f).grid(row=0, column=0, sticky=W, pady=10)
        self.name = Entry(self.right_frame2, font=f)
        submit = Button(self.right_frame2,
                          command=lambda: self.submitguestname(self.name.get()),
                          width=15, text='Submit', font=('Helvetica', 11), cursor='hand2', bg='#252221',
                          fg='lightgray', activebackground='lightgray',
                          activeforeground='#252221')
        close = Button(self.right_frame2, command=self.root6.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        self.name.grid(row=0, column=1, pady=10, padx=20)
        close.grid(row=1, column=1, pady=10, padx=10)
        submit.grid(row=1, column=0, pady=10, padx=10)
        self.right_frame2.pack()
        self.midwin(self.root6, 500, 250)

    def submitguestname(self, mail):
        self.__user[0] = mail
        self.root6.destroy()
        self.askroom()

    def register(self):
        self.reg = Tk()
        self.var = StringVar()
        self.reg.config(bg='#252221')
        f = ('Helvetica', 14)
        self.right_frame = Frame(self.reg, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(self.right_frame, text="Name", bg='#CCCCCC', font=f).grid(row=0, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Email", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Country", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Password", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Re-Enter Password", bg='#CCCCCC', font=f).grid(row=6, column=0, sticky=W, pady=10)
        self.name = Entry(self.right_frame, font=f)
        self.email = Entry(self.right_frame, font=f)
        self.country = Entry(self.right_frame, font=f)
        self.pwd = Entry(self.right_frame, font=f, show='*')
        self.pwd_again = Entry(self.right_frame, font=f, show='*')

        register = Button(self.right_frame,
                          command=self.regsend,
                          width=15, text='Register', font=('Helvetica', 11), cursor='hand2', bg='#252221',
                          fg='lightgray', activebackground='lightgray',
                          activeforeground='#252221')
        close = Button(self.right_frame, command=self.reg.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        self.name.grid(row=0, column=1, pady=10, padx=20)
        self.email.grid(row=1, column=1, pady=10, padx=20)
        self.country.grid(row=2, column=1, pady=10, padx=20)
        self.pwd.grid(row=5, column=1, pady=10, padx=20)
        self.pwd_again.grid(row=6, column=1, pady=10, padx=20)
        close.grid(row=7, column=1, pady=10, padx=10)
        register.grid(row=7, column=0, pady=10, padx=10)
        self.right_frame.pack()

        self.midwin(self.reg, 500, 350)

        self.reg.mainloop()

    def update_clock(self, c):
        flag = True
        if c >= 0:
            try:
                self.timer.config(text=c)
            except:
                flag = False
        else:
            self.root3.destroy()
            flag = False
        if flag:
            self.root.after(1000, lambda: self.update_clock(c - 1))

    def regsend(self):
        self.client.send('CRED'.encode())
        self.client.send(
            pickle.dumps([self.name.get(), self.email.get(), self.country.get(), self.var.get(), self.pwd.get()]))
        self.__attempt = self.pwd
        self.reg.destroy()

    def login(self):
        log = Tk()
        log.config(bg='#252221')
        f = ('Helvetica', 14)
        var = StringVar()
        right_frame = Frame(log, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame, text="Email", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame, text="Password", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)

        email = Entry(right_frame, font=f)
        pwd = Entry(right_frame, font=f, show='*')
        login = Button(right_frame,
                       command=lambda: [self.loginsend(email.get(), pwd.get(), log)],
                       width=15, text='Login', font=('Helvetica', 11), cursor='hand2', bg='#252221', fg='lightgray',
                       activebackground='lightgray',
                       activeforeground='#252221')
        close = Button(right_frame, command=log.destroy, text='Close', width=15, font=('Helvetica', 11), cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        email.grid(row=1, column=1, pady=10, padx=20)
        pwd.grid(row=5, column=1, pady=10, padx=20)
        close.grid(row=7, column=1, pady=10, padx=10)
        login.grid(row=7, column=0, pady=10, padx=10)
        right_frame.pack()
        self.midwin(log, 500, 200)
        log.mainloop()

    def addroom(self):
        self.roomroot = Tk()
        self.roomroot.config(bg='#252221')
        f = ('Helvetica', 14)
        var = StringVar()
        Label(self.roomroot, text="Add a Room", bg='#CCCCCC', font=f).grid(row=0, column=0, sticky=W, pady=10)
        right_frame = Frame(self.roomroot, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame, text="Room name", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame, text="Location", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)
        Label(right_frame, text="Price (per night)", bg='#CCCCCC', font=f).grid(row=3, column=0, sticky=W, pady=10)
        Label(right_frame, text="Check-in", bg='#CCCCCC', font=f).grid(row=4, column=0, sticky=W, pady=10)
        Label(right_frame, text="Check-out", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)

        Button(right_frame, text="Choose image", command=self.addfile, font=f, bg='#252221', fg='lightgray',
               cursor='hand2',
               activebackground='lightgray', activeforeground='#252221').grid(row=6, column=0, sticky=W, pady=10)

        self.roomname = Entry(right_frame, font=f)
        self.location = Entry(right_frame, font=f)
        self.price = Entry(right_frame, font=f)
        self.duration1 = DateEntry(right_frame, font=f, locale='en_IL', date_pattern='dd/mm/yyyy',
                                   mindate=datetime.datetime.now(), showweeknumbers=0)
        self.duration2 = DateEntry(right_frame, font=f, locale='en_IL', date_pattern='dd/mm/yyyy',
                                   mindate=datetime.datetime.now(), showweeknumbers=0)
        add = Button(right_frame,
                     command=self.addsend,
                     width=15, text='Add', font=('Helvetica', 11), cursor='hand2', bg='#252221', fg='lightgray',
                     activebackground='lightgray',
                     activeforeground='#252221')
        close = Button(right_frame, command=self.roomroot.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        self.message = Label(self.roomroot, bg='#252221', font=f)
        self.roomname.grid(row=1, column=1, pady=10, padx=20)
        self.location.grid(row=2, column=1, pady=10, padx=20)
        self.price.grid(row=3, column=1, pady=10, padx=20)
        self.duration1.grid(row=4, column=1, pady=10)
        self.duration2.grid(row=5, column=1, pady=10)
        close.grid(row=7, column=1, pady=10, padx=10)
        add.grid(row=7, column=0, pady=10, padx=10)
        right_frame.grid()
        self.message.grid(sticky=W, pady=10)
        self.midwin(self.roomroot, 500, 480)
        self.roomroot.mainloop()

    def addfile(self):
        self.roomroot.attributes('-topmost', False)
        self.filename = filedialog.askopenfilename(filetypes=[('image files', '.png'), ('image files', '.jpg')], )
        self.message.config(text=f'image: {self.filename}', bg='#CCCCCC')
        self.roomroot.attributes('-topmost', True)

    def addsend(self):
        err = False
        try:
            self.filename
        except:
            self.filename = ''
        if self.filename == '':
            self.message.config(text='No image selected', bg='#CCCCCC')
        elif self.duration1.get_date() > self.duration2.get_date():
            self.message.config(text='Invalid date range', bg='#CCCCCC')
        elif self.__user[0] != 'Guest':
            self.duration = (self.duration1.get_date().strftime('%d/%m/%Y'), self.duration2.get_date().strftime('%d/%m/%Y'))
            shutil.copy(self.filename, f'Images/{self.filename[self.filename.rfind("/") + 1:]}')
            temp = TkinterMapView()
            temp.set_address(self.location.get())
            c = temp.get_position()
            if c != (52.516268, 13.377694999999989):  # non-generic only
                if self.roomname.get() != '' and self.price.get().isdigit():
                    self.client.send(
                        f'ADD {self.roomname.get()}, {c[0]} {c[1]},'
                        f' {int(self.price.get()) * (int(abs((self.duration1.get_date() - self.duration2.get_date())).days) + 1)},'
                        f' {self.duration[0]}, {self.duration[1]}'
                        f', {self.__user[0]}, {self.filename[self.filename.rfind("/") + 1:]}'.encode())
                    self.sendimage()
                else:
                    self.message.config(text='values must be valid', bg='#CCCCCC')
                    err = True
                if not err:
                    conn = sqlite3.connect('Databases/database.db')
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO Offered (RoomName, By, Coordinates,'
                        ' Price, First, Last, ImagePath) VALUES (?,?,?,?,?,?,?)',
                        (self.roomname.get(), self.__user[0], f'{c[0]} {c[1]}',
                         int(self.price.get()) * (
                                     int(abs((self.duration1.get_date() - self.duration2.get_date())).days) + 1),
                         self.duration[0],
                         self.duration[1], self.filename[self.filename.rfind("/") + 1:]))
                    conn.commit()
                    conn.close()
                    self.roomroot.destroy()
            else:
                self.message.config(text='Invalid place', bg='#CCCCCC')

        else:
            self.message.config(text='Guests cannot add rooms', bg='#CCCCCC')

    def loginsend(self, email, pwd, log):
        self.client.send('CRED'.encode())
        self.client.send(pickle.dumps([email, pwd]))
        self.__attempt = pwd
        log.destroy()

    def logout(self):
        self.__user = ['Guest', None]
        self.recorders = []
        self.root.destroy()
        self.main()

    # Do you wish to exit the program entirely?
    def pop(self, root):
        popup = Tk()
        popup.config(bg='lightgray')
        lb3 = Label(popup, text='Do you wish to exit?', font=("Helvetica", 15), bg='#252221', fg='lightgray')
        lb3.pack(fill=BOTH)
        # Destroy both popup and root windows
        yes = Button(popup, text='Yes', command=lambda: [popup.destroy(), root.destroy()], bg='#252221',
                     fg='lightgray', activebackground='lightgray', activeforeground='#252221', padx=10, cursor='hand2')
        yes.pack(pady=10, side=RIGHT)

        no = Button(popup, text='No', command=popup.destroy, bg='#252221', fg='lightgray', activebackground='lightgray',
                    activeforeground='#252221', padx=10, cursor='hand2')  # Destroy popup window
        no.pack(pady=10, side=RIGHT)
        self.midwin(popup, 300, 80)  # place window in the center

    # window placed middle
    def midwin(self, root, x, y):
        a = int(root.winfo_screenwidth() / 2 - (x / 2))
        b = int(root.winfo_screenheight() / 2 - (y / 2))
        root.geometry('{}x{}+{}+{}'.format(x, y, a, b))

    # send an image
    def sendimage(self):
        with open(self.filename, 'rb') as txt:
            length = os.path.getsize(self.filename)
            send = pickle.dumps(length)
            self.client.send(send)
            s = 0
            while s != length:
                data = txt.read(self.BUF)
                s += len(data)
                self.client.send(data)

if __name__ == '__main__':
    print('___INITIALIZING___')
    try:
        c = Client()
    except ConnectionRefusedError:
        print('COULD NOT CONNECT')
