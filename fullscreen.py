from tkinter import Label, TOP, BOTH, YES, CENTER
from PIL import Image, ImageTk
from modal import Modal
from image import orientate, FILETYPES


class FullScreen(Modal):

    def __init__(self, root):
        Modal.__init__(self)
        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        self.top.geometry(f"{self.width}x{self.height}+0+0")
        self.imh = None

        self.labelImage = Label(self.top, image=self.imh, bg="black")
        self.labelImage.pack(side=TOP, fill=BOTH, expand=YES, anchor=CENTER)
        self.top.bind('<space>', self.next)
        self.top.bind('<Down>', self.next)
        self.top.bind('<Right>', self.next)
        self.top.bind('<Up>', self.previous)
        self.top.bind('<Left>', self.previous)

    def show(self, full_path):
        Modal.show(self)
        path = full_path.parent
        self.list = []  # type hint
        self.list = [p for p in sorted(path.iterdir()) if p.is_file() and p.suffix in FILETYPES]

        try:
            self.current = self.list.index(full_path)
        except ValueError:
            self.current = 0

        self.display_image()

    def next(self, event):
        if self.current < len(self.list)-1:
            self.current += 1
            self.display_image()

    def previous(self, event):
        if self.current > 0:
            self.current -= 1
            self.display_image()

    def display_image(self):
        path = self.list[self.current]

        im = orientate(Image.open(path))

        im.thumbnail((self.width, self.height), Image.LANCZOS)

        self.imh = ImageTk.PhotoImage(im)  # ref to image is kept to prevent garbage collection bug
        self.labelImage.configure(image=self.imh)
