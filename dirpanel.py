from tkinter import ttk, StringVar, filedialog, TOP, LEFT, BOTH, Y
from pathlib import Path


class DirPanel(ttk.Labelframe):
    def __init__(self, parent, change_dir_callback):

        ttk.Labelframe.__init__(self, parent, text='Directory')

        self.change_dir_callback = change_dir_callback

        self.pack(side=TOP, fill=BOTH, expand=Y)

        # self.curpath = os.path.join(os.getcwd(), 'images')  # current path
        self.imagepath = Path()
        self.dirName = StringVar()  # entry control variable
        self.dirName.set(self.imagepath)

        self.entry = ttk.Entry(self, width=30, textvariable=self.dirName)
        self.entry.pack(side=LEFT, fill=BOTH, padx='2m', pady='2m', expand=Y)
        self.entry.bind('<Return>', self._change_dir)

        btn = ttk.Button(self, text='Directory...', command=self._select_dir)
        btn.pack(side=LEFT, padx=(0, '2m'), pady='2m')

    def _change_dir(self, event):
        # print( 'Dirpanel select ', self.dirName.get() )
        self.change_dir_callback(Path(self.dirName.get()))

    def _select_dir(self):
        dir = filedialog.askdirectory(initialdir=self.dirName.get(),
                                      parent=self,
                                      title='Select a new files image directory',
                                      mustexist=True)  # only existing dirs
        if dir:
            self.change_path(dir)

    def focus(self):
        self.entry.focus_set()

    def get_path(self):
        return Path(self.dirName.get())

    def change_path(self, dir):
        self.dirName.set(dir)
        self.change_dir_callback(Path(dir))
