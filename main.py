import telebot
import requests
import config
import random
from telebot import types

bot = telebot.TeleBot(config.telegram_server_key, parse_mode=None)  # for SERVER


# bot = telebot.TeleBot(config.telegram_pc_key, parse_mode=None)  # for PC


def what_weather(city):
    """Функция принимает топоним как аргумент и возвращает температуру в его окрестностях в градусах цельсия.
    Топоним может задаваться на любом языке, предпочтительнее на английском. Предпочтительная форма - "город, страна",
    например "Paris, France". Чем точнее указан топоним, тем вероятнее его правильное распознавание.
    При неправильном распозновании топонима, будет возвращена температура в другом месте, либо 0.
    При недоступности серверов погоды или других ошибках будет возвращен 0."""

    url = f'http://wttr.in/{city}'
    weather_parameters = {
        'format': "%t",
        'm': ''
    }
    try:
        response = requests.get(url, params=weather_parameters)
    except requests.ConnectionError:
        return 0
    if response.status_code == 200:
        return int(response.text.strip()[0:-2])
    else:
        return 0


@bot.message_handler(commands=['start'])
def welcome(message):
    sti = open('panda.jfif', 'rb')
    bot.send_sticker(message.chat.id, sti)

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("❓ Помощь")
    item2 = types.KeyboardButton("😊 Как дела?")

    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     "Привет, {0.first_name}!\n"
                     "Я - <b>{1.first_name}</b>, бот, созданный чтобы помочь осознанным людям "
                     "вести полноценный здоровый образ жизни.\n"
                     "Пока я умею давать только одну рекомендацию. "
                     "Чтобы её получить, напиши город, в котором ты находишься.".format(message.from_user,
                                                                                        bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_echo(message):
    if message.chat.type == 'private':
        if message.text == '❓ Помощь':
            bot.send_message(message.chat.id,
                             "Если вы обнаружили, что бот работает неправильно, напишите ему без кавычек "
                             "слово 'Ошибка', двоеточие, а затем опишите проблему, например:\n"
                             "Ошибка: зацикливается при ответе\n"
                             "К сообщению обязательно приложите скриншот экрана с ошибкой!")
        elif message.text == '😊 Как дела?':

            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
            item2 = types.InlineKeyboardButton("Не очень", callback_data='bad')

            markup.add(item1, item2)

            bot.send_message(message.chat.id, 'Отлично, сам как?', reply_markup=markup)
        else:
            temp = what_weather(message.text)
            answer = 'Температура воздуха в твоём городе сейчас примерно ' + str(temp) + '\n\n'
            if temp < -20:
                answer += 'Это очень холодно.\n'
                answer += 'Увеличь калорийность своего дневного рациона на 5% за каждый час, проведённый на улице (10 часов в сутки - плюс 50%).'
            elif temp < 0:
                answer += 'Это холодно.\n'
                answer += 'Увеличь калорийность своего дневного рациона на 2% за каждый час, проведённый на улице (10 часов в сутки - плюс 20%).'
            else:
                answer += 'При такой температуре калорийность дневного рациона не нуждается в корректировке.\n'
            bot.send_message(message.chat.id, answer)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Вот и отличненько 😊')
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Бывает 😢')

            # remove inline buttons
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="😊 Как дела?",
                                  reply_markup=None)

            # show alert
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text="ЭТО ТЕСТОВОЕ УВЕДОМЛЕНИЕ!!11")

    except Exception as e:
        print(repr(e))


# RUN
bot.polling(none_stop=True)
