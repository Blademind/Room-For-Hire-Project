import pickle
import time
import tkinter.messagebox
from socket import *
from tkinter import *
# import threading
import _thread
import sqlite3
from tkintermapview import TkinterMapView
"""
Client by Alon Levy
"""

user = 'Guest'


class Client:
    def __init__(self, user):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.__BUF = 1024
        self.__ADDR = ('127.0.0.1', 50000)  # where to connect
        self.client.connect(self.__ADDR)
        _thread.start_new_thread(self.listen,())
        print('___SUCCESS___')
        self.main(user)

    def listen(self):
        while 1:
            data = self.client.recv(self.__BUF)
            if not data:
                break
            tkinter.messagebox.showinfo('Message from Server', data.decode())
            if 'Success' in data.decode():
                user = data.decode()[8:]
                print(user)
                user1.config(text=f'Welcome, {user}')

    def main(self, user):
        global user1
        root = Tk()
        reg1 = Button(root, command=self.register, text='Register', font=('Helvetica', 11), cursor='hand2',bg='#252221', fg='lightgray', activebackground='lightgray',
                   activeforeground='#252221')
        reg1.pack(side=LEFT, anchor=N)
        log1 = Button(root, command=self.login, text='Login', font=('Helvetica', 11), cursor='hand2',
                      bg='#252221', fg='lightgray', activebackground='lightgray',
                      activeforeground='#252221')
        log1.pack(side=LEFT, anchor=N)
        user1 = Label(root, text=f'Welcome {user}', font=('Helvetica', 11), cursor='hand2',
                      bg='#252221', fg='lightgray', activebackground='lightgray',
                      activeforeground='#252221')
        user1.pack(side=RIGHT, anchor=N)
        findroom = Button(root, command=self.worldrooms, width=25,height=2,
                      text='Find a Room', font=('Helvetica', 14),
                      cursor='hand2',bg='#252221', fg='lightgray', activebackground='lightgray',
                      activeforeground='#252221')
        findroom.pack(anchor=W, pady=50, padx=20)
        addroom = Button(root, command=lambda: self.pop(reg), width=25,height=2,
                      text='Add a Room', font=('Helvetica', 14),
                      cursor='hand2',bg='#252221', fg='lightgray', activebackground='lightgray',
                      activeforeground='#252221')
        addroom.pack(anchor=W,pady=10, padx=20)
        close = Button(root, command=lambda: self.pop(root), text='Close', font=('Helvetica', 11), cursor='hand2',bg='#252221', fg='lightgray', activebackground='lightgray',
                   activeforeground='#252221')
        close.pack(anchor=E)
        # menus
        menu = Menu(root)
        filemenu = Menu(menu, tearoff=0)
        filemenu.add_command(label='Help')
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=lambda: self.pop(root))
        menu.add_cascade(label="More", menu=filemenu)
        root.config(menu=menu, bg='lightgray')
        self.midwin(root, 550, 300)
        root.mainloop()

    def worldrooms(self):
        root2 = Tk()
        map_widget = TkinterMapView(root2, width=1000, height=700, corner_radius=0)
        map_widget.pack(fill="both", expand=True)

    def register(self):
        reg = Tk()
        reg.config(bg='#252221')
        f = ('Helvetica', 14)
        var = StringVar()
        right_frame = Frame(reg,bd=2,bg='#CCCCCC',padx=10,pady=10)
        Label(right_frame,text="Name", bg='#CCCCCC',font=f).grid(row=0, column=0, sticky=W, pady=10)
        Label(right_frame,text="Email", bg='#CCCCCC',font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame,text="Gender", bg='#CCCCCC',font=f).grid(row=3, column=0, sticky=W, pady=10)
        Label(right_frame, text="Country", bg='#CCCCCC', font=f).grid(row=2, column=0, sticky=W, pady=10)
        Label(right_frame,text="Password", bg='#CCCCCC',font=f).grid(row=5, column=0, sticky=W, pady=10)
        Label(right_frame,text="Re-Enter Password", bg='#CCCCCC',font=f).grid(row=6, column=0, sticky=W, pady=10)

        gender = LabelFrame(right_frame,bg='#CCCCCC',padx=10,pady=10,)
        name = Entry(right_frame, font=f)
        email = Entry(right_frame,font=f)
        country = Entry(right_frame,font=f)
        male = Radiobutton(gender,text='Male',bg='#CCCCCC', variable=var,value='male',font=('Times', 10),)
        female = Radiobutton(gender,text='Female',bg='#CCCCCC', variable=var,value='female',font=('Times', 10))
        pwd = Entry(right_frame, font=f, show='*')
        pwd_again = Entry(right_frame, font=f, show='*')

        register = Button(right_frame,
                          command=lambda: [self.client.send(pickle.dumps([name.get(),email.get(),country.get(),var.get(), pwd.get()])), reg.destroy()],
                          width=15, text='Register', font=('Helvetica', 11), cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                   activeforeground='#252221')
        close = Button(right_frame, command=reg.destroy, text='Close', width=15, font=('Helvetica', 11), cursor='hand2',bg='#252221', fg='lightgray', activebackground='lightgray',
                   activeforeground='#252221')
        name.grid(row=0, column=1, pady=10, padx=20)
        email.grid(row=1, column=1, pady=10, padx=20)
        country.grid(row=2, column=1, pady=10, padx=20)
        pwd.grid(row=5, column=1, pady=10, padx=20)
        pwd_again.grid(row=6, column=1, pady=10, padx=20)
        close.grid(row=7, column=1, pady=10, padx=10)
        register.grid(row=7, column=0, pady=10, padx=10)
        right_frame.pack()

        gender.grid(row=3, column=1, pady=10, padx=20)
        male.pack(expand=True, side=LEFT)
        female.pack(expand=True, side=LEFT)
        self.midwin(reg,500,400)
        reg.mainloop()

    def login(self):
        log = Tk()
        log.config(bg='#252221')
        f = ('Helvetica', 14)
        var = StringVar()
        right_frame = Frame(log,bd=2,bg='#CCCCCC',padx=10,pady=10)
        Label(right_frame,text="Email", bg='#CCCCCC',font=f).grid(row=1, column=0, sticky=W, pady=10)
        Label(right_frame,text="Password", bg='#CCCCCC',font=f).grid(row=5, column=0, sticky=W, pady=10)

        email = Entry(right_frame,font=f)
        pwd = Entry(right_frame, font=f, show='*')
        login = Button(right_frame,
                          command=lambda: [self.client.send(pickle.dumps([email.get(), pwd.get()])), log.destroy()],
                          width=15, text='Login', font=('Helvetica', 11), cursor='hand2', bg='#252221', fg='lightgray', activebackground='lightgray',
                   activeforeground='#252221')
        close = Button(right_frame, command=log.destroy, text='Close', width=15, font=('Helvetica', 11), cursor='hand2',bg='#252221', fg='lightgray', activebackground='lightgray',
                   activeforeground='#252221')
        email.grid(row=1, column=1, pady=10, padx=20)
        pwd.grid(row=5, column=1, pady=10, padx=20)
        close.grid(row=7, column=1, pady=10, padx=10)
        login.grid(row=7, column=0, pady=10, padx=10)
        right_frame.pack()
        self.midwin(log,500,400)
        log.mainloop()

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
        a = int(root.winfo_screenwidth() / 2 - (x/2))
        b = int(root.winfo_screenheight() / 2 - (y/2))
        root.geometry('{}x{}+{}+{}'.format(x, y, a, b))


# class App():
#     def __init__(self):
#         self.world = Tk()
#         self.world.geometry(f"800x750")
#
#         self.world.protocol("WM_DELETE_WINDOW", self.on_closing)
#         self.world.bind("<Return>", self.search)
#
#         self.world.grid_columnconfigure(0, weight=1)
#         self.world.grid_columnconfigure(1, weight=0)
#         self.world.grid_columnconfigure(2, weight=0)
#         self.world.grid_rowconfigure(1, weight=1)
#
#         self.search_bar = tkinter.Entry(self.world, width=50)
#         self.search_bar.grid(row=0, column=0, pady=10, padx=10, sticky="we")
#
#         self.search_bar_button = tkinter.Button(self.world, width=8, text="Search", command=self.search)
#         self.search_bar_button.grid(row=0, column=1, pady=10, padx=10)
#
#         self.world.search_bar_clear = tkinter.Button(self.world, width=8, text="Clear", command=self.clear)
#         self.world.search_bar_clear.grid(row=0, column=2, pady=10, padx=10)
#
#         self.map_widget = TkinterMapView(self.world, width=800, height=600, corner_radius=0)
#         self.map_widget.grid(row=1, column=0, columnspan=3, sticky="nsew")
#
#         self.marker_list_box = tkinter.Listbox(self.world, height=8)
#         self.marker_list_box.grid(row=2, column=0, columnspan=1, sticky="ew", padx=10, pady=10)
#
#         self.listbox_button_frame = tkinter.Frame(self.world)
#         self.listbox_button_frame.grid(row=2, column=1, sticky="nsew", columnspan=2)
#
#         self.listbox_button_frame.grid_columnconfigure(0, weight=1)
#
#         self.save_marker_button = tkinter.Button(self.listbox_button_frame, width=20, text="save current marker",
#                                                  command=self.save_marker)
#         self.save_marker_button.grid(row=0, column=0, pady=10, padx=10)
#
#         self.clear_marker_button = tkinter.Button(self.listbox_button_frame, width=20, text="clear marker list",
#                                                   command=self.clear_marker_list)
#         self.clear_marker_button.grid(row=1, column=0, pady=10, padx=10)
#
#         self.connect_marker_button = tkinter.Button(self.listbox_button_frame, width=20, text="connect marker with path",
#                                                     command=self.connect_marker)
#         self.connect_marker_button.grid(row=2, column=0, pady=10, padx=10)
#
#         self.map_widget.set_address("Israel")
#
#         self.marker_list = []
#         self.marker_path = None
#
#         self.search_marker = None
#         self.search_in_progress = False
#
#     def search(self, event=None):
#         if not self.search_in_progress:
#             self.search_in_progress = True
#             if self.search_marker not in self.marker_list:
#                 self.map_widget.delete(self.search_marker)
#
#             address = self.search_bar.get()
#             self.search_marker = self.map_widget.set_address(address, marker=True)
#             if self.search_marker is False:
#                 # address was invalid (return value is False)
#                 self.search_marker = None
#             self.search_in_progress = False
#
#     def save_marker(self):
#         if self.search_marker is not None:
#             self.marker_list_box.insert(tkinter.END, f" {len(self.marker_list)}. {self.search_marker.text} ")
#             self.marker_list_box.see(tkinter.END)
#             self.marker_list.append(self.search_marker)
#
#     def clear_marker_list(self):
#         for marker in self.marker_list:
#             self.map_widget.delete(marker)
#
#         self.marker_list_box.delete(0, tkinter.END)
#         self.marker_list.clear()
#         self.connect_marker()
#
#     def connect_marker(self):
#         print(self.marker_list)
#         position_list = []
#
#         for marker in self.marker_list:
#             position_list.append(marker.position)
#
#         if self.marker_path is not None:
#             self.map_widget.delete(self.marker_path)
#
#         if len(position_list) > 0:
#             self.marker_path = self.map_widget.set_path(position_list)
#
#     def clear(self):
#         self.search_bar.delete(0, last=tkinter.END)
#         self.map_widget.delete(self.search_marker)
#
#     def on_closing(self, event=0):
#         self.world.destroy()
#
#     def start(self):
#         self.world.mainloop()


if __name__ == '__main__':
    print('___INITIALIZING___')
    c = Client(user)
