import json

import requests
from django.conf import settings

KEYBOARD_GENDER = [
    ['M', 'W']
]

KEYBOARD_GAMETYPES = [['suggestion'],
                      ['self-monitoring'],
                      ['comparison'],
                      ['competition']]


def send_message(text, user_id, close_keyboard=False):
    reply_markup = {
        "hide_keyboard": close_keyboard
    }
    reply_markup = json.dumps(reply_markup)
    requests.post(settings.TELEGRAM_BOT_URL + "sendMessage", params={"chat_id": user_id,
                                                                     "text": text,
                                                                     "reply_markup": reply_markup})


def send_photo(files, user_id):
    requests.post(settings.TELEGRAM_BOT_URL + "sendPhoto", files=files,
                  params={"chat_id": user_id})


def send_message_reply(text, user_id):
    reply_markup = {
        'keyboard': [['1'], ['2']],
        'resize_keyboard': True,
        'one_time_keyboard': True
    }
    reply_markup = json.dumps(reply_markup)
    requests.post(settings.TELEGRAM_BOT_URL + "sendMessage", params={
        "chat_id": user_id,
        "text": text,
        "reply_markup": reply_markup
    })


def send_gametype_selection(user_id, message):
    reply_markup = {'keyboard': KEYBOARD_GAMETYPES,
                    'resize_keyboard': True,
                    'one_time_keyboard': True}
    reply_markup = json.dumps(reply_markup)
    requests.post(settings.TELEGRAM_BOT_URL + "sendMessage", params={
        "chat_id": user_id,
        "text": message,
        "reply_markup": reply_markup
    })


def send_height_selection(user_id, message):
    reply_markup = {
        "hide_keyboard": True
    }
    reply_markup = json.dumps(reply_markup)
    requests.post(settings.TELEGRAM_BOT_URL + "sendMessage", params={
        "chat_id": user_id,
        "text": message,
        "reply_markup": reply_markup
    })


def send_weight_selection(user_id, message):
    reply_markup = {
        "hide_keyboard": True
    }
    reply_markup = json.dumps(reply_markup)
    requests.post(settings.TELEGRAM_BOT_URL + "sendMessage", params={
        "chat_id": user_id,
        "text": message,
        "reply_markup": reply_markup
    })


def send_gender_selection(user_id, message):
    reply_markup = {
        'keyboard': KEYBOARD_GENDER,
        'resize_keyboard': True
    }
    reply_markup = json.dumps(reply_markup)
    requests.post(settings.TELEGRAM_BOT_URL + "sendMessage", params={
        "chat_id": user_id,
        "text": message,
        "reply_markup": reply_markup
    })


def get_updates():
    get_request = requests.get(settings.TELEGRAM_BOT_URL + "getUpdates")
    data = get_request.json()

    return data
