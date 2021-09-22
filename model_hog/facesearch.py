import os
# import shutil

import numpy as np
from PIL import Image
import face_recognition
import requests

from config import *


class Faces_Recognition():

    def __init__(self, photo_of_man_dir, vk_album_dir, urls):
        """ На вход подаются:
            -> папка фотографией человека
            -> папка с альбомом
        """
        self.error_mean = 0.61
        self.model = 'hog'  # можно было бы использовать CUDA, но нужен графический процессор от nvidia (модель cnn, быстрее и лучше)
        self.photo_of_man_dir = photo_of_man_dir
        self.vk_album_dir = vk_album_dir
        
        self.urls = urls

        self.child_faces = self.faces_of_child()


    def load_image_file(self, image_url):
        image = Image.open(requests.get(image_url, stream=True).raw)
        
        return np.array(image.convert('RGB'))


    def enconding_photo(self, photo):
        """ Создание дескриптора фото """
        ph_locations = face_recognition.face_locations(photo, model=self.model)

        ph_encodings = face_recognition.face_encodings(photo, ph_locations)

        return ph_encodings

    
    def faces_of_child(self):
        """ Создание дескрипторов для фото ребенка """
        child_faces = []

        for filename in os.listdir(self.photo_of_man_dir):
            photo = Image.open(f'{self.photo_of_man_dir}/{filename}')

            photo_enc = np.array(photo.convert('RGB'))

            child_faces.append(self.enconding_photo(photo_enc)[0])

        return child_faces
    

    def check_photo_social(self):
        """ Модель для нахождения и сравнения лиц """
        self.response = []            

        while True:
            try:
                mark = False

                image_url = self.urls.popleft()

                image = self.load_image_file(image_url)

                encodings = self.enconding_photo(image)

                for face_encoding in encodings:

                    # Сравниваем лицо ребенка и лица на фотографии
                    results = face_recognition.compare_faces(self.child_faces, face_encoding, self.error_mean)

                    # Если нет совпадений на фотографиях, то удаляем это фото
                    if True in results:
                        self.response.append(image_url)
                        break

                # if not mark:
                #     file_for_remove = f"{self.vk_album_dir}/{filename}"
                #     os.remove(file_for_remove)

            except IndexError:
                break


    # def photos_to_archive(self):
    #     """ Создание архива из всех подходящих фотографий """
    #     return shutil.make_archive("result_archive", 'zip', self.vk_album_dir)

