from tkinter import Label
from tkinter import BOTH, YES, CENTER, TOP
from PIL import Image, ImageTk
import piexif

from image import orientate


class ImagePanel(Label):
    def __init__(self, parent):

        Label.__init__(self, parent)

        # image handle to prevent garbage collection
        # of current display image
        self.imh = None
        self.labelImage = Label(self, image=self.imh)
        self.labelImage.pack(side=TOP, fill=BOTH, expand=YES, anchor=CENTER)

    def load_image(self, path):

        im = orientate(Image.open(path))
        im.thumbnail((self.labelImage.winfo_width(), self.labelImage.winfo_height()-20), Image.LANCZOS )
        self.imh = ImageTk.PhotoImage(im)
        self.labelImage.configure(image=self.imh, anchor=CENTER)

        self.current_image_path = path
        return im

        # # Haal de Exif-data op
        # exif_data = piexif.load(im.info['exif'])
        #
        # # Toon de metadata
        # for ifd_name in exif_data:
        #     print(f"\n--- {ifd_name} ---")
        #     if not isinstance(exif_data[ifd_name], dict):
        #         continue
        #     for tag, value in exif_data[ifd_name].items():
        #         tag_name = piexif.TAGS[ifd_name][tag]["name"]
        #         print(f"{tag_name}: {value}")
