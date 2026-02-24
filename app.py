import re
import telebot
from telebot import types
import datetime
import GSparse

# тестовый бот - test, основной бот - main
token = '7027691302:AAFPHN1OqPISHiRblAQNMy1NnI65qOGvJWs'
gsURL = 'https://docs.google.com/spreadsheets/d/1LePcTz8SUSEnyeqBwbMcUAK6vWGt5K0OD-9TN4kXvLw'
bot = telebot.TeleBot(token)
admin_id = 641336894
availableGroups = ['1', '2', '3', '4', '5', '6', '7']
dayButtons = ['Сегодня', 'Завтра', 'Понедельник',
              'Вторник', 'Среда', 'Четверг',
              'Пятница', 'Суббота', 'Сменить группу']
global groupNumber


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # for i in range(1,8):
    #     markup.add(types.KeyboardButton(str(i)))
    markup.add(*availableGroups)
    bot.send_message(message.chat.id,
                     text="Укажи номер группы (1-7)".format(
                         message.from_user), reply_markup=markup)


def chooseDay(message, group):
    bot.send_message(message.chat.id, text="Группа изменена на " + str(group) + "!")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*dayButtons)
    bot.send_message(message.chat.id,
                     text="Выбери день".format(
                         message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    global groupNumber
    gettedMessage = re.match(r"(\d+)", message.text)
    if gettedMessage and gettedMessage.group(1) in availableGroups:
        gettedMessage = gettedMessage.group(1)
        groupNumber = gettedMessage
        chooseDay(message, gettedMessage)
    # Buttons from dayButtons list
    elif message.text in dayButtons:
        # Today button
        if message.text == dayButtons[0]:
            dayNumber = datetime.datetime.now().weekday()
            if dayNumber == 6:
                return
            else:
                day = dayButtons[dayNumber + 1]
        # Tomorrow button
        elif message.text == dayButtons[1]:
            dayNumber = datetime.datetime.now().weekday() + 1
            if dayNumber == 6:
                bot.send_message(message.chat.id, text='Сегодня воскресенье!')
                return
            else:
                day = dayButtons[dayNumber + 1]
        # Change group button
        elif message.text == dayButtons[8]:
            start_message(message)
            return
        else:
            day = message.text
        # Weekday button
        day = day.upper()
        cells = GSparse.GetGS(gsURL)
        rowIndexes, groupIndexes = GSparse.getTimetableIndexes(cells)
        myTimetable = GSparse.getMyTimetable(rowIndexes[day], groupIndexes[groupNumber], cells)
        bot.send_message(message.chat.id, text=myTimetable)
    # Wrong button (message)
    else:
        bot.send_message(message.chat.id,
                         text="Не пон".format(
                             message.from_user))


bot.polling(non_stop=True, interval=0)  # запуск бота
