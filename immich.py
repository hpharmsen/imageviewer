# See documentation at https://immich.app/docs/api
import base64
import datetime
import hashlib
import mimetypes
import os
import json
import sys
import time
from functools import wraps

import requests
from PIL import Image
from dotenv import load_dotenv

from exif import Exif

def retry_on_connection_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                print(".", end='')
                time.sleep(10)
    return wrapper


class Immich:
    def __init__(self, url=''):
        if not url:
            url = os.environ['IMMICH_URL']
        self.url = url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': os.environ['IMMICH_API_KEY'],
        }

    @retry_on_connection_error
    def get(self, endpoint, payload):
        url = f"{self.url}/api/{endpoint}"
        response = requests.get(url, headers=self.headers, params=payload)
        if 200 <= response.status_code < 300:
            return json.loads(response.text)

    @retry_on_connection_error
    def post(self, endpoint, payload, data=None):
        url = f"{self.url}/api/{endpoint}"
        if data:
            response = requests.post(url, headers=self.headers, data=data)
        else:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
        return response.status_code, response.json()

    @retry_on_connection_error
    def put(self, endpoint: str, payload: dict):
        url = f"{self.url}/api/{endpoint}"
        res = requests.put(url, headers=self.headers, data=payload)
        if 200 <= res.status_code < 300:
            return res.json()
        panic(f"PUT {url} failed: {res.status_code} {res.text}")

    def create_album(self, name: str, description:str = '', assets: list = None):
        for album in self.albums():
            if album['albumName'] == name:
                return album['id']
        payload = {"albumName": name,  "description": description}
        if assets:
            payload['assetIds'] = assets
        status, data = self.post("albums", payload)
        if status == 201:
            return data['id']

    @retry_on_connection_error
    def delete(self, endpoint: str, payload: dict):
        url = f"{self.url}/api/{endpoint}"
        return requests.delete(url, headers=self.headers, data=payload)

    ##### Assets #####

    def upload_asset(self, file_path: str):
        # Returns: {'id': '948070b4-150d-49d3-89fd-db47095ffaa9', 'status': 'created'}
        local_checksum = calulate_checksum(file_path)
        search_results = self.find_assets({'checksum': local_checksum})
        if search_results:
            return search_results[0]['id']
        headers = {
            'Accept': 'application/json',
            'x-api-key': os.environ['IMMICH_API_KEY'],
            'x-immich-checksum': local_checksum
        }
        folder = file_path.split('/')[-2]
        payload = {
            'deviceAssetId': file_path,
            'deviceId': 'Macbook',
            'fileCreatedAt': folder[:4]+datetime.datetime.fromtimestamp(os.stat(file_path).st_birthtime).isoformat()[4:],
            'fileModifiedAt': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
        if is_image(file_path):
            payload['description'] = Exif(file_path).description

        with open(file_path, 'rb') as f:
            files = {'assetData': (os.path.basename(file_path), f, 'image/jpeg')}
            response = self._post_asset(f"{self.url}/api/assets", headers=headers, files=files, payload=payload)
        if 200 <= response.status_code < 300:
            data = response.json()
            return data['id']
        elif response.status_code == 413:
            print(f"File too large ({os.path.getsize(file_path)}): {file_path}")
            # 123_234_464
        else:
            panic(f"Upload failed: {response.status_code} {response.text}")

    @retry_on_connection_error
    def _post_asset(self, url, headers, files, payload):
        return requests.post(url, headers=headers, files=files, data=payload)

    def asset_info(self, asset_id: str):
        return self.get(f"assets/{asset_id}", {})

    def find_assets(self, searchparams: dict):
        result = []
        while True:
            status, data = self.post("search/metadata", searchparams)
            if status == 200:
                result += data['assets']['items'] # Voor nu alleen de eerste pagina
                if True or not data['assets']['nextPage']:
                    return result
                searchparams['page'] = data['assets']['nextPage']
            else:
                panic(f"Search failed: {status} {data}")

    def delete_assets(self, asset_ids: list):
        payload = json.dumps({
            "force": True,
            "ids":asset_ids
        })
        return self.delete("assets", payload=payload)

    ##### Albums ####

    def albums(self):
        return self.get("albums", {})

    def album_info(self, album_id: str):
        return self.get(f"albums/{album_id}", {})

    def delete_album(self, album_id: str):
        return self.delete(f"albums/{album_id}", {})

    def add_asset_to_album(self, album_id: str, asset_id: str):
        payload = json.dumps({"ids": [asset_id]})
        return self.put(f"albums/{album_id}/assets", payload)

    def remove_asset_from_album(self, asset_id: str, album_id: str):
        payload = {"ids": [album_id]}
        return self.delete("assets/{asset_id}/albums", payload)

    def move_to_different_album(self, asset_id: str, album_id: str):
        asset = self.asset_info(asset_id)
        old_album_id = asset['albums'][0]['id']
        self.remove_asset_from_album(asset_id, old_album_id)
        self.add_asset_to_album(album_id, asset_id)

    ##### Bulk #####

    def upload_folder(self, path: str):
        album_name = path.rsplit('/', 1)[1]
        album_id = self.create_album(album_name)
        for file in sorted(os.listdir(path)):
            full_path = f"{path}/{file}"
            if is_image(full_path):
                print(full_path)
                asset_id = self.upload_asset(full_path)
                if asset_id:
                    self.add_asset_to_album(album_id, asset_id)


def is_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        return False


def is_image_or_video(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith("video"):
        return True
    if mime_type and mime_type.startswith("image"):
        return is_image(file_path)
    return False


def calulate_checksum(file_path: str):
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha1(f.read()).digest()
    checksum = base64.b64encode(file_hash).decode("utf-8")
    return checksum


def panic(message:str):
    print(message)
    sys.exit()