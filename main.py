from random import randrange, randint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
from database import create_db, create_tables, insert_users, check_users


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


def get_add_info(user_id, user_info):
    bdate = user_info.setdefault('bdate', 'r')
    if len(bdate.split('.')) != 3:
        write_msg(user_id, "Введите дату рождения в формате ДД.ММ.ГГГГ")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    user_info['bdate'] = event.text
            if len(user_info['bdate'].split('.')) == 3:
                break

    city = user_info.setdefault('city', 'r')
    if type(city) != type(1):
        write_msg(user_id, "Введите название своего города")
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    city = event.text
                    values = {
                        'country_id': 1,
                        'q': city,
                        'count': 1
                    }
                    response = vk2.method('database.getCities', values=values)
                    if response['items']:
                        user_info['city'] = response['items'][0]['id']
            if type(user_info['city']) == type(1):
                break
    user_info['age'] = get_age(user_info['bdate'])
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


def search_output(user_id, found_users):
    random_id = randint(0, len(found_users) - 1)
    while check_users(found_users[random_id]['id']) == False:
        found_users.pop(random_id)
        random_id = randint(0, len(found_users) - 1)
    insert_users(found_users[random_id]['id'])
    user_photos = get_photos(found_users[random_id]['id'])
    if user_photos != False:
        write_msg(user_id, f"vk.com/id{found_users[random_id]['id']}")
        for k in range(3):
            write_msg(user_id, f"vk.com/photo{user_photos['user_id']}_{user_photos['photo_ids'][k]}")
        write_msg(event.user_id, "Для поиска следующего партнёра введите далее")
    else:
        found_users.pop(random_id)
    return found_users


def continue_searching(user_id, found_users):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text
                if request == "далее" or request == "Далее":
                    search_output(user_id, found_users)



create_db()
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text
            create_tables()

            if request == "привет" or request == "Привет":
                user_info = get_user_info(event.user_id)
                get_add_info(event.user_id, user_info)
                found_users = find_users(user_info)
                found_users = search_output(event.user_id, found_users)
                continue_searching(event.user_id, found_users)

            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Что бы начать напишите привет")
