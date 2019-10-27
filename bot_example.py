
import telebot
import telebot.apihelper
from telebot import types

api_token = '<TOKEN>'
bot = telebot.TeleBot('Token')


def is_member(char_id: str, user_id: str):
    try:
        ans = telebot.apihelper.get_chat_member(api_token, char_id, user_id)
        status = ans['status']
        return status != 'left' and status != 'kicked'
    except Exception as exp:
        # TODO логгировать юзера
        print(exp)
        print(char_id, user_id)
        return False

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


count = 0
last_message_id = 0

@bot.message_handler(commands=['SECRETS'])
def url(message):
    global count
    markup = types.InlineKeyboardMarkup()
    btn_my_site = types.InlineKeyboardButton(f"спасите! {count}", callback_data="LIKE")
    btn_my_site1 = types.InlineKeyboardButton("я нажалуюсь", callback_data="HATE")
    markup.add(btn_my_site)
    markup.add(btn_my_site1)
    print(message.chat.id)
    global last_message_id
    last_message_id = message.message_id
    bot.send_message(message.chat.id, "kILL THEM!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    markup = types.InlineKeyboardMarkup()
    global count;
    global last_message_id;
    count += 1;
    btn_my_site = types.InlineKeyboardButton(f"спасите! {count}", callback_data="LIKE")
    btn_my_site1 = types.InlineKeyboardButton("я нажалуюсь", callback_data="HATE")
    markup.add(btn_my_site)
    markup.add(btn_my_site1)
    print(call)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=last_message_id, reply_markup=markup)


@bot.message_handler(commands=['LIKE'])
def url1(message):
    print("1")


bot.polling(none_stop=True, interval=0)
