import base64
import time
import requests


def encode_image(image_dir):
    with open(image_dir, mode='rb') as image:
        image_code = image.read()

    return base64.encodebytes(image_code).decode('utf-8')


image = encode_image('kek.jpg')

start_time = time.time()

print(start_time)

data = {
    'group_link': 'https://vk.com/yantarn1y',
    'image_file': image,
    'first_date': int(time.time() - 1000000),
    'second_date': int(time.time()) 
}

r = requests.post("http://127.0.0.1:5000/api/new_request", json=data)

data = r.json()

print('user_id:', data)

time.sleep(3)

for i in range(50):
    r = requests.post("http://127.0.0.1:5000/api/get_status", json=data)
    print(r.json())

    if not 'status' in r.json():
        break

    time.sleep(60)

data = r.json()

# r = requests.post("http://127.0.0.1:5000/api/get_archive", json=data)

# print(r.json())

# print(time.time() - start_time)
#456248523 
# # считывание нескольких строк в массив из файла
# with open('24.txt', 'r') as file:
#     f = file.read()
#     f = f.split()
