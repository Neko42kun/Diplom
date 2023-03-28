from random import randrange, randint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from database import create_db, create_tables, insert_users, check_users
from get_info import get_user_info, get_photos, get_age, find_users


with open('token.txt', 'r') as file:
    token = file.readline()
with open('user_token.txt', 'r') as file:
    user_token = file.readline()

vk = vk_api.VkApi(token=token)
vk2 = vk_api.VkApi(token=user_token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


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
