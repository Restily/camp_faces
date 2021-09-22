import os

from config import *


def path_dirs(dir_name):
    """ Возвращает пути к папкам, если они уже существуют """
    return f'{UPLOAD_DIR}/{dir_name}/{MAN_PHOTO_DIR}'


def get_path_dir(root_dir, child_dir):
    """ Возвращает имя папки"""
    path_dir =  f'{root_dir}/{child_dir}'

    os.mkdir(path_dir)
    
    return path_dir


def create_dirs(dir_name):
    """ Создание новой папки пользователя """
    if dir_name in os.listdir(UPLOAD_DIR): # проверка, есть ли уже папка в директории
        return path_dirs(dir_name)

    user_dir = get_path_dir(UPLOAD_DIR, dir_name) # создание папки юзера
 
    man_dir = get_path_dir(user_dir, MAN_PHOTO_DIR) # создание папки с фотографией человека

    return man_dir