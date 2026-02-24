import re
import telebot
from telebot import types
import datetime
import GSparse
from flask import Flask, request

token = '7027691302:AAFPHN1OqPISHiRblAQNMy1NnI65qOGvJWs'
gsURL = 'https://docs.google.com/spreadsheets/d/1LePcTz8SUSEnyeqBwbMcUAK6vWGt5K0OD-9TN4kXvLw'
bot = telebot.TeleBot(token)
app = Flask(__name__)
admin_id = 641336894
availableGroups = ['1', '2', '3', '4', '5', '6', '7']
dayButtons = ['Сегодня', 'Завтра', 'Понедельник',
              'Вторник', 'Среда', 'Четверг',
              'Пятница', 'Суббота', 'Сменить группу']
users = {}
file = open('users', 'r')
for line in file:
    user, number = line.split(':')
    number = number[0]
    users[int(user)] = number


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
    # Select group number
    groupNumberMatch = re.match(r"(\d+)", message.text)
    if groupNumberMatch and groupNumberMatch.group(1) in availableGroups:
        groupNumberMatch = groupNumberMatch.group(1)
        if message.chat.id in users:
            users[message.chat.id] = groupNumberMatch
            fileC = open("users", "w")
            for key, value in users.items():
                fileC.write(f'{key}:{value}\n')
        else:
            users[message.chat.id] = groupNumberMatch
            fileA = open("users", 'a')
            fileA.write(f'{message.chat.id}:{groupNumberMatch}\n')
        chooseDay(message, groupNumberMatch)
    # Buttons from dayButtons list
    elif message.chat.id not in users:
        start_message(message)
        return
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
        myTimetable = GSparse.getMyTimetable(rowIndexes[day], groupIndexes[users[message.chat.id]], cells)
        bot.send_message(message.chat.id, text=myTimetable)
    # Wrong button (message)
    else:
        bot.send_message(message.chat.id,
                         text="Не пон".format(
                             message.from_user))


@app.route(f"/{token}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://phystimetablebot-production.up.railway.app/{token}")
    app.run(host="0.0.0.0", port=5000)
