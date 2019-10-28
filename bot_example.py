import telebot.apihelper
from property import PRP
from property import EMOJI
from telebot import types
import time
bot = telebot.TeleBot(PRP.BOT_TOKEN, threaded=False)

polling_status = {}


def in_private(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    return chat_id == user_id


def is_member(chat_id: str, user_id: str):
    try:
        ans = telebot.apihelper.get_chat_member(PRP.BOT_TOKEN, chat_id, user_id)
        status = ans['status']
        return status != 'left' and status != 'kicked'
    except Exception as exp:
        # TODO логгировать юзера
        print(exp)
        print(chat_id, user_id)
        return False


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

# TODO decorator
@bot.message_handler(regexp='^#aloud_in_private\s(\w|\W)*')
def aloud_in_private(message):
    user_id = message.from_user.id
    if in_private(message) and is_member(PRP.STUDENT_CHAT_ID, user_id):
        text = message.html_text[len('#aloud_in_private'):]
        bot.reply_to(message, "Твоё обращение принято")
        publish_claim_to_chat(text)
    else:
        bot.reply_to(message, "Эй, такое только в личку!")


def publish_claim_to_chat(text):
    markup = types.InlineKeyboardMarkup()
    btn_my_site = types.InlineKeyboardButton(EMOJI.THUMBS_UP + " 0", callback_data="LIKE")
    btn_my_site1 = types.InlineKeyboardButton(EMOJI.THUMBS_DOWN + " 0", callback_data="HATE")
    btn_my_site2 = types.InlineKeyboardButton(EMOJI.EYE + " 0", callback_data="NOT_KNOW")

    markup.add(btn_my_site)
    markup.add(btn_my_site1)
    markup.add(btn_my_site2)
    message = bot.send_message(PRP.STUDENT_CHAT_ID, text, reply_markup=markup)
    polling_status[message.message_id] = [set(),set(),set()]


@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    markup = types.InlineKeyboardMarkup()
    message_id = call.message.message_id
    user_id = call.from_user.id
    type_of_query = call.data
    if message_id not in polling_status:
        return

    stat = polling_status[message_id]

    if type_of_query == "LIKE":
        if user_id not in stat[0]:
            stat[0].add(user_id)
        else:
            stat[0].remove(user_id)
        stat[1].discard(user_id)
        stat[2].discard(user_id)
    elif type_of_query == "HATE":
        if user_id not in stat[1]:
            stat[1].add(user_id)
        else:
            stat[1].remove(user_id)
        stat[0].discard(user_id)
        stat[2].discard(user_id)
    elif type_of_query == 'NOT_KNOW':
        if user_id not in stat[2]:
            stat[2].add(user_id)
        else:
            stat[2].remove(user_id)
        stat[0].discard(user_id)
        stat[1].discard(user_id)
    else:
        return;

    btn_my_site = types.InlineKeyboardButton(f"{EMOJI.THUMBS_UP} {len(stat[0])}", callback_data="LIKE")
    btn_my_site1 = types.InlineKeyboardButton(f"{EMOJI.THUMBS_DOWN} {len(stat[1])}", callback_data="HATE")
    btn_my_site2 = types.InlineKeyboardButton(f"{EMOJI.EYE} {len(stat[2])}", callback_data="NOT_KNOW")
    markup.add(btn_my_site)
    markup.add(btn_my_site1)
    markup.add(btn_my_site2)
    print(call)

    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id, reply_markup=markup)


@bot.message_handler(commands=['LIKE'])
def url1(message):
    print("1")


bot.polling(none_stop=True, interval=0)
