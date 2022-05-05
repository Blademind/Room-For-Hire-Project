import datetime
import math
import pickle
import re
import shutil
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
Admin by Alon Levy
This aims to allow user interaction of which
he can personalize and buy rooms.
"""

file = __file__


class Admin:
    def __init__(self):
        self.servertime = datetime.datetime.today().date()
        self.client = socket(AF_INET, SOCK_STREAM)
        self.BUF = 2048
        self.ADDR = ('192.168.1.197', 50000)  # where to connect
        self.client.connect(self.ADDR)
        self.client = ssl.wrap_socket(self.client, server_side=False, keyfile='privkey.pem', certfile='certificate.pem')
        self.images = pickle.loads(self.client.recv(self.BUF))
        self.attraction_images = pickle.loads(self.client.recv(self.BUF))
        self.world_active = False

        self.getimage()
        self.recorders = []
        self.server = self.client.getpeername()
        _thread.start_new_thread(self.listen, ())
        self.__user = ['Guest', None]
        self.__creds = None
        print('___SUCCESS___')
        self.login()

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
                print(datacontent)
                if datacontent == 'FILES':
                    self.images = pickle.loads(self.client.recv(self.BUF))
                    self.attraction_images = pickle.loads((self.client.recv(self.BUF)))
                    self.getimage()
                    if self.world_active:
                        self.clear(self.root2)
                        self.worldrooms('Normal', False)
                elif 'Error:' in datacontent or 'Exists:' in datacontent or 'Success:' in datacontent:  # Errors, Successes
                    if 'Success:' in datacontent:
                        tkinter.messagebox.showinfo(message=datacontent)
                    else:
                        tkinter.messagebox.showerror(message=datacontent)
                elif 'Success' in datacontent:
                    self.__user[0] = data.decode()[8:]
                    self.__user[1] = self.__attempt
                    self.clear(self.root)
                    self.main()
                    self.log1.config(text='Logout', command=self.logout)
                    self.recent = Button(self.root,
                                         command=self.orders, text='Recent orders', font=('Helvetica', 11),
                                         cursor='hand2',
                                         bg='#252221', fg='lightgray', activebackground='lightgray',
                                         activeforeground='#252221')
                    self.recent.grid(column=2, row=0, sticky=W)

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
                elif datacontent == 'UPDATE':
                    self.all_orders = pickle.loads(self.client.recv(self.BUF))
                elif datacontent == 'PUSH':
                    self.get_database('registered')
            except Exception as e:
                try:
                    if type(pickle.loads(data)[0]) is bool:
                        if pickle.loads(data)[0] == True:  # if passed (not simplified so it wouldn't catch a list)
                            self.purchase_screen(pickle.loads(data)[1])  # (total)
                        elif not pickle.loads(data)[0]:
                            tkinter.messagebox.showinfo(message='The selected date is taken')
                            self.removeinst(self.row)
                    elif pickle.loads(data)[1][4] == 1:
                        self.recorders = pickle.loads(data)[0]
                        self.all_orders = pickle.loads(data)[2]
                        self.change = Button(self.root,
                                             command=self.change_date_tk, text='Change Date', font=('Helvetica', 11),
                                             cursor='hand2',
                                             bg='#252221', fg='lightgray', activebackground='lightgray',
                                             activeforeground='#252221')
                        self.change.grid(column=2, row=0)
                        Button(self.root,
                                             command=self.purchases, text='All Purchases', font=('Helvetica', 11),
                                             cursor='hand2',height=2,
                                             bg='#252221', fg='lightgray', activebackground='lightgray',
                                             activeforeground='#252221').grid(row=1, column=5, sticky='e')
                        Button(self.root,
                                             command=self.users_data, text='All Users', font=('Helvetica', 11),
                                             cursor='hand2',height=2,
                                             bg='#252221', fg='lightgray', activebackground='lightgray',
                                             activeforeground='#252221').grid(row=2, column=5, sticky='ne')
                        Button(self.root,
                                             command=self.offers_data, text='All Offers', font=('Helvetica', 11),
                                             cursor='hand2',height=2,
                                             bg='#252221', fg='lightgray', activebackground='lightgray',
                                             activeforeground='#252221').grid(row=2, column=5, sticky='e')

                    else:
                        self.root.withdraw()
                        tkinter.messagebox.showerror(message='Not an admin')
                        self.root.destroy()
                except: pass

    def purchases(self):
        if self.all_orders:
            all_orders_tk = Tk()
            f = ('Helvetica', 12)
            Label(all_orders_tk, text='Room Name', font=f, bg='#252221', fg='lightgray').grid(sticky=NSEW)
            orders1 = Listbox(all_orders_tk, font=f, bg='#CCCCCC')
            for row in self.all_orders:
                orders1.insert(END, row[0])
            orders1.grid()
            close = Button(all_orders_tk,
                           command=all_orders_tk.destroy, text='Close', width=15, font=('Helvetica', 11),
                           cursor='hand2',
                           bg='#252221', fg='lightgray', activebackground='lightgray',
                           activeforeground='#252221')
            close.grid()
            scrollbar = ttk.Scrollbar(all_orders_tk, orient=VERTICAL, command=orders1.yview)
            orders1.configure(yscrollcommand=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky='ns')
            orders1.bind('<Double-1>', lambda event: self.details(self.all_orders[orders1.curselection()[0]], all_orders_tk))
        else:
            tkinter.messagebox.showinfo(message='No orders have been placed')

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
            scrollbar.grid(row=0, column=1, sticky='ns')
            orders1.bind('<Double-1>', lambda event: self.details(self.recorders[orders1.curselection()[0]], self.root5))
        else:
            tkinter.messagebox.showinfo(message='You have not placed any order')

    def details(self, line, root):
        print(line)
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
        try:
            buyer = Label(right_frame, text=f'{line[-1]}', font=f, bg='#CCCCCC')  # last line added by server (buyer)
            Label(right_frame, text="Buyer", bg='#CCCCCC', font=f).grid(row=6, column=0, sticky=W, pady=10)
            buyer.grid(row=6, column=1, pady=10, padx=20)
        except: pass

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
        close.grid(row=7, column=1, pady=10, padx=20)
        t = datetime.datetime.strptime(line[4], '%d/%m/%Y')
        if t.date() > self.servertime:
            cancel = Button(right_frame,
                            command=lambda: [self.cancel(line), self.root4.destroy(), root.destroy(),
                                             tkinter.messagebox.showinfo(message='Cancelled')],
                            text='Cancel', width=15, font=('Helvetica', 11), cursor='hand2',
                            bg='#252221', fg='lightgray', activebackground='lightgray',
                            activeforeground='#252221')
            cancel.grid(row=7, column=0, pady=10, padx=20)

        right_frame.grid()
        self.root4.mainloop()

    def cancel(self, line):
        if line is self.recorders:
            self.recorders.remove(line)
        line = list(line)
        line.append(self.__user[0])
        self.client.send('UPDATE'.encode())
        self.client.send(pickle.dumps(line))

    def main(self):
        self.root.bind('<Return>', lambda event: None)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
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
        self.root.geometry('900x500')

    def searchplace(self, *args):
        self.map.set_address(self.message.get())
        self.message.delete(0, END)

    def clear(self, root):
        for widget in root.winfo_children():
            widget.destroy()

    def worldrooms(self, mode, flag):
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
        self.map.add_right_click_menu_command(label="Add an Attraction",
                                                command=self.add_marker_event_tk,
                                                pass_coords=True)
        self.map.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",max_zoom=22)\
            if mode == 'Normal' else self.map.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",max_zoom=22)
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
            mindate = row[4].split('/')
            maxdate = row[5].split('/')
            mindate = datetime.datetime(int(mindate[2]), int(mindate[1]), int(mindate[0]))
            maxdate = datetime.datetime(int(maxdate[2]), int(maxdate[1]), int(maxdate[0]))
            img = ImageTk.PhotoImage(Image.open(f'Images/{row[6]}').resize((150, 150)))
            self.map.set_marker(float(self.cord[0]), float(self.cord[1]), image=img,
                                image_zoom_visibility=(5, 22),
                                marker_color_circle="black",
                                marker_color_outside="gray40", text=row[0],
                                command=lambda here=row: self.askroomtk(here, mindate, maxdate))
        for row in self.all_attractions:
            self.cord = row[1].split(' ')
            img = ImageTk.PhotoImage(Image.open(f'Attractions_images/{row[2]}').resize((150, 150)))
            marker = self.map.set_marker(float(self.cord[0]), float(self.cord[1]), image=img,
                                image_zoom_visibility=(5, 22),
                                marker_color_circle="white",
                                marker_color_outside="gray40", command=lambda here=row: self.marker_interaction(here))
            marker.hide_image(True)
        options = OptionMenu(self.root2, self.val, *["Price(ASC.)", "Price(DESC.)", "Proximity(ASC.)", *[attraction[0] for attraction in self.dict_closeby.keys()]], command=self.display_selected)
        options.grid(row=0, column=1, sticky='new', columnspan=2)
        self.orders2 = Listbox(self.root2, font=('Helvetica', 12), bg='#CCCCCC')
        self.orders2.grid(row=0, column=1, columnspan=2,sticky='nsew', pady=30)
        self.orders2.bind('<Double-1>', lambda event: [[self.map.set_address(sub[2]), self.map.set_zoom(10)] for sub in self.all if self.orders2.get(self.orders2.curselection()[0]) == sub[0]])
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

    def add_marker_event_tk(self, coords):
        marker_tk = Toplevel()
        marker_tk.config(bg='#252221')
        f = ('Helvetica', 14)
        right_frame = Frame(marker_tk, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame, text="Name", bg='#CCCCCC', font=f).grid(row=0, column=0, sticky=W, pady=10)
        Label(right_frame, text="Location", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame, text="Radius", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)

        Button(right_frame, text="Choose image", command=lambda: self.addfile(marker_tk), font=f, bg='#252221', fg='lightgray',
               cursor='hand2',
               activebackground='lightgray', activeforeground='#252221').grid(row=3, column=0, sticky=W, pady=10)
        location = Label(right_frame, text=f"{coords}\n{tkintermapview.convert_coordinates_to_city(float(coords[0]), float(coords[1]))}", bg='#CCCCCC', font=f)
        name = Entry(right_frame, font=f)
        radius = Entry(right_frame, font=f)
        self.message = Label(marker_tk, bg='#252221', font=f)
        submit = Button(right_frame,
                        command=lambda: self.add_marker_event(coords, marker_tk, name.get(), radius.get()),
                        width=15, text='Add', font=('Helvetica', 11), cursor='hand2', bg='#252221',
                        fg='lightgray', activebackground='lightgray',
                        activeforeground='#252221')
        close = Button(right_frame, command=marker_tk.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        name.grid(row=0, column=1, sticky=W, pady=10)
        location.grid(row=1, column=1, sticky=W, pady=10)
        radius.grid(row=2, column=1, sticky=W, pady=10)
        close.grid(row=4, column=1, pady=10, padx=10)
        submit.grid(row=4, column=0, pady=10, padx=10)
        right_frame.grid()

        self.message.grid(row=3, column=0, sticky=W, pady=10)

    def marker_interaction(self, marker):
        if marker.image_hidden is True:
            marker.hide_image(False)
        else:
            marker.hide_image(True)

    def add_marker_event(self, coords, marker_tk, name, radius):
        try:
            self.filename
        except:
            self.filename = ''
        if self.filename == '':
            self.message.config(text='No image selected', bg='#CCCCCC')
        else:
            shutil.copy(self.filename, f'Attractions_images/{self.filename[self.filename.rfind("/") + 1:]}')
            self.client.send(f'ATTRACTION {coords[0]} {coords[1]}. {self.filename[self.filename.rfind("/") + 1:]}. {name}. {radius}'.encode())
            self.sendimage()
            self.filename = ""
            marker_tk.destroy()

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
        try:
            self.root3
        except:
            self.root3 = None
        if self.root3 is None:
            for i in self.all:
                if i[2].split(' ')[0] == str(row.position[0]) and i[2].split(' ')[1] == str(row.position[1]):
                    self.row = i
                    break
            self.root3 = Toplevel()
            self.root3.protocol("WM_DELETE_WINDOW", lambda: [self.removeinst(self.row),
                                            self.root3.destroy(), self.reset_root3()])

            self.root3.config(bg='#252221')
            self.client.send('OCC'.encode())
            self.client.send(pickle.dumps(self.row))
            f = ('Helvetica', 14)
            right_frame = Frame(self.root3, bd=2, bg='#CCCCCC', padx=10, pady=10)
            img = ImageTk.PhotoImage(Image.open(f'Images/{self.row[6]}').resize((200, 200)))
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

    def reset_root3(self):
        self.root3 = None

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

    def askroom(self):
        if self.__user[0] == 'Guest':
            self.guestmail()
        elif self.duration1.get_date() < self.duration2.get_date():
            self.client.send('CHECK'.encode())
            self.client.send(pickle.dumps((self.row, self.duration1.get_date(), self.duration2.get_date())))

    def guestmail(self):
        self.marker_tk = Tk()
        self.marker_tk.config(bg='#252221')
        f = ('Helvetica', 14)
        self.right_frame2 = Frame(self.marker_tk, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(self.right_frame2, text="Email", bg='#CCCCCC', font=f).grid(row=0, column=0, sticky=W, pady=10)
        self.name = Entry(self.right_frame2, font=f)
        submit = Button(self.right_frame2,
                        command=lambda: self.submitguestname(self.name.get()),
                        width=15, text='Submit', font=('Helvetica', 11), cursor='hand2', bg='#252221',
                        fg='lightgray', activebackground='lightgray',
                        activeforeground='#252221')
        close = Button(self.right_frame2, command=self.marker_tk.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        self.name.grid(row=0, column=1, pady=10, padx=20)
        close.grid(row=1, column=1, pady=10, padx=10)
        submit.grid(row=1, column=0, pady=10, padx=10)
        self.right_frame2.pack()
        self.midwin(self.marker_tk, 500, 250)

    def submitguestname(self, mail):
        self.__user[0] = mail
        self.marker_tk.destroy()
        self.askroom()

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

    def change_date_tk(self):
        date_root = Tk()
        date_root.config(bg='lightgray')
        lb3 = Label(date_root, text='When would you like to change the date to?', font=("Helvetica", 15), bg='#252221',
                    fg='lightgray')
        lb3.pack(fill=BOTH)
        dates = DateEntry(date_root, font=('Helvetica', 14), locale='en_IL', date_pattern='dd/mm/yyyy',
                          mindate=datetime.datetime.today() + datetime.timedelta(days=1), showweeknumbers=0)
        dates.pack(pady=10)
        submit = Button(date_root, text='Submit',
                        command=lambda: [self.change_date(dates.get_date()), date_root.destroy()], bg='#252221',
                        fg='lightgray', activebackground='lightgray', activeforeground='#252221', padx=10,
                        cursor='hand2')
        submit.pack(pady=10, side=RIGHT)

        close = Button(date_root, text='Close', command=date_root.destroy, bg='#252221', fg='lightgray',
                       activebackground='lightgray',
                       activeforeground='#252221', padx=10, cursor='hand2')  # Destroy popup window
        close.pack(pady=10, side=RIGHT)

        self.midwin(date_root, 400, 175)  # place window in the center

    def change_date(self, date):
        self.client.send('DATE'.encode())
        self.client.send(pickle.dumps(date))

    def login(self):
        self.root = Tk()
        self.root.config(bg='#252221')
        self.root.bind('<Return>', lambda event: [self.loginsend(email.get(), pwd.get(), message)])
        f = ('Helvetica', 14)
        right_frame = Frame(self.root, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame,width=10, text='Admin Login', bg='#252221', fg='#CCCCCC', font=f).grid(row=0, columnspan=2, sticky='nswe')
        Label(right_frame, text="Email", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame, text="Password", bg='#CCCCCC', font=f).grid(row=5, column=0, sticky=W, pady=10)
        email = Entry(right_frame, font=f)
        pwd = Entry(right_frame, font=f, show='*')
        message = Label(self.root, bg='#252221', font=f)
        login = Button(right_frame,
                       command=lambda: [self.loginsend(email.get(), pwd.get(), message)],
                       width=15, text='Login', font=('Helvetica', 11), cursor='hand2', bg='#252221', fg='lightgray',
                       activebackground='lightgray',
                       activeforeground='#252221')
        close = Button(right_frame, command=self.root.destroy, text='Close', width=15, font=('Helvetica', 11), cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        right_frame.grid(row=0)
        message.grid(row=1, column=0, sticky=W, pady=10)
        email.grid(row=1, column=1, pady=10, padx=20)
        pwd.grid(row=5, column=1, pady=10, padx=20)
        close.grid(row=7, column=1, pady=10, padx=10)
        login.grid(row=7, column=0, pady=10, padx=10)
        self.midwin(self.root, 450, 250)
        self.root.mainloop()

    def addroom(self):
        """ Allows user to add a room """
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

        Button(right_frame, text="Choose image", command=lambda: self.addfile(self.roomroot), font=f, bg='#252221', fg='lightgray',
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

    def addfile(self, root):
        root.attributes('-topmost', False)
        self.filename = filedialog.askopenfilename(filetypes=[('image files', '.png'), ('image files', '.jpg')], )
        self.message.config(text=f'image: {self.filename}', bg='#CCCCCC')
        root.attributes('-topmost', True)

    def addsend(self):
        """ sends added room data to server """
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

    def purchase_screen(self, total):
        root7 = Toplevel()
        root7.config(bg='#252221')
        f = ('Helvetica', 14)
        right_frame3 = Frame(root7, bd=2, bg='#CCCCCC', padx=10, pady=10)
        Label(right_frame3, text="Total", bg='#CCCCCC', font=f).grid(row=0, column=0, sticky=W, pady=10)
        # Label(right_frame3, text="Credit Card", bg='#CCCCCC', font=f).grid(row=1, column=0, sticky=W, pady=10)
        total_label = Label(right_frame3, text=f'{total}₪', font=f, bg='#CCCCCC')
        # name = Entry(right_frame3, font=f)
        submit = Button(right_frame3,
                        command=lambda: self.commit_purchase(root7, total),
                        width=15, text='Submit', font=('Helvetica', 11), cursor='hand2', bg='#252221',
                        fg='lightgray', activebackground='lightgray',
                        activeforeground='#252221')
        close = Button(right_frame3, command=root7.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        total_label.grid(row=0, column=1, pady=10, padx=20)
        # name.grid(row=1, column=1, pady=10, padx=20)
        close.grid(row=1, column=1, pady=10, padx=10)
        submit.grid(row=1, column=0, pady=10, padx=10)
        right_frame3.pack()

    def commit_purchase(self, root7, total):
        """Sends purchase query"""
        row = list(self.row)
        row.append(total)
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

    def loginsend(self, email, pwd, message):
        """Sends to server the user's credentials, logs in attempt"""
        mail_re = re.compile('^[\w\.]+@([\w-]+\.)+[\w-]{2,4}$')
        pass_re = re.compile("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")
        if mail_re.match(email) is not None and pass_re.match(pwd) is not None:
            self.client.send('CRED'.encode())
            self.client.send(pickle.dumps([email, pwd]))
            self.__attempt = pwd
        else:
            message.config(text='Invalid mail or password', bg='#CCCCCC')

    def logout(self):
        """Logs user out"""
        self.__user = ['Guest', None]
        self.recorders = []
        self.root.destroy()
        self.login()

    # Do you wish to exit the program entirely?
    def pop(self, root):
        popup = Tk()
        popup.resizable(None, None)
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
        """Places window in the middle"""
        a = int(root.winfo_screenwidth() / 2 - (x / 2))
        b = int(root.winfo_screenheight() / 2 - (y / 2))
        root.geometry('{}x{}+{}+{}'.format(x, y, a, b))

    def sendimage(self):
        """Send an image selected by the user in adding a room"""
        with open(self.filename, 'rb') as txt:
            length = os.path.getsize(self.filename)
            send = pickle.dumps(length)
            self.client.send(send)
            s = 0
            while s != length:
                data = txt.read(self.BUF)
                s += len(data)
                self.client.send(data)

    def users_data(self):
        root = Tk()
        root.bind('<Return>', lambda event: self.search_record(tree, message.get(), 'registered'))
        root.title('users')
        conn = sqlite3.connect('Databases/registered.db')
        all_data = conn.execute('SELECT * FROM Registered').fetchall()
        conn.close()
        # define columns
        columns = ('Fullname', 'Email', 'Country', 'Password', 'Admin')

        tree = ttk.Treeview(root, columns=columns, show='headings')
        tree.grid(row=1, column=0, sticky='nsew')

        # define headings
        tree.heading('Fullname', text='Full Name')
        tree.column('Fullname', width=20)
        tree.heading('Email', text='Email')
        tree.column('Email', width=20)
        tree.heading('Country', text='Country')
        tree.column('Country', width=20)
        tree.heading('Password', text='Password')
        tree.column('Password', width=20)
        tree.heading('Admin', text='Is Admin')
        tree.column('Admin', width=20)

        tree.bind('<<TreeviewSelect>>', lambda event: self.make_admin(tree, root))
        message = Entry(root, bg='lightgray', fg='#252221',
                        font=("Helvetica", 15, 'bold'), width=60)
        message.grid(row=0, column=0, sticky=EW)
        search = Button(root,
                       command=lambda: self.search_record(tree, message.get(), 'registered'), text='Search', font=('Helvetica', 11),
                       cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        search.grid(column=1, row=0, pady=10)
        close = Button(root,
                       command=root.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        close.grid(column=0, row=2, pady=10)
        for data in all_data:
            tree.insert('', END, values=data)
        scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='nsw')
        self.midwin(root, 750, 325)

    def search_record(self, tree, record, database):
        conn = sqlite3.connect(f'Databases/{database}.db')
        if database == 'registered':
            all_data = conn.execute('SELECT * FROM Registered WHERE Email="{0}" OR Fullname="{0}" OR Country="{0}" OR Password="{0}" OR Admin="{0}"'.format(record)).fetchall()
            conn.commit()
            conn.close()
            tree.delete(*tree.get_children())
            for data in all_data:
                tree.insert('', END, values=data)
        else:
            all_data = conn.execute('SELECT * FROM Offered WHERE RoomName="{0}" OR By="{0}" OR Coordinates="{0}"'
                                    ' OR Price="{0}" OR First="{0}" OR Last="{0}" OR ImagePath="{0}" OR RATING="{0}"'
                                    ' OR Conditions="{0}"'.format(record)).fetchall()
            conn.commit()
            conn.close()
            tree.delete(*tree.get_children())
            for data in all_data:
                tree.insert('', END, values=data)

    def make_admin(self, tree, root):
        selected = tree.item(tree.selection())["values"]
        print(selected)
        if selected and selected[4] != 1:
            admin_tk = Tk()
            admin_tk.resizable(None, None)
            admin_tk.config(bg='lightgray')
            lb3 = Label(admin_tk, text=f'Do you wish to make {selected[0]} an Admin?', font=("Helvetica", 15), bg='#252221', fg='lightgray')
            lb3.pack(fill=BOTH)
            # Destroy both popup and root windows
            yes = Button(admin_tk, text='Yes', command=lambda: [self.client.send(f"MAKE {selected[1]}".encode()),
                                                                admin_tk.destroy(), root.destroy()], bg='#252221',
                         fg='lightgray', activebackground='lightgray', activeforeground='#252221', padx=10, cursor='hand2')
            yes.pack(pady=10, side=RIGHT)

            no = Button(admin_tk, text='No', command=admin_tk.destroy, bg='#252221', fg='lightgray', activebackground='lightgray',
                        activeforeground='#252221', padx=10, cursor='hand2')  # Destroy popup window
            no.pack(pady=10, side=RIGHT)
            self.midwin(admin_tk, 350, 80)  # place window in the center

    def offers_data(self):
        root = Tk()
        root.bind('<Return>', lambda event: self.search_record(tree, message.get(), 'database'))
        root.title('users')
        conn = sqlite3.connect('Databases/database.db')
        all_data = conn.execute('SELECT * FROM Offered').fetchall()
        conn.close()
        # define columns
        columns = ('RoomName', 'By', 'Coordinates', 'Price', 'First', 'Last', 'ImagePath', 'RATING', 'Conditions')

        tree = ttk.Treeview(root, columns=columns, show='headings',)
        tree.grid(row=1, column=0, sticky='nsew')

        # define headings
        tree.heading('RoomName', text='Room Name')
        tree.column('RoomName', width=20)
        tree.heading('By', text='Publisher')
        tree.column('By', width=20)
        tree.heading('Coordinates', text='Location')
        tree.column('Coordinates', width=20)
        tree.heading('Price', text='Price')
        tree.column('Price', width=20)
        tree.heading('First', text='From')
        tree.column('First', width=20)
        tree.heading('Last', text='Until')
        tree.column('Last', width=20)
        tree.heading('ImagePath', text='Image Path')
        tree.column('ImagePath', width=20)
        tree.heading('RATING', text='Rating')
        tree.column('RATING', width=20)
        tree.heading('Conditions', text='Conditions')
        tree.column('Conditions', width=20)


        message = Entry(root, bg='lightgray', fg='#252221',
                        font=("Helvetica", 15, 'bold'), width=60)
        message.grid(row=0, column=0, sticky=EW)
        search = Button(root,
                       command=lambda: self.search_record(tree, message.get(),'database'), text='Search', font=('Helvetica', 11),
                       cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        search.grid(column=1, row=0, pady=10)
        close = Button(root,
                       command=root.destroy, text='Close', width=15, font=('Helvetica', 11),
                       cursor='hand2',
                       bg='#252221', fg='lightgray', activebackground='lightgray',
                       activeforeground='#252221')
        close.grid(column=0, row=2, pady=10)
        for data in all_data:
            tree.insert('', END, values=data)
        scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky='nsw')
        self.midwin(root, 750, 325)


if __name__ == '__main__':

    print('___INITIALIZING___')
    try:
        a = Admin()
    except ConnectionRefusedError:
        print('COULD NOT CONNECT')
