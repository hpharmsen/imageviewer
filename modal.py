from tkinter import Toplevel


class Modal():
    def __init__(self):

        self.top = Toplevel(bg="black")
        self.top.overrideredirect(True)  # No border
        self.top.overrideredirect(False)

        self.top.bind("<Escape>", self.hide)  # Or .destroy
        self.hide()

    def show(self):
        # self.fs.update()
        self.top.deiconify()
        self.top.lift()
        self.top.grab_set()

    def hide(self, event=None):
        self.top.withdraw()
        self.top.grab_release()
