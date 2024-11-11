from modal import Modal
from tkinter import Toplevel, Label, Entry, END

class FilenamePopup(Modal):
    def __init__(self ):
        Modal.__init__(self)

        self.top.geometry("200x60")

        Label(self.top,text="Filename").pack()

        self.entry=Entry(self.top)
        self.entry.pack()
        self.entry.bind('<Return>', self.action)
        self.hide()

    def show(self, path, change_filename_callback):
        Modal.show(self)

        self.path = path
        self.change_filename_callback = change_filename_callback
        self.entry.delete(0, END)
        self.entry.insert(END, path.name)
        self.entry.focus()


    def action(self, event):
        self.change_filename_callback( self.path, self.entry.get() )
        self.hide()

