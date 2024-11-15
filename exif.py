import struct

import piexif
from PIL import Image

class Exif:
    def __init__(self, im):
        if isinstance(im, str):
            self.im = Image.open(im)
            self.path = im
        else:
            self.im = im
            self.path = None
        try:
            self.data = piexif.load(self.im.info['exif']) if 'exif' in self.im.info else {"0th": {}}
        except struct.error:
            self.data = {"0th": {}}

    @property
    def description(self):
        return self.data["0th"].get(piexif.ImageIFD.ImageDescription, b"").decode("utf-8")

    @description.setter
    def description(self, value):
        if self.data["0th"].get(piexif.ImageIFD.ImageDescription) != value.encode("utf-8"):
            self.data["0th"][piexif.ImageIFD.ImageDescription] = value.encode("utf-8")
            exif_bytes = piexif.dump(self.data)
            if self.path:
                self.im.save(self.path, exif=exif_bytes)


if __name__=="__main__":
    import json
    a = get_exif('/Users/hp/foto/1993 diversen/1993 HP bij de informatiezuil 2.jpg')
    pass