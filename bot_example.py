import telebot
import telebot.apihelper

api_token = '<TOKEN>'


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
