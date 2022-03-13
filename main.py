import requests
import telebot
from instabot import Bot
import os
from fake_headers import Headers

try:
    if os.path.abspath(f'config/{os.environ.get("USERNAME")}_uuid_and_cookie.json'):
        file_json = os.path.abspath(f'config/{os.environ.get("USERNAME")}_uuid_and_cookie.json')
        os.remove(file_json)
except Exception as exc:
    print(exc)

bot = Bot()
bot.login(username=os.environ.get('USERNAME'), password=os.environ.get('PASSWORD'))
tbot = telebot.TeleBot(os.environ.get('TOKEN'))
header = Headers(browser="chrome", os='win', headers=True)


@tbot.message_handler(commands=['photo', 'video'])
def photo_and_video(message):
    tbot.send_message(message.chat.id, 'Введите аккаунт')
    if message.text == '/photo':
        tbot.register_next_step_handler(message, get_all_photo)
    else:
        tbot.register_next_step_handler(message, get_all_video)


def get_all_photo(message):
    acc = message.text
    try:
        os.mkdir('video')
    except FileExistsError as exc:
        print(exc)
    all_medias = bot.get_total_user_medias(acc)
    for e, media_id in enumerate(all_medias):
        media = bot.get_media_info(media_id)[0]
        if 'image_versions2' in media.keys() and 'video_versions' not in media.keys():
            url = media['image_versions2']['candidates'][0]['url']
            response = requests.get(url, headers=header.generate())
            tbot.send_photo(message.chat.id, response.content)
        if "carousel_media" in media.keys():
            for e, element in enumerate(media["carousel_media"]):
                url = element['image_versions2']["candidates"][0]["url"]
                response = requests.get(url, headers=header.generate())
                tbot.send_photo(message.chat.id, response.content)
    tbot.send_message(message.chat.id, 'загрузка завершена')


def get_all_video(message):
    acc = message.text
    all_medias = bot.get_total_user_medias(acc, )
    for e, media_id in enumerate(all_medias):
        media = bot.get_media_info(media_id)[0]
        if 'video_versions' in media.keys():
            url = media['video_versions'][0]['url']
            response = requests.get(url, headers=header.generate())
            tbot.send_video(message.chat.id, response.content)

tbot.polling()