import telebot
import traceback
import json
import requests

TOKEN = "6055623531:AAEe1y73lp15xnjZGu3r7jTMgStHYKwhUTw"
API_KEY = "806829e610173c4cf71e00a3"
bot = telebot.TeleBot(TOKEN)

keys = {
    'доллар': 'USD',
    'евро': 'EUR',
    'рубль': 'RUB',
}

class APIException(Exception):
    pass


class Converter:
    @staticmethod
    def get_price(base, sym, amount):
        try:
            base_key = keys[base.lower()]
        except KeyError:
            raise APIException(f"Валюта {base} не найдена!")

        try:
            sym_key = keys[sym.lower()]
        except KeyError:
            raise APIException(f"Валюта {sym} не найдена!")

        if base_key == sym_key:
            raise APIException(f'Невозможно перевести одинаковые валюты {base}!')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}!')

        r = requests.get(f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_key}")
        if r.status_code != 200:
            raise APIException("Не удалось получить данные о валюте")

        resp = json.loads(r.content)
        new_price = resp['conversion_rates'][sym_key] * amount
        new_price = round(new_price, 3)
        message = f"Цена {amount} {base} в {sym} : {new_price}"
        return message

@bot.message_handler(commands=['start', 'help'])
def send_welcomehelp(message):
    bot.send_message(message.chat.id, f"Рад видеть тебя, {message.chat.username}, чтобы начать работу, "
                                      f"введите команду боту в следующем формате: \n<имя валюты> \<в какую валюту "
                                      f"перевести> \<количество переводимой валюты> \n Увидеть список всех доступных "
                                      f"валют /values")
    bot.send_message(message.chat.id, message)

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = '\n'.join((text, key))
    bot.reply_to(message, text)

@bot.message_handler(content_types=['text', ])
def converter(message: telebot.types.Message):
    try:
        base, sym, amount = message.text.split(' ')
    except ValueError as e:
        bot.reply_to(message, 'Неверное количество параметров!')
    try:
        new_price = Converter.get_price(base, sym, amount)
        bot.reply_to(message, new_price)
    except APIException as e:
        bot.reply_to(message, f'Ошибка в команде: \n{e}')

bot.polling()
