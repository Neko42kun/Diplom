from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll
import datetime


with open('token.txt', 'r') as file:
    token = file.readline()
with open('user_token.txt', 'r') as file:
    user_token = file.readline()

vk = vk_api.VkApi(token=token)
vk2 = vk_api.VkApi(token=user_token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


def get_user_info(user_id):
    user_info = {}
    response = vk.method('users.get', {'user_id': user_id,
                                       'v': 5.131,
                                       'fields': 'first_name, last_name, sex, city, bdate'})
    if response:
        for key, value in response[0].items():
            if key == 'city':
                user_info[key] = value['id']
            else:
                user_info[key] = value
    else:
        write_msg(user_id, 'Ошибка')
        return False
    return user_info


def get_age(date):
    return datetime.datetime.now().year - int(date[-4:])


def find_users(user_info):
    response = vk2.method('users.search', {
        'age_from': user_info['age'] - 3,
        'age_to': user_info['age'] + 3,
        'sex': 3 - user_info['sex'],
        'city': user_info['city'],
        'status': 6,
        'has_photo': 1,
        'count': 1000,
        'fields': 'photo_400_orig',
        'v': 5.131})
    if response:
        if response.get('items'):
            return response.get('items')
        write_msg(user_info['id'], 'Ошибка')
        return False


def get_photos(user_id):
    try:
        response = vk2.method('photos.get', {'owner_id': user_id,
                                             'album_id': 'profile',
                                             'extended': '1',
                                             'v': '5.131'})
        if response.get('count'):
            if response.get('count') < 3:
                return False
            top_photos = sorted(response.get('items'), key=lambda x: x['likes']['count']
                                + x['comments']['count'], reverse=True)[:3]
            photo_data = {'user_id': top_photos[0]['owner_id'], 'photo_ids': []}
            for photo in top_photos:
                photo_data['photo_ids'].append(photo['id'])
            return photo_data
        return False
    except vk_api.exceptions.ApiError as error:
        return False