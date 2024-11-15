# File: imageviewer.py

from tkinter import Tk, ttk, Frame, filedialog  # ttk = TkInter Tile widgets
from tkinter import X, Y, TOP, BOTH, LEFT, Text # brew install python-tk to get it working
from pathlib import Path

import piexif

import image
from dirpanel import DirPanel
from exif import get_exif, Exif
from filepanel import FilePanel
from imagepanel import ImagePanel
from filenamepopup import FilenamePopup
from fullscreen import FullScreen
import subprocess
import collections


INITIAL_PATH = Path('/Users/hp/foto/')


def _copy(self, target):
    import shutil
    assert self.is_file()
    shutil.copy(self, target)
Path.copy = _copy

# SpecialActions are used to maintain a list of move or copy actions to previously used locations
SpecialAction = collections.namedtuple('SpecialAction', 'action path')


class ImageViewer(ttk.Frame):
    def __init__(self):
        self.special_actions = []

        ttk.Frame.__init__(self, name='imageviewer')
        self.master.title('Image Viewer')
        self.master.geometry("1200x700")
        self.master.bind('<Control-d>', self.delete_image)
        self.master.bind('<Control-e>', self.edit_filename)
        self.master.bind('<Control-f>', self.show_in_finder)
        self.master.bind('<Control-c>', self.copy_image)
        self.master.bind('<Control-m>', self.move_image)
        self.master.bind('<Control-r>', self.rotate_image)
        self.master.bind('<Control-l>', self.lucky)
        self.master.bind('<Return>', self.switch_to_fullscreen)
        self.master.bind('<Key>', self.keypress)

        # Main panel
        self.top = Frame(name='imageviewer')
        self.top.pack(side=TOP, fill=BOTH, expand=Y)

        # Top bar: dirPanel
        self.dirPanel = DirPanel(self.top, change_dir_callback=self.dirpanel_dir_change)
        self.dirPanel.pack(fill=X, expand=False)

        # Side bar: sidebar with filePanel and helpPanel
        sidebar = Frame(self.top)
        sidebar.pack(side=LEFT, fill=BOTH)

        self.filePanel = FilePanel(sidebar,
                                   select_item_callback=self.filepanel_select_item,
                                   change_dir_callback=self.filepanel_dir_change)
        self.filePanel.pack(side=TOP, fill=BOTH, expand=True)

        self.helpPanel = ttk.Label(sidebar, text=self.help_text())
        self.helpPanel.pack(side=TOP, fill=BOTH)

        # Image panel: rest of the window
        self.imagePanel = ImagePanel(self.top)
        self.imagePanel.pack(fill=BOTH, expand=1)

        # Text edit balk voor de beschrijving
        self.text_entry = Text(self.top, height=2)
        self.text_entry.pack(fill=X, expand=False)
        self.text_entry.bind("<<Modified>>", self._on_text_change)

        # Bind Control+V (Windows/Linux) en Command+V (macOS) voor plakken
        self.text_entry.bind("<Control-v>", self._on_text_paste)
        self.text_entry.bind("<Command-v>", self._on_text_paste)
        self.text_entry.bind("<Button-2>", self._on_text_paste)  # Voor muisklik plakken
        # Set things in motion
        self.dirPanel.change_path(INITIAL_PATH)

    def _on_text_change(self, event):
        # Roep de functie aan
        self.update_image_description()

        # Reset de modified status zodat het event opnieuw kan worden getriggerd
        self.text_entry.edit_modified(False)

    def _on_text_paste(self, event=None):
        # Plakken, gevolgd door update_image_description
        self.after(1, self._on_text_change)  # Delay om geplakte tekst te detecteren

    def load_image(self, path):
        im = self.imagePanel.load_image(path)
        # Haal Exif-data op en laad beschrijving in text_entry
        try:
            self.text_entry.delete("1.0", "end")
            self.text_entry.insert("1.0", Exif(im).description)
        except KeyError:
            self.text_entry.delete("1.0", "end")  # Wis text_entry als er geen beschrijving is


    def update_image_description(self):
        import piexif
        from PIL import Image

        path = self.filePanel.current_item()
        if not path or not path.is_file():
            return

        # Save in Exif
        new_description = self.text_entry.get("1.0",'end-1c')
        im = Image.open(path)
        Exif(im).description = new_description

    # -- callbacks van filepanel en dirpanel --

    def dirpanel_dir_change(self, dir):
        ''' New directory chosen in the dir panel, register and notify file panel '''
        self.filePanel.load_dir(dir)

    def filepanel_dir_change(self, path):
        ''' New directory chosen in the file panel, register and notify other panels '''
        self.dirPanel.change_path(path)

    def filepanel_select_item(self, path):
        self.load_image(path)

    # -- Editing the file name --

    def edit_filename(self, event):
        path = self.filePanel.current_item()
        if not path:
            return
        filenamepopup.show(path, self.change_filename)

    def change_filename(self, path, newname):
        path.replace(path.parent / newname)
        self.filePanel.edit_current(newname)

    # -- show in finder --

    def show_in_finder(self, event):
        path = self.filePanel.current_item()
        if not path:
            return
        subprocess.Popen(['open', '-R', '%s' % (path)])

    # -- delete image --

    def delete_image(self, event):
        path = self.filePanel.current_item()
        if not path or not path.is_file():
            return
        trash = Path('~').expanduser() / '.Trash'
        path.replace(trash / path.name)
        self.filePanel.delete_current()

    # -- copying and moving --

    def copy_image(self, event):
        path = self.filePanel.current_item()
        if not path or not path.is_file():
            return
        new_dir = filedialog.askdirectory(initialdir=path, title="Copy photo")
        if new_dir:
            new_path = Path(new_dir)
            path.copy(new_path / path.name)
            self.add_special_action('copy', new_path)

    def move_image(self, event):
        path = self.filePanel.current_item()
        if not path or not path.is_file():
            return
        new_dir = filedialog.askdirectory(initialdir=path, title="Move photo")
        if new_dir:
            new_path = Path(new_dir)
            path.replace(new_path / path.name)
            self.filePanel.delete_current()
            self.add_special_action('move', new_path)

    # -- Rotate image ---

    def rotate_image(self, event):
        path = self.filePanel.current_item()
        if not path or not path.is_file():
            return
        image.rotate(path)
        self.load_image(path)

    # -- Lucky ---

    def lucky(self, event):
        path = self.filePanel.current_item()
        if not path or not path.is_file():
            return
        image.lucky(path)
        self.load_image(path)

    # -- Full screen --

    def switch_to_fullscreen(self, event):
        path = self.filePanel.current_item()
        if not path:
            return
        if path.is_file():
            fullscreen.show(path)
        elif path.is_dir():
            self.dirPanel.change_path(path)

    # -- showing the help text ---

    def help_text(self):
        extra_locations = [f'^{i} - {action.action} to {action.path.name}'
                           for i, action in enumerate(self.special_actions, 1)]
        return '\n\n' + \
            'Down/Up - Next/previous\n' + \
            '^D - Delete image\n' + \
            '^E - Edit filename\n' + \
            '^F - Show image in finder\n' + \
            '^C - Copy image\n' + \
            '^M - Move image\n' + \
            '^R - Rotate image\n' + \
            '\n'.join(extra_locations) + '\n\n'

    def add_special_action(self, action, path):
        special_action = SpecialAction(action, path)
        if special_action not in self.special_actions:
            self.special_actions += [special_action]
            self.helpPanel['text'] = self.help_text()

    # -- Special actions ---

    def keypress(self, event):
        key = event.keysym
        path = self.filePanel.current_item()

        # Controleer of het event een Control-modifier bevat en een cijfer is
        if event.state & 0x4 and key.isdigit() and int(key) > 0 and int(key) <= len(self.special_actions) and path and path.is_file():
            action = self.special_actions[int(key) - 1]
            if action.action == 'move':
                path.replace(action.path / path.name)
                self.filePanel.delete_current()
            elif action.action == 'copy':
                path.copy(action.path / path.name)
        elif event.char.isprintable() or key in ["Left", "Right", "BackSpace"]:
            current_focus = self.master.focus_get()
            self.text_entry.focus_set()
            self.text_entry.insert("insert", event.char)
            # Herstel de oorspronkelijke focus
            if current_focus:
                current_focus.focus_set()

if __name__ == '__main__':
    # ImageViewer().mainloop()
    root = Tk()
    viewer = ImageViewer()
    filenamepopup = FilenamePopup()
    fullscreen = FullScreen(root)
    root.mainloop()
