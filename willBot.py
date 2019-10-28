import os
import pickle

import telebot
import telebot.apihelper
from telebot import types

from helpers import log, PollStat, RejectProtector, TimeProtector
from property import *

bot = telebot.TeleBot(PRP.BOT_TOKEN, threaded=False)

TRACKED_POLLS = {}
MULTI_POLLS_PROTECTION = {}

LAST_WILL_USED_USERS = set()

if os.path.isfile(LAST_WILL_USERS_FILE):
    with open(LAST_WILL_USERS_FILE, 'rb') as handle:
        LAST_WILL_USED_USERS = pickle.load(handle)


def add_last_will_user(user_id):
    LAST_WILL_USED_USERS.add(user_id)
    with open(LAST_WILL_USERS_FILE, 'ab') as handle:
        pickle.dump(LAST_WILL_USED_USERS, handle, protocol=pickle.HIGHEST_PROTOCOL)


def in_private(message):
    return message.chat.id == message.from_user.id


def is_member(chat_id: str, user_id: str):
    try:
        ans = telebot.apihelper.get_chat_member(PRP.BOT_TOKEN, chat_id, user_id)
        status = ans['status']
        return status != 'left' and status != 'kicked'
    except Exception as exp:
        log("Not a member tries to access bot", user_id, exp)
        log(chat_id, user_id)
    return False


def send_stiker(chat_id, stiker_name):
    sti = open(f"stikers/{stiker_name}.webp", 'rb')
    return bot.send_sticker(chat_id, sti)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if in_private(message):
        send_stiker(message.chat.id, "ready_to_work")
        bot.reply_to(message,
                     "Готов к работе.\n"
                     "Напиши сообщение с тегом #aloud_in_private "
                     "в самом начале, и я отправлю его в студенческий чат для голосования."
                     )
        bot.send_message(
            message.chat.id,
            "<b>Помни:</b>\n"
            f"{EMOJI.POINT_RIGHT} Любому студенту положен 1 пост в день.\n"
            f"{EMOJI.POINT_RIGHT} Если многие поставят тебе {EMOJI.REJECT} ты не сможешь постить своё "
            "мнение очень и очень долго.\n\n"
            "Если тебе охота сказать последнее слово используй #last_will\n"
            "(его говорят только однажды и сразу в общий чат).",
            parse_mode="HTML"
        )


@bot.message_handler(regexp='^#last_will\s(\w|\W)*')
def last_will(message):
    if not in_private(message):
        bot.reply_to(message, "Эй, такое только в личку!")
        return

    user_id = message.from_user.id

    if not is_member(PRP.STUDENT_CHAT_ID, user_id):
        return

    if user_id in LAST_WILL_USED_USERS:
        send_stiker(message.chat.id, "no_last_will_left")
        bot.reply_to(message, "Последняя воля уже использована!")
    else:
        add_last_will_user(user_id)
        send_stiker(message.chat.id, "last_will_acceptance")
        bot.reply_to(message, "Быть может жаль. Ваше обращение принято.")

        text = message.html_text[len('#last_will '):]
        send_stiker(PRP.COMMON_CHAT, "last_will")
        bot.send_message(PRP.COMMON_CHAT, "<b>ПОСЛЕДНЯЯ ВОЛЯ: </b>\n" + text, parse_mode="HTML")


# TODO decorator
@bot.message_handler(regexp='^#aloud_in_private\s(\w|\W)*')
def publish_claim(message):
    user_id = message.from_user.id

    # protection from bad users
    if user_id not in MULTI_POLLS_PROTECTION:
        MULTI_POLLS_PROTECTION[user_id] = (TimeProtector(), RejectProtector())
    else:
        time_protector: TimeProtector = MULTI_POLLS_PROTECTION[user_id][0]
        reject_protector: TimeProtector = MULTI_POLLS_PROTECTION[user_id][1]
        if not time_protector.can_post():
            send_stiker(message.chat.id, "khkh")
            bot.reply_to(message,
                         "Жди день перед тем как можно будет отправить ещё.")
            return
        if not reject_protector.can_post():
            send_stiker(message.chat.id, "khkh")
            bot.reply_to(
                message,
                "Ты часто пишешь неправильные вещи. В этот раз ты сам по себе."
            )
            return
        time_protector.refresh_time()

    if in_private(message) and is_member(PRP.STUDENT_CHAT_ID, user_id):
        text = message.html_text[len('#aloud_in_private'):]
        send_stiker(message.chat.id, "claim_accepted")
        bot.reply_to(message, "Ваше обращение принято.")
        publish_claim_to_chat(text)
    else:
        bot.reply_to(message, "Эй, такое только в личку!")


def handle_poll(message, message_id) -> bool:
    stat: PollStat = TRACKED_POLLS[message_id]
    likes, dislikes, rejects = stat

    should_delete = len(rejects) >= DELETE_MESSAGE_COUNT
    should_publish = False

    if not should_delete and \
            len(likes) + len(dislikes) + len(rejects) >= PUBLISH_MESSAGE_COUNT:
        should_publish = len(likes) > (len(dislikes) + len(rejects))
        should_delete = len(likes) * 1.2 <= (len(dislikes) + len(rejects))

    if len(likes) + len(dislikes) + len(rejects) >= 30:
        should_delete = True

    if should_publish:
        should_delete = True
        text = message.message.html_text
        send_stiker(PRP.COMMON_CHAT, "common_chat_publish")
        bot.send_message(PRP.COMMON_CHAT, "<b>Люди выразили своё мнение:</b> \n" + text, parse_mode="HTML")

    if should_delete:
        bot.delete_message(PRP.STUDENT_CHAT_ID, message_id)
        bot.delete_message(PRP.STUDENT_CHAT_ID, stat.stiker_id)
        del TRACKED_POLLS[message_id]
    return should_delete


def publish_claim_to_chat(text):
    sti_msg = send_stiker(PRP.STUDENT_CHAT_ID, "cries")

    btn_my_site = types.InlineKeyboardButton(f"{EMOJI.THUMBS_UP} 0", callback_data="LIKE")
    btn_my_site1 = types.InlineKeyboardButton(f"{EMOJI.THUMBS_DOWN} 0", callback_data="DISLIKE")
    btn_my_site2 = types.InlineKeyboardButton(f"{EMOJI.REJECT} 0", callback_data="REJECT")

    markup = types.InlineKeyboardMarkup().row(btn_my_site, btn_my_site1, btn_my_site2)
    message = bot.send_message(PRP.STUDENT_CHAT_ID, text, reply_markup=markup)
    TRACKED_POLLS[message.message_id] = PollStat(stiker_id=sti_msg.message_id)


@bot.callback_query_handler(func=lambda call: True)
def poll_vote_update(call):
    message_id = call.message.message_id

    if message_id not in TRACKED_POLLS:
        return

    user_id = call.from_user.id

    type_of_query = call.data

    stat: PollStat = TRACKED_POLLS[message_id]
    stat.remove_vote(user_id)

    if type_of_query == "LIKE":
        stat.add_like(user_id)
    elif type_of_query == "DISLIKE":
        stat.add_dislike(user_id)
    elif type_of_query == 'REJECT':
        stat.add_reject(user_id)

    if handle_poll(call, message_id):  # poll deleted
        return

    btn_my_site = types.InlineKeyboardButton(f"{EMOJI.THUMBS_UP} {len(stat.likes)}", callback_data="LIKE")
    btn_my_site1 = types.InlineKeyboardButton(f"{EMOJI.THUMBS_DOWN} {len(stat.dislikes)}", callback_data="DISLIKE")
    btn_my_site2 = types.InlineKeyboardButton(f"{EMOJI.REJECT} {len(stat.rejects)}", callback_data="REJECT")

    markup = types.InlineKeyboardMarkup().row(btn_my_site, btn_my_site1, btn_my_site2)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=message_id, reply_markup=markup)
    # log(f"Callback : {call}")


bot.polling(none_stop=True, interval=0)
