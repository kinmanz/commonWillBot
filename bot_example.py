
import telebot

bot = telebot.TeleBot('token')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

bot.polling(none_stop=True, interval=0)