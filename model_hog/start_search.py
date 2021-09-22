import json
import os
import shutil

from model_hog.facesearch import Faces_Recognition
from config import *


def search_child_photos(user_id, urls):
    """ 
    Input: путь к папке с фотографиями ребенка, путь к папке с фотографиями из соцсетей
    Output: словарь {'имя фотографии': 'закодированная фотография'}
    """
    
    man_dir = f'{UPLOAD_DIR}/{user_id}/{MAN_PHOTO_DIR}'
    vk_album_dir = f'{UPLOAD_DIR}/{user_id}/{VK_PHOTO_DIR}'

    fr = Faces_Recognition(man_dir, vk_album_dir, urls)
    fr.check_photo_social()
    
    shutil.rmtree(man_dir)

    with open(f'{UPLOAD_DIR}/{user_id}/{DATA_FILENAME}', 'w') as outfile:
        json.dump(fr.response, outfile)
    
