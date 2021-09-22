import os
import threading
from zipfile import ZipFile

from flask import Flask, json, request, redirect, send_from_directory, jsonify
from flask_cors import CORS
import requests
from werkzeug.wrappers import Response

from utils import *
from config import *
from dirs import *
from vk_api import VkApi


app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={
    r'/*': {
        'origins': '*'
        # 'origins': ALLOWED_ORIGINS
    }
})

app.config['SECRET_KEY'] = APP_SECRET_KEY
app.config['threaded'] = True


@app.route('/')
def index():
    return redirect('http://www.google.com')


@app.route('/api/new_request', methods=['POST'])
def new_face_request():
    """
    Создание нового запроса 

    POST-запрос по запросу /api/new_request 

    -> group_link: str - ссылка на группу вк
    -> image_file: base64 - фотография человека 
    -> first_date: int - крайняя слева дата
    -> second_date: int - крайняя справа дата

    <- {"error": "vk group not found"} - неверный URL
    <- {"error": vk group closed} - группа закрыта
    <- {"user_id": int} - id юзера в случае успешного старта
    """
    data = request.get_json()

    image_json = data['image_file'] # получение фотографии пользователя
    group_link = data['group_link'] # получение ссылки на альбом
    first_date = data['first_date'] # получение даты
    second_date = data['second_date'] # получение даты

    user_id = generate_user_id()

    man_dir = create_dirs(user_id)  # создание директории пользователя 

    man_image = save_image(image_json, 'man.jpg', man_dir)
    
    vk = VkApi(first_date, second_date, user_id)

    check_link_status = vk.check_vk_link(group_link)

    if check_link_status == 'not found':
        return jsonify({"error": "vk group not found"})
    
    elif check_link_status == 'closed':
        return jsonify({"error": "vk group closed"})
    
    elif check_link_status == 'start running task':
        thread_task = threading.Thread(target=start_running_task, args=(vk, user_id))
        thread_task.start()

    return jsonify({'user_id': user_id})


@app.route('/api/get_status', methods=['POST'])
def get_status():
    """
    Возвращает статус глобального запроса
    
    POST-запрос по запросу /api/get_status 

    -> user_id: int - id юзера

    <- {"status":"not yet"} - запрос не выполнен до конца
    <- {image_name: url} - если запрос выполнился, возвращается словарь 
    в виде "имя фотографии": ссылка (имя фотографии не играет роли)
    <- {"error": "photos not found"} - фотографии не найдены
    """
    data = request.get_json()

    folder_path = f'{UPLOAD_DIR}/{data["user_id"]}'
    data_path = f'{folder_path}/{DATA_FILENAME}'

    if os.path.exists(data_path):
        with open(data_path) as json_file:
            response = json.load(json_file)
        
        os.remove(data_path)

        if len(os.listdir(folder_path)) == 0:
            os.rmdir(folder_path)

        if len(response) == 0:
            return jsonify({"error": "photos not found"})

        return jsonify(response)

    return jsonify({"status":"not yet"})


@app.route('/api/get_photo', methods=['POST'])
def get_photo():
    """
    Получение base64 изображения

    POST-запрос по запросу /api/get_photo 
    
    -> image_name: str - имя файла  
    -> user_id: str = id юзера 
    
    <- {"error": "image not found"} - фотография не найдена
    <- {"image_name": base64} - фотография в формате base64
    """
    data = request.get_json()

    image_name = data['image_name'] # получение фотографии пользователя
    user_id = data['user_id'] # получение ссылки на альбом
    
    image_path = f'{UPLOAD_DIR}/{user_id}/{VK_PHOTO_DIR}/{image_name}'

    if not os.path.exists(image_path):
        return jsonify({"error": "image not found"})

    return jsonify({image_name: encode_image(image_path)})


@app.route('/api/get_archive', methods=['POST'])
def get_archive():
    """
    Создание архива

    POST-запрос по запросу /api/get_archive

    -> images: [urls] - фотографии
    
    <- {"donwload_url": str} - ссылка для скачивания
    """
    data = request.get_json()

    images = data['images'] # получение фотографии пользователя
    
    user_id = generate_user_id()
    os.mkdir(f'{UPLOAD_DIR}/{user_id}')

    archive_path = f'{UPLOAD_DIR}/{user_id}/{ARCHIVE_NAME}'

    if os.path.exists(ARCHIVE_NAME):
        os.remove(archive_path)

    with ZipFile(archive_path, 'w') as user_archive:
        for ind, image_url in enumerate(images):
            image_req = requests.get(image_url, allow_redirects=True)

            # image_dir = f"{UPLOAD_DIR}/{user_id}/{ind}.jpg"

            # with open(image_dir, mode='wb') as image:
            #     image.write(image_req.content) 

            user_archive.writestr(f'{ind + 1}.jpg', image_req.content)

            # os.remove(image_dir)

        user_archive.close()

    return jsonify({'download_url': f'/download_archive/{user_id}'})


@app.route('/download_archive/<user_id>')
def download_archive(user_id):
    """
    Получение фотографий по ссылке /download_archive/<user_id> 
    """
    check_date_archives()

    if not os.path.exists(f'{UPLOAD_DIR}/{user_id}/{ARCHIVE_NAME}'):
        return Response(status=405)

    return send_from_directory(f'{UPLOAD_DIR}/{user_id}', ARCHIVE_NAME, as_attachment=True)


if __name__ == "__main__":
   app.run(debug=False)


# for image_name in os.listdir(f'{UPLOAD_DIR}/1/{VK_PHOTO_DIR}'):
#     with open(f'{UPLOAD_DIR}/1/{VK_PHOTO_DIR}/{image_name}', mode='rb') as image:
#         img = image.read()
    
#     response['images'][image_name] = base64.encodebytes(img).decode('utf-8')

# return jsonify(response)


# @app.route('/photos/<request_id>/download/<filename>', methods=['GET', 'POST'])
# def download_photo(request_id, filename):
#     """ Скачивание фото """
#     return send_from_directory(f'{UPLOAD_DIR}/{request_id}/{VK_PHOTO_DIR}', filename, as_attachment=True)


# @app.route('/photos/<request_id>/download_archive')
# def download_archive(request_id):
#     """ Скачивание архива с фотографиями """
#     archive_dir = photos_to_archive(f'{os.getcwd()}/{UPLOAD_DIR}/{request_id}')

#     return jsonify(archive_dir=archive_dir, archive_name='findmychild.zip')


# @app.route('/api/<user_id>/get_photo/<image_name>')
# def get_photo(image_name, user_id):
#     """
#     Запрос фотографии \n
#     GET-запрос по запросу /api/<user_id>/get_photos/<image_name> \n
#     <- {"error": "image not found"}, фотография не найдена \n
#     <- {"image_name": str, "user_id": str} - успешное выполнение
#     """
#     return jsonify({image_name: encode_image(user_id, image_name)})


# @app.route('/photos/<request_id>', methods = ['GET'])
# def get_images(request_id):
#     """ Получение списка фотографий """
#     image_names = os.listdir(f'{UPLOAD_DIR}/{request_id}/{VK_PHOTO_DIR}') # список фотографий из директории пользователя
    
#     return render_template("photos.html", image_names=image_names, request_id=request_id)


