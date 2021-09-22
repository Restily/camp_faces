import uuid
import base64
import os
import time

from model_hog.start_search import search_child_photos
from config import *


def save_image(decode_image, image_name, image_dir):
    with open(f'{image_dir}/{image_name}', mode='wb') as image:
        image.write(base64.b64decode(decode_image))


def encode_image(image_dir):
    with open(image_dir, mode='rb') as image:
        image_code = image.read()
    
    return base64.encodebytes(image_code).decode('utf-8')


def generate_user_id():
    """ Создание request id """
    return str(uuid.uuid4())[:8]


def check_date_archives():
    for user in os.listdir(UPLOAD_DIR):
        archive_path = f'{UPLOAD_DIR}/{user}/{ARCHIVE_NAME}'

        if os.path.exists(archive_path):
            if time.time() - os.path.getctime(archive_path) > 1800:
                os.remove(archive_path)
                os.rmdir(f'{UPLOAD_DIR}/{user}')


def start_running_task(vk, user_id):
    """ Запуск процесса """
    vk_urls = vk.get_albums_photos()

    print(time.time(), len(vk_urls))

    search_child_photos(user_id, vk_urls) # запуск нейронки