from urllib.error import URLError
import telebot
from telebot import types
import datetime
import csv
import io
import urllib.request

# тестовый бот - test, основной бот - main
token = '7027691302:AAFPHN1OqPISHiRblAQNMy1NnI65qOGvJWs'
bot = telebot.TeleBot(token)

admin_id = 641336894
fortochka = 'Форточка 🕺'
def getSubject(day, para, group):
    # адрес таблицы (без листа)
    url = 'https://docs.google.com/spreadsheets/d/1LePcTz8SUSEnyeqBwbMcUAK6vWGt5K0OD-9TN4kXvLw/export?format=csv'
    # получаем всю таблицу в лист rows
    rows = []
    response = urllib.request.urlopen(url)
    with io.TextIOWrapper(response, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
            #print(row)

    # Возвращаемые значения
    subject_type = ''
    subject_name = ''
    room = ''
    teacher = ''

    input_day_key = 0  # Позиция нужного дня в таблице
    input_para_key = 0  # Позиция нужной пары в таблице
    founded_type = False  # есть ли в названии тип предмета

    # Для сравнения дня недели из таблицы с требуемым
    wday = {"ПОНЕДЕЛЬНИК": 0, "ВТОРНИК": 1, "СРЕДА": 2, "ЧЕТВЕРГ": 3, "ПЯТНИЦА": 4, "СУББОТА": 5}

    # Поиск позиции нужного дня в таблице
    for i in range(1, len(rows) - 1):
        if rows[i][0] in wday and wday[rows[i][0]] == day:
            input_day_key = i




    # Поиск позиции нужной пары в таблице, начиная с позиции нужного дня
    for i in range(input_day_key, len(rows)):
        buffer = rows[i][2]
        buffer = buffer.split('\n')
        if len(buffer) == 2:
            if buffer[0] == str(para):
                input_para_key = i
                break
    print("BUF: ", buffer)

    is_cell_empty = False  # пустая ли клетка предмета
    groups = {3: 7, 4: 9}  # номер группы: номер столбца, относящегося к этой группе
    par_times = {1: '8:15 - 9:50', 2: '10:00 - 11:35', 3: '11:45 - 13:20', 4: '14:00 - 15:35',
                 5: '15:45 - 17:20', 6: '17:30 - 19:05', 7: '19:25 - 21:00'}  # номер пары: время

    group_ind = groups[group]  # получаем столбец нужной группы
    subject = rows[input_para_key][group_ind]  # клетка нужной пары

    # проверка на форточку или объединенную пару
    if subject == '':
        is_cell_empty = True
        subjectOtherGroup = rows[input_para_key][groups[3]]
        if subjectOtherGroup == '':
            subjectPI = rows[input_para_key][3]
            buffer = subjectPI.split('\n')
            subjectPI = buffer[0]
            if subjectPI == 'Физическая культура':
                return {'name': 'Физ-ра', 'type': 'ПЗ', 'room': 'Карла Маркса, 31',
                        'teacher': 'Ксения-Ксения и Сергей-Сергей', 'time': par_times[para]}
            else:
                return {'name': fortochka, 'type': '-', 'room': '-', 'teacher': '-', 'time': par_times[para]}
        else:
            subject_type = 'ЛК'
            founded_type = True
            subject = subjectOtherGroup

    # разделение на предмет и преподавателя
    #print(subject)
    buffer_list = subject.split('\n')  # Список из названия предмета и преподавателя
    buffer = buffer_list[0]  # Название предмета
    teacher = buffer_list[1]  # Преподаватель

    # Удаляем лишний пробел, если есть
    if buffer[-1:] == ' ':
        buffer = buffer[:-1]


    # ищем тип предмета
    for i in range(len(buffer) - 1):
        if buffer[i] + buffer[i + 1] == "ЛК":
            founded_type = True
            subject_type = "ЛК"
        if buffer[i] + buffer[i + 1] == "ПЗ":
            founded_type = True
            subject_type = "ПЗ"
        if founded_type:
            subject_name = buffer[:i] + buffer[i + 2:]
            break

    # если нет типа, определяем как спецкурс
    if not founded_type:
        subject_type = 'какая-то пара\n'
        subject_name = buffer
    # если пустая клетка и не лекция, то это форточка
    print('subject_type: ', subject_type)
    if is_cell_empty and subject_type != 'ЛК':
        print("ФОРТОЧКА СРАБОТАЛА ТУТЬ")

        return {'name': fortochka, 'type': '-', 'room': '-', 'teacher': '-', 'time': par_times[para]}

    if subject_type != 'ЛК':
        room = rows[input_para_key][group_ind + 1]
    else:
        room = rows[input_para_key][groups[4] + 1]

    return {'name': subject_name, 'type': subject_type, 'room': room, 'teacher': teacher, 'time': par_times[para]}


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    group_3 = types.KeyboardButton("/3")
    group_4 = types.KeyboardButton("/4")
    markup.add(group_3, group_4)
    bot.send_message(message.chat.id,
                     text="Укажи номер группы\n(сейчас доступны: 3, 4)".format(
                         message.from_user), reply_markup=markup)


@bot.message_handler(commands=['3', '4'])
def set_group_three(message):
    global set_group
    set_group = int(message.text[1])
    bot.send_message(message.chat.id, text="Группа изменена на " + str(set_group) + "!")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    today = types.KeyboardButton("Сегодня")
    monday = types.KeyboardButton("Понедельник")
    tuesday = types.KeyboardButton("Вторник")
    wendsday = types.KeyboardButton("Среда")
    thursdya = types.KeyboardButton("Четверг")
    friday = types.KeyboardButton("Пятница")
    saturday = types.KeyboardButton("Суббота")
    change_group = types.KeyboardButton("Сменить группу")
    tomorrow = types.KeyboardButton("Завтра")
    markup.add(today, tomorrow, monday, tuesday, wendsday, thursdya, friday, saturday, change_group)
    bot.send_message(message.chat.id,
                     text="Выбери день".format(
                         message.from_user), reply_markup=markup)


def adminfunc(git_code, message):
    git_buffer = '&gid=' + git_code
    buffer = 'https://docs.google.com/spreadsheets/d/1lmSfZIINVP3gnuDD1KppiGMlrJYpwLi0znT3Oh_Y9IQ/export?format=csv' + git_buffer
    try:
        urllib.request.urlopen(buffer)
    except urllib.error.HTTPError:
        bot.send_message(message.chat.id, text="Неправильный git листа!")
        return
    git.gitstr = git_buffer


@bot.message_handler(content_types=['text'])
def func(message):
    weekdays = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота"}
    global set_group
    try:
        print(set_group)
    except NameError:
        set_group = 4
    current_weekday = datetime.datetime.now().weekday()
    messages = {"Понедельник": 0,
                "Вторник": 1,
                "Среда": 2,
                "Четверг": 3,
                "Пятница": 4,
                "Суббота": 5,
                "Сегодня": current_weekday,
                "Завтра": current_weekday + 1, }
    if current_weekday == 6:
        messages["Завтра"] = 0
    if message.text in messages:
        today_number = messages[message.text]
    else:
        if message.text == "Сменить группу":
            start_message(message)
            return
        else:
            if message.chat.id == admin_id:
                adminfunc(message.text, message)
                return
            else:
                bot.send_message(message.chat.id, text="Фигня какая-то")
                return
    if today_number == 6:
        bot.send_message(message.chat.id, text="ВОСКРЕСЕНЬЕ, ЧИЛЛЬ!")
    else:
        amount_pars = 6
        # if today_number == 0 or amount_pars == 5:
        #     amount_pars = 4
        bot.send_message(message.chat.id,
                         text="Вот твоё расписание на " + weekdays[today_number] + "!" + "\n(Номер группы: " + str(
                             set_group) + ")", parse_mode='HTML')
        output_message = []
        for i in range(amount_pars + 1):
            i_subject = getSubject(today_number, i + 1, set_group)
            print(i_subject)
            name = i_subject['name']
            stype = ''
            teacher = ''
            time = ''
            room = ''
            if name != fortochka:
                name += "\n"
                stype = i_subject['type']
                if stype == "ПЗ":
                    stype = "Практосик\n"
                elif stype == "ЛК":
                    stype = "Лектосик\n"
                teacher = i_subject['teacher'] + "\n"
                time = i_subject['time']
                room = "Аудитория " + i_subject['room'] + '\n'
            buffer_list = [str(i + 1) + "-я пара:\n", stype, name, teacher, room, time, "\n", "\n"]
            output_message.append(buffer_list)
        for i in reversed(range(len(output_message))):
            if output_message[i][2] == fortochka:
                output_message[i] = ''
            else:
                break
        buffer_str = ""
        for el in output_message:
            for word in el:
                buffer_str += word
        bot.send_message(message.chat.id, text=buffer_str, parse_mode='HTML')


bot.polling(non_stop=True, interval=0)  # запуск бота