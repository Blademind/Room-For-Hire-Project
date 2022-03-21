import pickle
import time
import tkinter.messagebox
from socket import *
from tkinter import *
import threading
import sqlite3

"""
Client by Alon Levy
"""


class Client:
    def __init__(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.__BUF = 1024
        self.__ADDR = ('127.0.0.1', 50000)  # where to connect
        self.client.connect(self.__ADDR)
        threading.Thread(target=self.listen).start()
        print('___SUCCESS___')
        self.main()

    def listen(self):
        while 1:
            data = self.client.recv(self.__BUF)
            if not data:
                break
            tkinter.messagebox.showinfo('Message from Server', data.decode())

    def main(self):
        root = Tk()
        reg1 = Button(root, command=self.register, text='Register', font=('Helvetica', 11), cursor='hand2',bg='#252221', fg='lightgray', activebackground='lightgray',
                   activeforeground='#252221')
        reg1.pack(anchor=E)
        findroom = Button(root, command=self.register, width=25,height=2,
                      text='Find a Room', font=('Helvetica', 14),
                      cursor='hand2',bg='#252221', fg='lightgray', activebackground='lightgray',
                      activeforeground='#252221')
        findroom.pack(pady=10, padx=20)
        addroom = Button(root, command=lambda: self.pop(reg), width=25,height=2,
                      text='Add a Room', font=('Helvetica', 14),
                      cursor='hand2',bg='#252221', fg='lightgray', activebackground='lightgray',
                      activeforeground='#252221')
        addroom.pack(pady=10, padx=20)
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
        self.midwin(root,300,250)
        root.mainloop()

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
                          command=lambda: self.client.send(pickle.dumps([name.get(),email.get(),country.get(),var.get(), pwd.get()])),
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

    # Do you wish to exit the program entirely?
    def pop(self, root):
        popup = Tk()
        popup.config(bg='lightgray')
        lb3 = Label(popup, text='Do you wish to exit?', font=("Helvetica", 15), bg='#252221', fg='lightgray')
        lb3.pack(fill=BOTH)
        # Destroy both popup and root windows
        yes = Button(popup, text='Yes', command=lambda: [popup.destroy(), root.destroy()], bg='#252221',
                     fg='lightgray', activebackground='lightgray', activeforeground='#252221', padx=10)
        yes.pack(pady=10, side=RIGHT)

        no = Button(popup, text='No', command=popup.destroy, bg='#252221', fg='lightgray', activebackground='lightgray',
                    activeforeground='#252221', padx=10)  # Destroy popup window
        no.pack(pady=10, side=RIGHT)
        self.midwin(popup, 300, 80)  # place window in the center

    def midwin(self, root, x, y):
        a = int(root.winfo_screenwidth() / 2 - (x/2))
        b = int(root.winfo_screenheight() / 2 - (y/2))
        root.geometry('{}x{}+{}+{}'.format(x, y, a, b))


if __name__ == '__main__':
    print('___INITIALIZING___')
    c = Client()
