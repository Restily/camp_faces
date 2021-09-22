from collections import deque

import requests

from config import *


class VkApi():

    def __init__(self, first_date, second_date, user_id):
        self.first_date = first_date
        self.second_date = second_date
        self.user_id = user_id

        self.group_id = 0
        self.urls = deque()
    

    def vk_api_request(self, method, params):
        """ 
        -> method: метод запроса
        -> params: параметры запроса
        <- response: словарь с инфорамацией о группе
        """
        params_req = ''

        for key, param_key in params.items():
            params_req += f'{key}={param_key}&'

        response = requests.post(f"https://api.vk.com/method/{method}?{params_req}v={VK_VERSION}&access_token={VK_API_SERVICE_KEY}")

        return response.json()


    def get_group_albums(self, vk_group_id):
        """
        Документация: https://vk.com/dev/photos.getAlbums
        """
        method = 'photos.getAlbums'
        params = {
            'owner_id': vk_group_id
        }

        return self.vk_api_request(method, params)


    def get_group_photos(self, vk_group_id, offset=0):
        """
        Документация: https://vk.com/dev/photos.getAll
        """
        method = 'photos.getAll'
        params = {
            'owner_id': vk_group_id,
            'count': 200,
            'offset': offset,
            'no_service_albums': 1,
        }

        return self.vk_api_request(method, params)


    def get_vk_group_info(self, vk_group):
        """ 
        Документация: vk.com/dev/groups.getById
        """
        method = 'groups.getById'
        params = {
            'group_ids': vk_group
        }

        return self.vk_api_request(method, params)


    def get_vk_album_photos(self, group_id, album_id):
        method = 'photos.get'
        params = {
            'owner_id': group_id,
            'album_id': album_id,
            'rev': 1
        }

        return self.vk_api_request(method, params)


    def check_date(self, photo_date):
        """ Проверка, что фотография нормальная """
        if photo_date <= self.second_date:
            if photo_date >= self.first_date:
                return 1
            else:
                return 0

        return 2


    def download_photos(self, photos):
        """ Скачивание фотографий """
        for photo in photos:

            if len(self.urls) == 100:
                return 0

            photo_date = photo['date']

            check = self.check_date(photo_date)

            if check == 1:
                if photo['sizes'][-3]['type'] == 'x':
                    self.urls.append(photo['sizes'][-3]['url'])
                elif photo['sizes'][2]['type'] == 'x':
                    self.urls.append(photo['sizes'][2]['url'])
                else:
                    self.urls.append(photo['sizes'][-1]['url'])

            elif not check:
                return 0
        
        return 1


    def check_vk_link(self, group_link):
        """ 
        Проверка ссылки на валидность;
        Если ссылка не валидна, вызывается ошибка 
        """
        vk_group = group_link.split('/')[-1]

        vk_group_info = self.get_vk_group_info(vk_group)   

        # print(vk_group_info)

        request_status = next(iter(vk_group_info))

        if request_status == 'error':
            return 'not found'
        
        if vk_group_info['response'][0]['is_closed'] == 1:
            return 'closed'
        
        self.vk_group_id = f"-{vk_group_info['response'][0]['id']}"

        albums = self.get_group_albums(self.vk_group_id)

        if next(iter(albums)) == 'error':
            return 'closed'

        return 'start running task'


    def get_albums_photos(self):
        """ Получеие фотографий сообщества """
        photos = self.get_group_photos(self.vk_group_id)['response']

        photos_count = photos['count']

        download = self.download_photos(photos['items'])

        if download:
            for offset in range(200, photos_count, 200):
                photos = self.get_group_photos(self.vk_group_id, offset)['response']

                download = self.download_photos(photos['items'])

                if not download:
                    break

        # albums = self.get_group_albums(self.vk_group_id)['response']

        # for album in albums['items']:
        #     album_id = album['id']

        #     photos = self.get_vk_album_photos(self.vk_group_id, album_id)

        #     self.download_photos(photos['response']['items'])

        wall_photos = self.get_vk_album_photos(self.vk_group_id, 'wall')

        self.download_photos(wall_photos['response']['items'])

        return self.urls
