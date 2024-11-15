from dotenv import load_dotenv

from immich import Immich, is_image_or_video, calulate_checksum

import os


def sync_folder(im: Immich, directory: str):
    print('Syncing ' + directory)
    album_name = directory.rsplit('/', 1)[1]
    album_id = im.create_album(album_name)

    # Get the hashes of all files in this album
    album_info = im.album_info(album_id)
    album_contents = {asset['checksum']: asset['id'] for asset in album_info['assets']}

    # Get the hashes of all files in the directory
    dir_contents = {}
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if not os.path.isfile(file_path) or not is_image_or_video(file_path):
            continue
        dir_contents[calulate_checksum(file_path)] = file_path

    # Delete all images from the album that are not in the directory (anymore)
    to_delete = [asset_id for checksum, asset_id in album_contents.items() if checksum not in dir_contents]
    if to_delete:
        print(f'Deleting {len(to_delete)} assets')
        im.delete_assets(to_delete)

    # Add all images from the director that are not in the album
    to_add = [file_path for checksum, file_path in dir_contents.items() if checksum not in album_contents]
    for file_path in to_add:
        print('Uploading ' + file_path)
        asset_id = im.upload_asset(file_path)
        if asset_id:
            im.add_asset_to_album(album_id, asset_id)


def delete_assets_without_album(im: Immich):
    to_delete = [asset['id'] for asset in im.find_assets({"isNotInAlbum": True})]
    print(f'Deleting {len(to_delete)} without album')
    im.delete_assets(to_delete)

def is_int(s: str):
    try:
        int(s)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    load_dotenv()
    im = Immich()
    delete_assets_without_album(im)
    for directory in sorted(os.listdir('/Users/hp/foto')):
        if is_int(directory[:4]):
            sync_folder(im, f'/Users/hp/foto/{directory}')