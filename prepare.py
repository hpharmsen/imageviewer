'''Prepares a directory with photos by:
- Converting them to jpeg if needed
- Renaming them to yyyy-mm-dd hh:mm:ss format
'''
import sys
from datetime import datetime, timedelta
from pathlib import Path
from time import strptime

from PIL import ExifTags, Image
from wand.image import Image as HeicImage

from image import orientate, FILETYPES

import subprocess

class DateNotFoundException(Exception):
    pass

def get_photo_date_taken(file):
    """Gets the date taken for a photo through a shell."""

    #if file.suffix.lower() != '.heic':
    #    return datetime.fromtimestamp(file.stat().st_birthtime)

    # Onderstaande is nodig omdat bij foto's die je opslaat de mac de filetijd aanpast en we willen de foto creatietijd
    cmd = "mdls '%s'" % file
    output = subprocess.check_output(cmd, shell = True)
    lines = output.decode("ascii").split("\n")
    for l in lines:
        if "kMDItemContentCreationDate" in l:
            datetime_str = l.split("= ")[1]
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S +0000")
    raise DateNotFoundException("No EXIF date taken found for file %s" % file)

def set_right_name( file ):
    #return file # Nu even niks omdat os niet Contents Created time kan uitlezen.
    file_format = '%Y-%m-%d %H.%M.%S'
    try:
        date_in_name = strptime(file.stem, file_format)
    except:
        # Not in the right format rename to created date/time
        created = get_photo_date_taken( file )
        new_name = created.strftime(file_format) + file.suffix
        new_path = file.parent / new_name
        while new_path.is_file():
            created += timedelta(0, 1)  # 0 days, 1 second
            new_name = created.strftime(file_format) + file.suffix
            new_path = file.parent / new_name
        file = file.rename(new_path)
    return file

def save_backup(file: Path):
    backup_dir = file.parent / 'backup'
    backup_dir.mkdir(exist_ok=True)  # create if necessary
    backup_file =  backup_dir / file.name
    file.rename( backup_file )

def convert_from_heic(file):
    im = HeicImage(filename=file)
    im.format = 'jpg'
    im.save(filename=file.with_suffix('.jpg'))
    im.close()

def convert_from_other(file):
    # creating a image object (main image)
    im = orientate(Image.open(file))
    # save a image using extension
    im = im.convert('RGB')
    im.save(file.with_suffix('.jpg'))
    im.close()


def prepare_folder(folder):
    path = Path( folder )
    for file in path.iterdir():
        lower_suffix = file.suffix.lower()

        if not lower_suffix in FILETYPES + ['.heic']:
            continue
        print( file )

        # Rename if needed
        oldname = file.name
        file = set_right_name( file )

        # convert to jpeg if needed
        if not lower_suffix in ('.jpeg','.jpg'):
            if lower_suffix == '.heic':
                convert_from_heic( file )
            else:
                convert_from_other( file )
            save_backup( file )


if __name__=='__main__':
    folder = sys.argv[1]
    prepare_folder(folder)