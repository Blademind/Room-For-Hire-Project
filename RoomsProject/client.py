import pickle
import time
import tkinter.messagebox
from socket import *
from tkinter import *
import _thread
import sqlite3
from tkintermapview import TkinterMapView

"""
Client by Alon Levy
"""


class Client:
    def __init__(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.BUF = 1024
        self.ADDR = ('127.0.0.1', 50000)  # where to connect
        self.client.connect(self.ADDR)
        self.getfile()
        _thread.start_new_thread(self.listen, ())
        self.__user = ['Guest', None]
        print('___SUCCESS___')
        self.main()

    def getfile(self):
        data = self.client.recv(self.BUF)
        img = pickle.loads(data)
        with open('create.db', 'wb') as txt:
            s = 0
            while s < img:
                data2 = self.client.recv(self.BUF)
                if not data2: break
                txt.write(data2)
                s += len(data2)

    def listen(self):
        while 1:
            data = self.client.recv(self.BUF)
            if not data:
                break
            tkinter.messagebox.showinfo('Message from Server', data.decode())
            if 'Success' in data.decode():
                self.log1.config(text='Logout', command=self.logout)
                self.__user[0] = data.decode()[8:]
                self.__user[1] = self.__attempt
                self.user1.config(text=f'Welcome,\n{self.__user[0]}')

    def main(self):
        self.root = Tk()
        self.root.config(bg='lightgray')
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        reg1 = Button(self.root, command=self.register, text='Register', font=('Helvetica', 11), cursor='hand2',
                      bg='#252221', fg='lightgray', activebackground='lightgray',
                      activeforeground='#252221')
        reg1.grid(column=0, row=0)
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
        self.map.pack(expand=True)
        conn = sqlite3.connect('create.db')
        cursor = conn.cursor().execute('SELECT * FROM Offered')
        self.all = cursor.fetchall()
        conn.close()
        for row in self.all:
            self.cord = row[2].split(' ')
            self.map.set_marker(float(self.cord[0]), float(self.cord[1]), text=row[0], command=lambda *args: self.askroom(row))

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

    def askroom(self, row):
        self.root3 = Tk()
        self.root3.config(bg='#252221')
        f = ('Helvetica', 14)
        right_frame = Frame(self.root3, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame, text="Price", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame, text="When", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)
        Label(right_frame, text="Where", bg='#CCCCCC', font=f).grid(row=3, column=0, sticky=W, pady=10)
        Label(right_frame, text="Recipient", bg='#CCCCCC', font=f).grid(row=4, column=0, sticky=W, pady=10)

        price = Label(right_frame, text=f'{row[3]}', font=f, bg='#CCCCCC')
        when = Label(right_frame, text=f'{row[4]}', font=f, bg='#CCCCCC')
        where = Label(right_frame, text=f'{row[2]}', font=f, bg='#CCCCCC')
        recipient = Label(right_frame, text=f'{row[1]}', font=f, bg='#CCCCCC')
        proceed = Button(right_frame,
                       width=15, text='Proceed', font=('Helvetica', 11), cursor='hand2', bg='#252221', fg='lightgray',
                       activebackground='lightgray',
                       activeforeground='#252221')
        close = Button(right_frame, command=self.root3.destroy, text='Close', width=15, font=('Helvetica', 11), cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        price.grid(row=1, column=1, pady=10, padx=20)
        when.grid(row=2, column=1, pady=10, padx=20)
        where.grid(row=3, column=1, pady=10, padx=20)
        recipient.grid(row=4, column=1, pady=10, padx=20)
        close.grid(row=7, column=1, pady=10, padx=10)
        proceed.grid(row=7, column=0, pady=10, padx=10)
        right_frame.pack()
        self.midwin(self.root3, 600, 250)

    def register(self):
        self.reg = Tk()
        self.reg.config(bg='#252221')
        f = ('Helvetica', 14)
        self.var = StringVar()
        self.right_frame = Frame(self.reg, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(self.right_frame, text="Name", bg='#CCCCCC', font=f).grid(row=0, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Email", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Gender", bg='#CCCCCC', font=f).grid(row=3, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Country", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Password", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Re-Enter Password", bg='#CCCCCC', font=f).grid(row=6, column=0, sticky=W, pady=10)

        self.gender = LabelFrame(self.right_frame, bg='#CCCCCC', padx=10, pady=10, )
        self.name = Entry(self.right_frame, font=f)
        self.email = Entry(self.right_frame, font=f)
        self.country = Entry(self.right_frame, font=f)
        self.male = Radiobutton(self.gender, text='Male', bg='#CCCCCC', variable=self.var, value='male',
                                font=('Times', 10), )
        self.female = Radiobutton(self.gender, text='Female', bg='#CCCCCC', variable=self.var, value='female',
                                  font=('Times', 10))
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

        self.gender.grid(row=3, column=1, pady=10, padx=20)
        self.male.pack(expand=True, side=LEFT)
        self.female.pack(expand=True, side=LEFT)
        self.midwin(self.reg, 500, 400)
        self.reg.mainloop()

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
        Label(right_frame, text="Price", bg='#CCCCCC', font=f).grid(row=3, column=0, sticky=W, pady=10)
        Label(right_frame, text="Dates (from - to)", bg='#CCCCCC', font=f).grid(row=4, column=0, sticky=W, pady=10)

        self.roomname = Entry(right_frame, font=f)
        self.location = Entry(right_frame, font=f)
        self.price = Entry(right_frame, font=f)
        self.duration = Entry(right_frame, font=f)
        add = Button(right_frame,
                     command=self.addsend,
                     width=15, text='Add', font=('Helvetica', 11), cursor='hand2', bg='#252221', fg='lightgray',
                     activebackground='lightgray',
                     activeforeground='#252221')
        close = Button(right_frame, command=self.roomroot.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        self.err = Label(self.roomroot, bg='#CCCCCC', font=f)
        self.roomname.grid(row=1, column=1, pady=10, padx=20)
        self.location.grid(row=2, column=1, pady=10, padx=20)
        self.price.grid(row=3, column=1, pady=10, padx=20)
        self.duration.grid(row=4, column=1, pady=10, padx=20)
        close.grid(row=7, column=1, pady=10, padx=10)
        add.grid(row=7, column=0, pady=10, padx=10)
        right_frame.grid()
        self.err.grid(sticky=W, pady=10)
        self.midwin(self.roomroot, 500, 350)
        self.roomroot.mainloop()

    def addsend(self):
        err = False
        if self.__user[0] != 'Guest':
            temp = TkinterMapView()
            temp.set_address(self.location.get())
            c = temp.get_position()
            if c != (52.516268, 13.377694999999989):
                if self.roomname.get() != '' and self.price.get().isdigit() and self.duration.get() != '':
                    self.client.send(
                        f'ADD {self.roomname.get()}, {c[0]} {c[1]}, {self.price.get()}, {self.duration.get()}, {self.__user[0]}'.encode())
                else:
                    self.err.config(text='values must be valid')
                    err = True
                if not err:
                    conn = sqlite3.connect('create.db')
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT INTO Offered (RoomName, By, Coordination,'
                        ' Price, LendTime) VALUES (?,?,?,?,?)',
                        (self.roomname.get(), self.__user[0], f'{c[0]} {c[1]}', self.price.get(), self.duration.get()))
                    conn.commit()
                    conn.close()
                    self.roomroot.destroy()
            else:
                self.err.config(text='Invalid place')

        else:
            self.err.config(text='Guests cannot add rooms')

    def loginsend(self, email, pwd, log):
        self.client.send('CRED'.encode())
        self.client.send(pickle.dumps([email, pwd]))
        self.__attempt = pwd
        log.destroy()

    def logout(self):
        self.__user = ['Guest', None]
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

    def midwin(self, root, x, y):
        a = int(root.winfo_screenwidth() / 2 - (x / 2))
        b = int(root.winfo_screenheight() / 2 - (y / 2))
        root.geometry('{}x{}+{}+{}'.format(x, y, a, b))


if __name__ == '__main__':
    print('___INITIALIZING___')
    c = Client()
