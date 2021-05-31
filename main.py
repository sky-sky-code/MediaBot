import requests
import telebot
from instabot import Bot
import os
from config.conf import *

try:
    if os.path.abspath('config/clas.ssp_uuid_and_cookie.json'):
        file_json = os.path.abspath('config/clas.ssp_uuid_and_cookie.json')
        os.remove(file_json)
except Exception as exc:
    print(exc)

bot = Bot()
bot.login(username=USERNAME, password=PASSWORD)
tbot = telebot.TeleBot(TOKEN)

@tbot.message_handler(commands=['wp', 'wv']) # w - Write
def check_and_write(message):
    check_dirs()
    tbot.send_message(message.chat.id, 'Введите аккаунт')
    if message.text == '/wp':
        tbot.register_next_step_handler(message, write_photo)
    else:
        tbot.register_next_step_handler(message, write_video)


@tbot.message_handler(commands=['photo', 'video'])
def get_media(message):
    text = message.text
    path = text.split('/')
    for root, dirs, files in os.walk(path[1]):
        for file in files:
            if path[1] == 'photo':
                with open(f'{path[1]}/{file}', 'rb') as obj:
                    tbot.send_photo(message.chat.id, obj)
            else:
                with open(f'{path[1]}/{file}', 'rb') as obj:
                    tbot.send_video(message.chat.id, obj)


@tbot.message_handler(content_types=['text'])
def write_media_for_url(message):
    check_dirs()
    url = message.text
    try:
        os.mkdir('photo')
    except FileExistsError as exc:
        print(exc)
    chose_media = bot.get_media_id_from_link(url)
    download_photo(chose_media, "photo/img_")
    tbot.send_message(message.chat.id, 'загрузка завершена')


def write_photo(message):
    acc = message.text
    try:
        os.mkdir('photo')
    except FileExistsError as exc:
        print(exc)
    twony_last_medias = bot.get_user_medias(acc, filtration=None)
    for e, media_id in enumerate(twony_last_medias):
        download_photo(media_id, "photo/img_" + str(e))
    tbot.send_message(message.chat.id, 'загрузка завершена')

def write_video(message):
    acc = message.text
    try:
        os.mkdir('video')
    except FileExistsError as exc:
        print(exc)
    twony_last_medias = bot.get_user_medias(acc, filtration=None)
    for e, media_id in enumerate(twony_last_medias):
        download_video(media_id, "video/vd_" + str(e))
    tbot.send_message(message.chat.id, 'загрузка завершена')

def check_dirs():
    for root, dirs, files in os.walk('photo'):
        for file in files:
            os.remove(f'photo/{file}')
    for root, dirs, files in os.walk('video'):
        for file in files:
            os.remove(f'video/{file}')


def download_photo(media_id, filename):
    media = bot.get_media_info(media_id)[0]
    if 'image_versions2' in media.keys() and 'video_versions' not in media.keys():
        url = media['image_versions2']['candidates'][0]['url']
        response = requests.get(url)
        with open(filename + ".jpg", "wb") as f:
            response.raw.decode_content = True
            f.write(response.content)
    if "carousel_media" in media.keys():
        for e, element in enumerate(media["carousel_media"]):
            url = element['image_versions2']["candidates"][0]["url"]
            response = requests.get(url)
            with open(filename + str(e) + ".jpg", "wb") as f:
                response.raw.decode_content = True
                f.write(response.content)

def download_video(media_id, filename):
    media = bot.get_media_info(media_id)[0]
    if 'video_versions' in media.keys():
        url = media['video_versions'][0]['url']
        response = requests.get(url)
        with open(filename + '.mp4', 'wb') as f:
            response.raw.decode_content = True
            f.write(response.content)


tbot.polling()