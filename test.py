#!/usr/bin/python
import tkinter as tk

class App(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent)

        self.parent = parent

        self.initUI()

    def initUI(self):

        self.parent.title("Fullscreen Application")

        self.pack(fill="both", expand=True, side="top")

        self.parent.wm_state("zoomed")

        self.parent.bind("<Return>", self.fullscreen_toggle)
        self.parent.bind("<Escape>", self.fullscreen_cancel)

        self.fullscreen_toggle()

        self.label = tk.Label(self, text="Fullscreen", font=("default",120), fg="black")
        self.label.pack(side="top", fill="both", expand=True)

    def fullscreen_toggle(self, event="none"):

        self.parent.focus_set()
        self.parent.overrideredirect(True)
        self.parent.overrideredirect(False) #added for a toggle effect, not fully sure why it's like this on Mac OS
        self.parent.attributes("-fullscreen", True)
        self.parent.wm_att§ributes("-topmost", 1)

    def fullscreen_cancel(self, event="none"):

        self.parent.overrideredirect(False)
        self.parent.attributes("-fullscreen", False)
        self.parent.wm_attributes("-topmost", 0)

        self.centerWindow()

    def centerWindow(self):

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()

        w = sw*0.7
        h = sh*0.7

        x = (sw-w)/2
        y = (sh-h)/2

        self.parent.geometry("%dx%d+%d+%d" % (w, h, x, y))

if __name__ == "__main__":
    root = tk.Tk()
    App(root).pack(side="top", fill="both", expand=True)
    root.mainloop()