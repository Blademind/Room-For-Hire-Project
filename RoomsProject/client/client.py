import datetime
import math
import pickle
import re
import shutil
import socket
import sys
import time
import tkinter.messagebox
from socket import *
from tkinter import *
import _thread
import sqlite3
import tkintermapview
from tkintermapview import TkinterMapView
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from tkcalendar import DateEntry
import ssl
from tkinter import ttk
"""
Client by Alon Levy
This aims to allow user interaction of which
he can personalize and buy rooms.
"""

file = __file__


class Client:
    def __init__(self):
        self.servertime = datetime.datetime.today().date()
        self.client = socket(AF_INET, SOCK_STREAM)
        self.BUF = 2048
        self.ADDR = ('127.0.0.1', 50000)  # where to connect
        self.client.connect(self.ADDR)
        self.client = ssl.wrap_socket(self.client, server_side=False, keyfile='privkey.pem', certfile='certificate.pem')
        self.images = pickle.loads(self.client.recv(self.BUF))
        self.attraction_images = pickle.loads(self.client.recv(self.BUF))
        self.getimage()
        self.recorders = []
        self.server = self.client.getpeername()
        _thread.start_new_thread(self.listen, ())
        self.__user = ['Guest', None]
        self.__creds = None
        print('___SUCCESS___')
        self.main()

    def get_database(self, name):
        data = self.client.recv(self.BUF)
        img = pickle.loads(data)
        with open(f'Databases/{name}.db', 'wb') as txt:
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
        for name in self.attraction_images:
            data = self.client.recv(self.BUF)
            img = pickle.loads(data)
            s = 0
            with open(f'Attractions_images/{name}', 'wb') as txt:
                while s != img:
                    data2 = self.client.recv(self.BUF)
                    txt.write(data2)
                    s += len(data2)
        self.get_database('database')

    def listen(self):
        while 1:
            data = self.client.recv(self.BUF)
            if not data:
                break
            try:
                datacontent = data.decode()
                if datacontent == 'FILES':
                    self.images = pickle.loads(self.client.recv(self.BUF))
                    self.attraction_images = pickle.loads((self.client.recv(self.BUF)))
                    self.getimage()
                elif 'Error:' in datacontent or 'Exists:' in datacontent or 'Success:' in datacontent:  # Errors, Successes
                    if 'Success:' in datacontent:
                        tkinter.messagebox.showinfo(message=datacontent)
                    else:
                        tkinter.messagebox.showerror(message=datacontent)
                elif 'Success' in datacontent:  # successfully connected user
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
                    tkinter.messagebox.showinfo(message='Success')
                elif datacontent == 'DESTROY':
                    self.root3.destroy()
                    self.root3 = None
                    tkinter.messagebox.showinfo(message='The room is currently being watched')
                elif datacontent == 'RATE':
                    data = pickle.loads(self.client.recv(self.BUF))
                    self.rating(data[0])
                elif datacontent == 'DATE':
                    self.servertime = pickle.loads(self.client.recv(self.BUF))
                    if self.__user[0] != 'Guest':
                        self.client.send('RATE'.encode())
                        self.client.send(pickle.dumps(self.__user))
            except Exception as e:
                print(e)
                try:
                    if type(pickle.loads(data)[0]) is not bool:
                        self.recorders = pickle.loads(data)[0]
                    else:  # CHECK RESULTS
                        if pickle.loads(data)[0]:  # if passed room check
                            self.purchase_screen(pickle.loads(data)[1])  # (total)
                        else:
                            tkinter.messagebox.showinfo(self.root3, message='The selected date is taken')
                            self.removeinst(self.row)
                except:
                    tkinter.messagebox.showinfo(message='Please use Admin interface')
                    self.root.destroy()

    def rating(self, name):
        rate = Tk()
        rate.config(bg='lightgray')
        lb3 = Label(rate, text=f'How did you like your stay at {name}?', font=("Helvetica", 15), bg='#252221',
                    fg='lightgray')
        lb3.pack(fill=BOTH)
        scale = Scale(rate, from_=1, to=10, bg='#252221', orient=HORIZONTAL, fg='lightgray')
        scale.pack(fill=BOTH, pady=10)
        submit = Button(rate, text='Submit', command=lambda: [self.rate(scale.get(), name), rate.destroy()], bg='#252221',
                        fg='lightgray', activebackground='lightgray', activeforeground='#252221', padx=10,
                        cursor='hand2')
        submit.pack(pady=10, side=RIGHT)

        no = Button(rate, text='No vote', command=lambda: [self.rate(0, name), rate.destroy()],
                    bg='#252221', fg='lightgray', activebackground='lightgray',
                    activeforeground='#252221', padx=10, cursor='hand2')  # Destroy popup window
        no.pack(pady=10, side=RIGHT)
        self.midwin(rate, 350, 150)
        rate.mainloop()

    def rate(self, scale, name):
        self.client.send('RATING'.encode())
        self.client.send(pickle.dumps([scale, name, self.__user[0]]))
        print(f'SENT {scale}')

    def orders(self):
        if len(self.recorders) != 0:
            self.root5 = Tk()
            self.root5.resizable(False, False)
            f = ('Helvetica', 12)
            Label(self.root5, text='Room Name', font=f, bg='#252221', fg='lightgray').grid(sticky=NSEW)
            orders1 = Listbox(self.root5, font=f, bg='#CCCCCC')
            for row in self.recorders:
                orders1.insert(END, row[0])
            orders1.grid()

            close = Button(self.root5,
                           command=self.root5.destroy, text='Close', width=15, font=('Helvetica', 11),
                           cursor='hand2',
                           bg='#252221', fg='lightgray', activebackground='lightgray',
                           activeforeground='#252221')
            close.grid()
            scrollbar = ttk.Scrollbar(self.root5, orient=VERTICAL, command=orders1.yview)
            orders1.configure(yscrollcommand=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky='ns',rowspan=2)
            orders1.bind('<Double-1>', lambda event: self.details(self.recorders[orders1.curselection()[0]]))
        else:
            tkinter.messagebox.showinfo(message='You have not placed any order')

    def details(self, line):
        self.root4 = Tk()
        self.root4.config(bg='#252221')
        f = ('Helvetica', 14)
        right_frame = Frame(self.root4, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame, text="Price", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame, text="Check-in", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)
        Label(right_frame, text="Check-out", bg='#CCCCCC', font=f).grid(row=3, column=0, sticky=W, pady=10)
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
        if t.date() > self.servertime:
            cancel = Button(right_frame,
                            command=lambda: [self.cancel(line), tkinter.messagebox.showinfo(message='Cancelled'), self.root4.destroy(), self.root5.destroy(),
                                             self.orders()],
                            text='Cancel', width=15, font=('Helvetica', 11), cursor='hand2',
                            bg='#252221', fg='lightgray', activebackground='lightgray',
                            activeforeground='#252221')
            cancel.grid(row=6, column=0, pady=10, padx=20)

        right_frame.grid()
        self.root4.mainloop()

    def cancel(self, line):
        self.recorders.remove(line)
        line = list(line)
        line.append(self.__user[0])
        self.client.send('UPDATE'.encode())
        self.client.send(pickle.dumps(line))

    def clear(self, root):
        """Clear all widgets within a root"""
        for widget in root.winfo_children():
            widget.destroy()

    def main(self):
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.pop)
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
        findroom = Button(self.root, command=lambda: self.worldrooms("Normal", True), width=25, height=2,
                          text='Find a Room', font=('Helvetica', 14),
                          cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                          activeforeground='#252221')
        findroom.grid(row=1, column=2, pady=10, padx=20)

        addroom = Button(self.root, command=self.addroom, width=25, height=2,
                         text='Add a Room', font=('Helvetica', 14),
                         cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                         activeforeground='#252221')
        addroom.grid(row=2, column=2, pady=20, padx=20)
        close = Button(self.root, command=lambda: self.pop(), text='Close', font=('Helvetica', 11),
                       cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        close.grid(row=3, column=5, sticky=E)
        # menus
        menu = Menu(self.root)
        filemenu = Menu(menu, tearoff=0)
        filemenu.add_command(label='Help')
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=lambda: self.pop())
        menu.add_cascade(label="More", menu=filemenu)
        self.root.config(menu=menu, bg='lightgray')
        self.midwin(self.root, 900, 500)
        self.root.mainloop()

    def searchplace(self, *args):
        self.map.set_address(self.message.get())
        self.message.delete(0, END)

    def worldrooms(self, mode, flag):
        """Map of the world showing all locations added and ready / not ready for purchase"""
        self.world_active = True
        if flag:
            self.root2 = Toplevel()
        self.root2.grid_columnconfigure(0, weight=1)
        self.root2.grid_columnconfigure(1, weight=1)
        self.root2.grid_rowconfigure(0, weight=1)
        self.val = StringVar(self.root2)
        self.val.set("Sort by")
        self.root2.bind('<Return>', self.searchplace)
        self.root2.config(bg='lightgray')
        self.root2.geometry('800x600')
        self.map = TkinterMapView(self.root2, width=800, height=550, corner_radius=0)
        self.map.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22) \
            if mode == 'Normal' else self.map.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map.set_address('Israel')
        self.map.set_zoom(7)
        self.map.grid(row=0, column=0, sticky='nsew')
        conn = sqlite3.connect('Databases/database.db')
        cursor = conn.cursor().execute('SELECT * FROM Offered')
        self.all = cursor.fetchall()
        cursor = conn.cursor().execute('SELECT * FROM Attractions')
        self.all_attractions = cursor.fetchall()
        conn.close()
        self.dict_closeby = {}
        self.dict_closeby = dict.fromkeys(self.all_attractions, [])
        for attraction in self.all_attractions:
            self.dict_closeby[attraction] = []
        for attraction in self.all_attractions:
            for place in self.all:
                if self.check_radius(place, attraction):
                    self.dict_closeby[attraction].append(place)
        for row in self.all:
            self.cord = row[2].split(' ')
            if len(self.recorders) == 0 or any(row[0] != element[0] for element in self.recorders):  # Did the user already buy the room?
                mindate = row[4].split('/')
                maxdate = row[5].split('/')
                mindate = datetime.datetime(int(mindate[2]), int(mindate[1]), int(mindate[0]))
                maxdate = datetime.datetime(int(maxdate[2]), int(maxdate[1]), int(maxdate[0]))
                img = ImageTk.PhotoImage(Image.open(f'Images/{row[6]}').resize((150, 150)), master=self.root2)
                self.map.set_marker(float(self.cord[0]), float(self.cord[1]), image=img,
                                    image_zoom_visibility=(5, 22),
                                    marker_color_circle="black",
                                    marker_color_outside="gray40", text=row[0],
                                    command=lambda row=row, mindate=mindate, maxdate=maxdate: self.askroomtk(row, mindate, maxdate))
        for row in self.all_attractions:
            self.cord = row[1].split(' ')
            img = ImageTk.PhotoImage(Image.open(f'Attractions_images/{row[2]}').resize((150, 150)), master=self.root2)
            marker = self.map.set_marker(float(self.cord[0]), float(self.cord[1]), image=img,
                                image_zoom_visibility=(5, 22),
                                marker_color_circle="white",
                                marker_color_outside="gray40", command=lambda here=row: self.marker_interaction(here))
            marker.hide_image(True)

        options = OptionMenu(self.root2, self.val, *["Price(ASC.)", "Price(DESC.)", "Proximity(ASC.)", *[attraction[0] for attraction in self.dict_closeby.keys()]], command=self.display_selected)
        options.grid(row=0, column=1, sticky='new', columnspan=2)
        self.orders2 = Listbox(self.root2, font=('Helvetica', 12), bg='#CCCCCC')
        self.orders2.grid(row=0, column=1, columnspan=2,sticky='nsew', pady=30)
        self.orders2.bind('<Double-1>', lambda event: [[self.map.set_address(sub[2]), self.map.set_zoom(10)]
                                                       for sub in self.all if len(self.orders2.curselection()) != 0 and
                                                       self.orders2.get(self.orders2.curselection()[0]) == sub[0]])
        mode = Button(self.root2, command=lambda: self.change_map_mode(mode), text='Satellite' if mode == 'Normal' else 'Normal', font=('Helvetica', 11),
                             cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                             activeforeground='#252221')
        mode.grid(row=0, column=1,sticky="se")
        self.message = Entry(self.root2, bg='lightgray', fg='#252221',
                             font=("Helvetica", 15, 'bold'), width=60)  # user entry, sent to server
        self.message.grid(row=1, column=0, pady=10, sticky='we')
        self.message.focus()
        self.close2 = Button(self.root2, command=self.close_map, text='Close', font=('Helvetica', 11),
                             cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                             activeforeground='#252221')
        self.close2.grid(row=1, column=2, pady=10,sticky='e')
        self.search = Button(self.root2, command=self.searchplace, text='Search', font=('Helvetica', 11),
                             cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                             activeforeground='#252221')
        self.search.grid(row=1, column=1, pady=10, sticky='e')
        self.midwin(self.root2, 900, 600)
        self.root2.mainloop()

    def close_map(self):
        self.world_active = False
        self.root2.destroy()

    def change_map_mode(self, mode):
        if mode.cget('text') == "Satellite":
            self.clear(self.root2)
            self.worldrooms("Satellite", False)
        else:
            self.clear(self.root2)
            self.worldrooms("Normal", False)

    def distance(self, a):
        current = self.map.get_position()
        return math.sqrt((float(a[0]) - current[0]) ** 2 + (float(a[1])-current[1]) ** 2)

    def display_selected(self, choice):
        self.close = True
        self.orders2.delete(0, END)
        choice = self.val.get()
        conn = sqlite3.connect('Databases/database.db')
        if choice == 'Price(ASC.)':
            cursor = conn.execute('SELECT * FROM Offered ORDER BY Price;')
            sort = cursor.fetchall()
            for item in sort:
                self.orders2.insert(END, item[0])
            conn.close()
        elif choice == 'Price(DESC.)':
            cursor = conn.execute('SELECT * FROM Offered ORDER BY Price DESC;')
            sort = cursor.fetchall()
            for item in sort:
                self.orders2.insert(END, item[0])
            conn.close()
        elif choice == 'Proximity(ASC.)':
            self.close = False
            cursor = conn.execute('SELECT Coordinates FROM Offered;')
            data = cursor.fetchall()
            conn.close()
            _thread.start_new_thread(self.update_on_move, (data,))
        else:
            for item in self.all_attractions:
                if item[0] == choice:
                    place = item
                    break
            for item in self.dict_closeby[place]:
                if len(item) != 0:
                    self.orders2.insert(END, item[0])

    def update_on_move(self, data):
        last2 = None
        while 1:
            if self.close:
                break
            sort = [i[0].split(' ') for i in data]
            locations = sorted([s for s in sort], key=self.distance)
            locations = [' '.join(i) for i in locations]
            if locations != last2:
                self.orders2.delete(0, END)
                for location in locations:
                    for place in self.all:
                        if location in place:
                            self.orders2.insert(END, place[0])
                            break
                last2 = locations
            time.sleep(1)

    def askroomtk(self, row, mindate, maxdate):
        try:  # does an active root exist?
            self.root3
        except:
            self.root3 = None
        if self.root3 is None:
            for i in self.all:
                if i[2].split(' ')[0] == str(row.position[0]) and i[2].split(' ')[1] == str(row.position[1]):
                    self.row = i
                    break
            self.root3 = Tk()
            self.root3.protocol("WM_DELETE_WINDOW", lambda: [self.removeinst(self.row),
                                            self.root3.destroy(), self.reset_root3()])
            self.root3.config(bg='#252221')
            self.client.send('OCC'.encode())
            self.client.send(pickle.dumps(self.row))
            f = ('Helvetica', 14)
            right_frame = Frame(self.root3, bd=2, bg='#CCCCCC', padx=10, pady=10)
            image = Image.open(f'Images/{self.row[6]}').resize((200, 200))
            img = ImageTk.PhotoImage(image, master=self.root3)
            panel = Label(right_frame, image=img)
            panel.grid(row=3, rowspan=3, column=0, padx=10)
            Label(right_frame, text="Price (per night)", bg='#CCCCCC', font=f).grid(row=1, column=1, sticky=W, pady=10)
            Label(right_frame, text="Conditions", bg='#CCCCCC', font=f).grid(row=2, column=1, sticky=W, pady=10)
            Label(right_frame, text="Check-in", bg='#CCCCCC', font=f).grid(row=3, column=1, sticky=W, pady=10)
            Label(right_frame, text="Check-out", bg='#CCCCCC', font=f).grid(row=4, column=1, sticky=W, pady=10)
            Label(right_frame, text="Where", bg='#CCCCCC', font=f).grid(row=5, column=1, sticky=W, pady=10)
            Label(right_frame, text="Recipient", bg='#CCCCCC', font=f).grid(row=6, column=1, sticky=W, pady=10)

            cord = self.row[2].split(' ')
            conditions = Label(right_frame, text=f'{self.row[8]}', font=f, bg='#CCCCCC')
            price = Label(right_frame, text=f'{self.row[3]}', font=f, bg='#CCCCCC')
            when = Label(right_frame, text=f'{self.row[4]}', font=f, bg='#CCCCCC')
            until = Label(right_frame, text=f'{self.row[5]}', font=f, bg='#CCCCCC')
            if self.row[-2] is not None:
                Label(right_frame, text="Rating", bg='#CCCCCC', font=f).grid(row=7, column=1, sticky=W, pady=10)
                rating = Label(right_frame, text=f'{self.row[-2]} / 10', font=f, bg='#CCCCCC')
                rating.grid(row=7, column=2, pady=10, padx=20)
            self.where = Label(right_frame, text=f'{tkintermapview.convert_coordinates_to_address(float(cord[0]), float(cord[1])).street}',
                               font=f,
                               bg='#CCCCCC')
            self.recipient = Label(right_frame, text=f'{self.row[1]}', font=f, bg='#CCCCCC')
            self.timer = Label(right_frame, font=('Helvetica', 12),
                               bg='#252221', fg='lightgray', activebackground='lightgray',
                               activeforeground='#252221')
            self.timer.grid(column=8, row=0, sticky=E)
            self.duration1 = DateEntry(right_frame, font=f, locale='en_IL', date_pattern='dd/mm/yyyy',
                                       mindate=mindate if mindate > datetime.datetime.today() else datetime.datetime.today(), maxdate=maxdate, showweeknumbers=0)
            self.duration2 = DateEntry(right_frame, font=f, locale='en_IL', date_pattern='dd/mm/yyyy',
                                       mindate=mindate if mindate > datetime.datetime.today() else datetime.datetime.today(), maxdate=maxdate, showweeknumbers=0)
            proceed = Button(right_frame,
                             width=15, text='Proceed', command=self.askroom, font=('Helvetica', 11), cursor='hand2',
                             bg='#252221', fg='lightgray',
                             activebackground='lightgray',
                             activeforeground='#252221')
            close = Button(right_frame,
                           command=lambda: [self.removeinst(self.row),
                                            self.root3.destroy(), self.reset_root3()], text='Close', width=15,
                           font=('Helvetica', 11),
                           cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                           activeforeground='#252221')
            price.grid(row=1, column=2, pady=10, padx=20)
            conditions.grid(row=2, column=2, pady=10, padx=20)
            self.duration1.grid(row=3, column=2, pady=10)
            self.duration2.grid(row=4, column=2, pady=10)
            self.where.grid(row=5, column=2, pady=10, padx=20)
            self.recipient.grid(row=6, column=2, pady=10, padx=20)
            close.grid(row=8, column=2, pady=10, padx=10)
            proceed.grid(row=8, column=1, pady=10, padx=10)
            right_frame.grid()
            self.update_clock(60)
            self.root3.mainloop()

    def removeinst(self, row):
        self.client.send('REM'.encode())
        self.client.send(pickle.dumps(row))

    def marker_interaction(self, marker):
        if marker.image_hidden is True:
            marker.hide_image(False)
        else:
            marker.hide_image(True)

    def reset_root3(self):
        self.root3 = None

    def askroom(self):
        if self.__user[0] == 'Guest':
            self.guestmail()
        elif self.duration1.get_date() < self.duration2.get_date():
            self.client.send('CHECK'.encode())
            self.client.send(pickle.dumps((self.row, self.duration1.get_date(), self.duration2.get_date())))

    def guestmail(self):
        self.root6 = Tk()
        self.root6.config(bg='#252221')
        f = ('Helvetica', 14)
        self.right_frame2 = Frame(self.root6, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(self.right_frame2, text="Email", bg='#CCCCCC', font=f).grid(row=0, column=0, sticky=W, pady=10)
        self.name = Entry(self.right_frame2, font=f)
        message = Label(self.right_frame2, bg='#CCCCCC', font=f)
        submit = Button(self.right_frame2,
                        command=lambda: self.submitguestname(self.name.get(), message),
                        width=15, text='Submit', font=('Helvetica', 11), cursor='hand2', bg='#252221',
                        fg='lightgray', activebackground='lightgray',
                        activeforeground='#252221')
        close = Button(self.right_frame2, command=self.root6.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        self.name.grid(row=0, column=1, sticky=W, pady=10)
        message.grid(row=1, column=0, sticky=W, pady=10)
        close.grid(row=2, column=1, pady=10, padx=10)
        submit.grid(row=2, column=0, pady=10, padx=10)

        self.right_frame2.pack()
        self.midwin(self.root6, 500, 250)

    def submitguestname(self, mail, message):
        mail_re = re.compile('^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$')
        if mail_re.match(mail) is None:
            message.config(text="Invalid Email", bg='#252221', fg='#CCCCCC')
        else:
            self.__user[0] = mail
            self.root6.destroy()
            self.askroom()

    def register(self):
        self.reg = Tk()
        self.reg.bind('<Return>', self.register_send)
        self.reg.config(bg='#252221')
        f = ('Helvetica', 14)

        self.right_frame = Frame(self.reg, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(self.right_frame, width=10, text='Register', bg='#252221', fg='#CCCCCC', font=f).grid(row=0, columnspan=2, sticky='nswe')
        Label(self.right_frame, text="Name", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Email", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Country", bg='#CCCCCC', font=f).grid(row=3, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Password", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)
        Label(self.right_frame, text="Re-Enter Password", bg='#CCCCCC', font=f).grid(row=6, column=0, sticky=W, pady=10)
        name = Entry(self.right_frame, font=f)
        email = Entry(self.right_frame, font=f)
        country = Entry(self.right_frame, font=f)
        pwd = Entry(self.right_frame, font=f, show='*')
        pwd_again = Entry(self.right_frame, font=f, show='*')
        message = Label(self.reg, bg='#252221', font=f)

        register = Button(self.right_frame,
                          command=lambda: self.register_send(name, email,country, pwd, pwd_again, message),
                          width=15, text='Register', font=('Helvetica', 11), cursor='hand2', bg='#252221',
                          fg='lightgray', activebackground='lightgray',
                          activeforeground='#252221')
        close = Button(self.right_frame, command=self.reg.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        self.right_frame.grid()
        message.grid(row=1, sticky=W, pady = 5)
        name.grid(row=1, column=1, pady=10, padx=20)
        email.grid(row=2, column=1, pady=10, padx=20)
        country.grid(row=3, column=1, pady=10, padx=20)
        pwd.grid(row=5, column=1, pady=10, padx=20)
        pwd_again.grid(row=6, column=1, pady=10, padx=20)
        close.grid(row=7, column=1, pady=10, padx=10)
        register.grid(row=7, column=0, pady=10, padx=10)

        self.midwin(self.reg, 500, 380)

        self.reg.mainloop()

    def update_clock(self, c):
        flag = True
        if c >= 0:
            try:
                self.timer.config(text=c)
            except:
                flag = False
        else:
            if self.root3 is not None:
                self.root3.destroy()
                self.root3 = None
            flag = False
        if flag:
            self.root.after(1000, lambda: self.update_clock(c - 1))

    def register_send(self, name, email, country, pwd, pwd_again, message):
        mail_re = re.compile('^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$')
        pass_re = re.compile("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")
        if mail_re.match(email.get()) is None:
            message.config(text="Invalid Email", bg='#CCCCCC')
        elif len(name.get()) == 0:
            message.config(text="Name should be something...", bg='#CCCCCC')
        elif pass_re.match(pwd.get()) is None:
            message.config(text="Invalid Password (8 characters with numbers)", bg='#CCCCCC')
        elif pwd.get() != pwd_again.get():
            message.config(text="Passwords don't match", bg='#CCCCCC')
        else:
            with open('countries.txt') as txt:
                countries = txt.read().split('\n')
            if country.get() not in countries:
                message.config(text="Country doesn't exist", bg='#CCCCCC')
            else:
                self.client.send('CRED'.encode())
                self.client.send(
                    pickle.dumps([name.get(), email.get(), country.get(), pwd.get()]))
                self.__attempt = pwd
                self.reg.destroy()

    def login(self):
        log = Tk()
        log.config(bg='#252221')
        log.bind('<Return>', lambda event: [self.loginsend(email.get(), pwd.get(), log, message)])
        f = ('Helvetica', 14)
        right_frame = Frame(log, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame, width=10, text='Login', bg='#252221', fg='#CCCCCC', font=f).grid(row=0, columnspan=2, sticky='nswe')
        Label(right_frame, text="Email", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame, text="Password", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)

        email = Entry(right_frame, font=f)
        pwd = Entry(right_frame, font=f, show='*')
        message = Label(log, bg='#252221', font=f)
        login = Button(right_frame,
                       command=lambda: [self.loginsend(email.get(), pwd.get(), log, message)],
                       width=15, text='Login', font=('Helvetica', 11), cursor='hand2', bg='#252221', fg='lightgray',
                       activebackground='lightgray',
                       activeforeground='#252221')
        close = Button(right_frame, command=log.destroy, text='Close', width=15, font=('Helvetica', 11), cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        right_frame.grid(row=0)
        message.grid(row=1, column=0,sticky=W, pady=10)
        email.grid(row=1, column=1, pady=10, padx=20)
        pwd.grid(row=5, column=1, pady=10, padx=20)
        close.grid(row=7, column=1, pady=10, padx=10)
        login.grid(row=7, column=0, pady=10, padx=10)
        self.midwin(log, 500, 240)
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
        Label(right_frame, text="Conditions", bg='#CCCCCC', font=f).grid(row=3, column=0, sticky=W, pady=10)
        Label(right_frame, text="Price (per night)", bg='#CCCCCC', font=f).grid(row=4, column=0, sticky=W, pady=10)
        Label(right_frame, text="Check-in", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)
        Label(right_frame, text="Check-out", bg='#CCCCCC', font=f).grid(row=6, column=0, sticky=W, pady=10)

        Button(right_frame, text="Choose image", command=self.addfile, font=f, bg='#252221', fg='lightgray',
               cursor='hand2',
               activebackground='lightgray', activeforeground='#252221').grid(row=6, column=0, sticky=W, pady=10)

        self.roomname = Entry(right_frame, font=f)
        self.location = Entry(right_frame, font=f)
        self.conditions = Entry(right_frame, font=f)
        self.price = Entry(right_frame, font=f)
        self.duration1 = DateEntry(right_frame, font=f, locale='en_IL', date_pattern='dd/mm/yyyy',
                                   mindate=self.servertime, showweeknumbers=0)
        self.duration2 = DateEntry(right_frame, font=f, locale='en_IL', date_pattern='dd/mm/yyyy',
                                   mindate=self.servertime, showweeknumbers=0)
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
        self.conditions.grid(row=3, column=1, pady=10, padx=20)
        self.price.grid(row=4, column=1, pady=10, padx=20)
        self.duration1.grid(row=5, column=1, pady=10)
        self.duration2.grid(row=6, column=1, pady=10)
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
        """ Sends data of room adding after done inspecting it """
        err = False
        try:
            self.filename
        except:
            self.filename = ''
        if self.filename == '':
            self.message.config(text='No image selected', bg='#CCCCCC')
        elif self.duration1.get_date() >= self.duration2.get_date():
            self.message.config(text='Invalid date range', bg='#CCCCCC')
        elif self.__user[0] != 'Guest':
            self.duration = (
            self.duration1.get_date().strftime('%d/%m/%Y'), self.duration2.get_date().strftime('%d/%m/%Y'))
            shutil.copy(self.filename, f'Images/{self.filename[self.filename.rfind("/") + 1:]}')
            temp = TkinterMapView()
            temp.set_address(self.location.get())
            c = temp.get_position()
            if c != (52.516268, 13.377694999999989):  # non-generic only
                if self.roomname.get() != '' and self.price.get().isdigit():
                    self.client.send(
                        f'ADD {self.roomname.get()}. {c[0]} {c[1]}.'
                        f' {int(self.price.get())}.'
                        f' {self.duration[0]}. {self.duration[1]}'
                        f'. {self.__user[0]}. {self.filename[self.filename.rfind("/") + 1:]}.'
                        f' {self.conditions.get()}'.encode())
                    self.sendimage()
                    self.filename = ''

                else:
                    self.message.config(text='values must be valid', bg='#CCCCCC')
                    err = True
                if not err:
                    self.roomroot.destroy()
            else:
                self.message.config(text='Invalid place', bg='#CCCCCC')

        else:
            self.message.config(text='Guests cannot add rooms', bg='#CCCCCC')

    def purchase_screen(self, total):
        root7 = Toplevel()
        root7.config(bg='#252221')
        f = ('Helvetica', 14)
        right_frame3 = Frame(root7, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame3, text="Total", bg='#CCCCCC', font=f).grid(row=0, column=0, sticky=W, pady=10)
        # Label(right_frame3, text="Credit Card", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        total = Label(right_frame3, text=f'{total}₪', font=f, bg='#CCCCCC')
        # name = Entry(right_frame3, font=f)
        submit = Button(right_frame3,
                        command=lambda: self.commit_purchase(root7),
                        width=15, text='Submit', font=('Helvetica', 11), cursor='hand2', bg='#252221',
                        fg='lightgray', activebackground='lightgray',
                        activeforeground='#252221')
        close = Button(right_frame3, command=root7.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        total.grid(row=0, column=1, pady=10, padx=20)
        # name.grid(row=1, column=1, pady=10, padx=20)
        close.grid(row=1, column=1, pady=10, padx=10)
        submit.grid(row=1, column=0, pady=10, padx=10)
        right_frame3.pack()
        self.midwin(root7, 500, 200)

    def commit_purchase(self, root7):
        row = list(self.row)
        self.recorders.append(row)
        row[4], row[5] = self.duration1.get_date().strftime(
            '%d/%m/%Y'), self.duration2.get_date().strftime('%d/%m/%Y')
        row.append(self.__user[0])
        self.client.send('BUY'.encode())
        self.client.send(pickle.dumps(row))
        self.root3.destroy()
        root7.destroy()
        self.reset_root3()
        self.removeinst(self.row)
        self.row = None
        tkinter.messagebox.showinfo(message='Room bought')

    def loginsend(self, email, pwd, log, message):
        mail_re = re.compile('^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$')
        pass_re = re.compile("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")
        if mail_re.match(email) is not None and pass_re.match(pwd) is not None:
            self.client.send('CRED'.encode())
            self.client.send(pickle.dumps([email, pwd]))
            self.__attempt = pwd
            log.destroy()
        else:
            message.config(text='Invalid mail or password', bg='#CCCCCC')

    def logout(self):
        self.__user = ['Guest', None]
        self.recorders = []
        self.root.destroy()
        self.main()

    # Do you wish to exit the program entirely?
    def pop(self):
        popup = Tk()
        popup.resizable(False, False)
        popup.config(bg='lightgray')
        lb3 = Label(popup, text='Do you wish to exit?', font=("Helvetica", 15), bg='#252221', fg='lightgray')
        lb3.pack(fill=BOTH)
        # Destroy both popup and root windows
        yes = Button(popup, text='Yes', command=sys.exit, bg='#252221',
                     fg='lightgray', activebackground='lightgray', activeforeground='#252221', padx=10, cursor='hand2')
        yes.pack(pady=10, side=RIGHT)

        no = Button(popup, text='No', command=popup.destroy, bg='#252221', fg='lightgray', activebackground='lightgray',
                    activeforeground='#252221', padx=10, cursor='hand2')  # Destroy popup window
        no.pack(pady=10, side=RIGHT)
        self.midwin(popup, 300, 80)  # place window in the center

    def check_radius(self, point, attraction):
        coords = attraction[1].split(' ')
        point_coords = point[2].split(' ')
        point_coords[0], point_coords[1] = float(point_coords[0]), float(point_coords[1])
        coords[0], coords[1] = float(coords[0]), float(coords[1])
        limitxmax = coords[0] + float(attraction[3])
        limitxmin = coords[0] - float(attraction[3])
        limitymax = coords[1] + float(attraction[3])
        limitymin = coords[1] - float(attraction[3])
        if limitxmin <= point_coords[0] <= limitxmax and limitymin <= point_coords[1] <= limitymax:
            return 1
        return 0

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
