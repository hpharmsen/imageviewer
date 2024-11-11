import tkinter
import tkinter.ttk
from pathlib import Path

import _tkinter

from image import FILETYPES


class FilePanel(tkinter.ttk.Labelframe):

    def __init__(self, parent, select_item_callback, change_dir_callback):

        tkinter.ttk.Labelframe.__init__(self, parent, text='Files')

        self.path = Path()
        self.select_item_callback = select_item_callback
        self.change_dir_callback = change_dir_callback

        self.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # there is no ttk.Listbox; however, ttk.Scrollbar
        # works fine with the tkinter Listbox
        self.values = tkinter.Variable(value=[])
        self.filelist = tkinter.Listbox(self, listvariable=self.values, width=20, height=20)
        sbar = tkinter.ttk.Scrollbar(self, command=self.filelist.yview, orient=tkinter.VERTICAL)
        self.filelist.configure(yscrollcommand=sbar.set)
        # self.load_dir()

        self.filelist.pack(side=tkinter.LEFT, fill=tkinter.Y, expand=tkinter.Y)
        sbar.pack(side=tkinter.LEFT, fill=tkinter.Y, expand=tkinter.Y)

        self.filelist.bind('<<ListboxSelect>>', self._select_item)
        self.filelist.bind('<Double-Button-1>', self._change_dir)
        # self.filelist.bind('<Key>', self.key)

        self.filelist.select_set(0)  # This only sets focus on the first item.
        self.filelist.event_generate("<<ListboxSelect>>")

    def _select_item(self, event):
        try:
            item = self.filelist.get(self.filelist.curselection())
        except _tkinter.TclError:
            return
        path = self.path / item

        if path.is_file():
            self.select_item_callback(path)

    def current_item(self):
        selection = self.filelist.curselection()
        if not selection:
            return Path('')
        item = self.filelist.get(selection)
        if item == '..':
            return self.path.parent
        else:
            return self.path / item

    def _change_dir(self, event):
        path = self.current_item()
        if path.is_dir():
            self.change_dir_callback(path)

    def load_dir(self, path):

        self.path = path
        self.filelist.delete(0, tkinter.END)
        self.filelist.insert(tkinter.END, '..')
        # populate files list with filenames from
        # selected directory
        for f in sorted(path.iterdir()):
            if (f.is_dir() or f.suffix in FILETYPES) and str(f.name)[0] != '.':
                self.filelist.insert(tkinter.END, f.name)

        # prevent <Return> event from propagating to
        # windows higher up in the hierarchy
        return 'break'  # ?? nodig?

    def delete_current(self):
        # Delete from Listbox
        selection = self.filelist.curselection()[0]
        self.filelist.delete(selection)
        # Set next item active
        self.filelist.select_set(selection)
        self.filelist.event_generate("<<ListboxSelect>>")

    def edit_current(self, newname):
        if not self.filelist.curselection():
            return
        selection = self.filelist.curselection()[0]
        self.filelist.delete(selection)
        self.filelist.insert(selection, newname)
        self.filelist.select_set(selection)
