#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under MIT license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import json
import os
import calendar
import time

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, JobQueue
from telegram.ext.defaults import Defaults

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

vycladachi = {
    "GolDO": ["Гололобов Д.О.", "Gololobov D.O."],
    "GryOM": ["Гришко О.М.", "Gryshko O.M."],
    "MorOV": ["Мороз О.В.", "Moroz O.V."],
    "BelYA": ["Бєлозьорова Я.А.", "Belozorova Y.A."],
    "KorSP": ["Корнієнко С.П.", "Kornienko S.P."],
    "BorLO": ["Борковська Л.О.", "Borkovska L.O."],
    "ZybSV": ["Зибін С.В.", "Zybin S.V."],
    "TreMP": ["Трембовецький М.П.", "Trembovetskyi M.P."],
    "PryOY": ["Приходько О.Ю.", "Prykhodko O.Y."],
    "LytSV": ["Литвинська С.В.", "Lytvynska S.V."],
    "VasMD": ["Васильєва М.Д.", "Vasylieva M.D."],
    "TerLG": ["Теремінко Л.Г.", "Tereminko L.G."],
    "PosLP": ["Поставна Л.П.", "Postavna L.P."],
    "AndTV": ["Андреєва Т.В.", "Andreeva T.V."],
    "SmoUB": ["Смольніков Ю.Б.", "Smolnikov Y.B."],
    "BilNP": ["Білоус Н.П.", "Bilous N.P."],
    "OleTA": ["Олешко Т.А.", "Oleshko T.A."],
    "GriOO": ["Гріненко О.О.", "Grinenko O.O."]
}

pary_type = {
    "LC": ["Лекція", "Lecture"],
    "PC": ["Практична", "Practice"],
    "LB": ["Лабораторна", "Laboratory"],
    "None": ["", ""]
}

pary = {
    "MatAn": ["Математичний аналіз", "Mathematical Analysis"],
    "KDM": ["Комп'ютерна дискретна математика", "Computer Discret Mathematics"],
    "KH": ["Кураторський час", "Curator Hour"],
    "OIPZ": ["Основи інженерії програмного забезпечення", "Software Engineering Foundations"],
    "FIM": ["Фахова іноземна мова", "Professional foreign language"],
    "OP": ["Основи програмування", "Basics of programming"],
    "IYDtK": ["Історія української державності та культури", "History of Ukrainian statehood and culture"],
}

administrators = [
    558344464, # Вова
    825837683, # Аня
    493996898, # Тарас
    827266899, # Толік
    614805155, # Каміла
]

groups = [
    -1001455040673, # 121
    -1001659329648, # 123
    -1001705683153, # 124
]

english_groups = [
    -1001705683153 # 124
]

# дата: [день тижня, навчальний тиждень]
saturday_handler = {
    "01.10": [4, 1],
    "08.10": [5, 1],
    "15.10": [1, 2],
    "22.10": [2, 2],
    "29.10": [3, 2],
    "05.11": [4, 2],
    "12.11": [5, 2],
    "19.11": [1, 1],
    "26.11": [2, 1],
    "03.12": [3, 1],
    "10.12": [4, 1],
    "17.12": [5, 1]
}

# Week we started learning
starting_week = 38

TimeZone = ZoneInfo("Europe/Kiev")

def get_rozklad_string(group_id, date, subgroup, user_id):
    users_languages = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_languages.json"), "r") as file:
        users_languages = json.load(file)
    english_group = 0
    if(group_id in english_groups):
        english_group = 1
    elif(str(user_id) in users_languages):
        english_group = users_languages[str(user_id)]
    global_week = int(date.strftime("%W"))
    week_day = int(date.strftime("%w"))-1

    # Wether it's 1st or 2nd week rn
    array_week = not ((global_week - starting_week) & 1)

    current_string_date = date.strftime("%d.%m")
    if(english_group):
        reply = '<b>Lessons for '
    else:
        reply = '<b>Пари на '
    reply += current_string_date
    #if it's staurday
    if week_day == 5:
        if current_string_date in saturday_handler:
            new_dates = saturday_handler[current_string_date]
            reply += ' (Saturday | '+calendar.day_name[new_dates[0]-1]+' '+str(new_dates[1])+'):</b>\n'
            week_day = new_dates[0]-1
            array_week = new_dates[1]-1
        else:
            if(english_group):
                return 'There are no lessons on ' + current_string_date + '!'
            else:
                return current_string_date + ' ніяких пар немає!'
    elif week_day == -1:
        if(english_group):
            return 'There are no lessons on ' + current_string_date + '!'
        else:
            return current_string_date + ' ніяких пар немає!'
    else:
        reply += ' ('+date.strftime("%A")+' '+str(array_week+1)+'):</b>\n'

    rozkl = []
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), str(group_id)+'.json'), "r") as file:
        rozkl = json.load(file)

    changes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), str(group_id)+"_changes.json"), "r") as file:
        changes = json.load(file)

    today_changes = []
    if date.strftime("%d.%m.%Y") in changes:
        today_changes = changes[date.strftime("%d.%m.%Y")]

    if len(today_changes) >= 1:
        for time in today_changes[0]:
            if today_changes[0][time] == "REMOVE":
                try:
                    del rozkl[0][array_week][week_day][time]
                except (KeyError):
                    ""
            else:
                rozkl[0][array_week][week_day][time] = today_changes[0][time]

        if len(today_changes) >= 2:
            for time in today_changes[1]:
                if today_changes[1][time] == "REMOVE":
                    try:
                        del rozkl[1][array_week][week_day][time]
                    except (KeyError):
                        ""
                else:
                    rozkl[1][array_week][week_day][time] = today_changes[1][time]

    if (len(rozkl)) <= 1:
        subgroup = 0

    if subgroup == -1:
        if(english_group):
            reply += '\n<b>First subgroup:</b>\n'
        else:
            reply += '\n<b>Перша підгрупа:</b>\n'
        loop_array = rozkl[0][array_week][week_day]
        loop_datetime = []

        for time in loop_array:
            loop_datetime.append(datetime.strptime(time, "%H:%M"))
            
        loop_datetime = sorted(loop_datetime)

        for para_time in loop_datetime:
            para_time = para_time.strftime("%H:%M")
            data_array = loop_array[para_time]
            if(english_group):
                posylanny = "Link is missing"
            else:
                posylanny = "Посилання Відсутнє"
            if len(data_array) >= 4:
                if(english_group):
                    posylanny = "<a href='"+data_array[3]+"'>Link</a>"
                else:
                    posylanny = "<a href='"+data_array[3]+"'>Посилання</a>"
            reply += para_time + " - " + pary[data_array[0]][english_group] + ' | ' + (pary_type[data_array[1]][english_group]+' | ' if data_array[1] != "None" else "" ) + vycladachi[data_array[2]][english_group] + ' | ' + posylanny + '\n'

        if(english_group):
            reply += '\n<b>Second subgroup:</b>\n'
        else:
            reply += '\n<b>Друга підгрупа:</b>\n'
        loop_array = rozkl[1][array_week][week_day]
        loop_datetime = []

        for time in loop_array:
            loop_datetime.append(datetime.strptime(time, "%H:%M"))

        loop_datetime = sorted(loop_datetime)

        for para_time in loop_datetime:
            para_time = para_time.strftime("%H:%M")
            data_array = loop_array[para_time]
            posylanny = "Link is missing"
            if len(data_array) >= 4:
                if(english_group):
                    posylanny = "<a href='"+data_array[3]+"'>Link</a>"
                else:
                    posylanny = "<a href='"+data_array[3]+"'>Посилання</a>"
            reply += para_time + " - " + pary[data_array[0]][english_group] + ' | ' + (pary_type[data_array[1]][english_group]+' | ' if data_array[1] != "None" else "" ) + vycladachi[data_array[2]][english_group] + ' | ' + posylanny + '\n'
    else:
        if(english_group):
            reply += ('\n<b>'+('First' if subgroup == 0 else 'Second')+' subgroup:</b>\n')
        else:
            reply += ('\n<b>'+('Перша' if subgroup == 0 else 'Друга')+' підгрупа:</b>\n')
        loop_array = rozkl[subgroup][array_week][week_day]
        loop_datetime = []

        for time in loop_array:
            loop_datetime.append(datetime.strptime(time, "%H:%M"))

        loop_datetime = sorted(loop_datetime)

        for para_time in loop_datetime:
            para_time = para_time.strftime("%H:%M")
            data_array = loop_array[para_time]
            if(english_group):
                posylanny = "Link is missing"
            else:
                posylanny = "Посилання Відсутнє"
            if len(data_array) >= 4:
                if(english_group):
                    posylanny = "<a href='"+data_array[3]+"'>Link</a>"
                else:
                    posylanny = "<a href='"+data_array[3]+"'>Посилання</a>"
            reply += para_time + " - " + pary[data_array[0]][english_group] + ' | ' + (pary_type[data_array[1]][english_group] +' | ' if data_array[1] != "None" else "" ) + vycladachi[data_array[2]][english_group] + ' | ' + posylanny + '\n'

    return reply

def rozklad(update, context):
    users_groups = {}
    # Load data so we can merge later
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_groups.json"), "r") as file:
        users_groups = json.load(file)
    users_group = None

    if (str(update.message.from_user.id) in users_groups):
        users_group = users_groups[str(update.message.from_user.id)] 

    users_subgroups = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_subgroups.json"), "r") as file:
        users_subgroups = json.load(file)

    users_languages = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_languages.json"), "r") as file:
        users_languages = json.load(file)
    english_group = False
    if(update.message.chat_id in english_groups):
        english_group = True
    elif(str(update.message.from_user.id) in users_languages):
        english_group = users_languages[str(update.message.from_user.id)]

    if (update.message.chat_id not in groups):
        if (update.message.chat_id != update.message.from_user.id):
            if(english_group):
                update.message.reply_text('You can only use this command in your group chat!')
            else:
                update.message.reply_text('Використання цієї команди доступне лише в чаті групи!')
            return
        elif not users_group:
            if(english_group):
                update.message.reply_text("You didn't set your main group!")
            else:
                update.message.reply_text('Відсутня обрана основна група!')
            return

    try:
        if len(context.args) >= 1:
            passed_date = datetime.strptime(context.args[0]+'.'+datetime.now(TimeZone).strftime("%Y"), "%d.%m.%Y")
        else:
            passed_date = datetime.now(TimeZone)

        group_id = update.message.chat_id
        if (update.message.chat_id == update.message.from_user.id):
            group_id = users_group

        if(len(context.args) >= 2):
            subgroup = int(context.args[1])-1
        elif (str(update.message.from_user.id) in users_subgroups):
            subgroup = users_subgroups[str(update.message.from_user.id)] 
        else:
            subgroup = -1

        update.message.reply_text(get_rozklad_string(group_id, passed_date, subgroup, update.message.from_user.id), parse_mode = ParseMode.HTML)

    except (IndexError, ValueError, KeyError):
        update.message.reply_text('Ви зробили крінж!')

def rozklad_tomorrow(update, context):
    tomorrow = datetime.now(TimeZone) + timedelta(days=1)
    if len(context.args) >= 1:
        if len(context.args) >= 2:
            context.args[1] = context.args[0]
        else:
            context.args.append(context.args[0])
        context.args[0] = tomorrow.strftime("%d.%m")
    else:
        context.args.append(tomorrow.strftime("%d.%m"))
    return rozklad(update, context)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def sanity_check(update, arguments):
    failed = False
    reply = "<b>Невірні аргументи:</b>\n\n"

    try:
        datetime.strptime(arguments[0], "%d.%m.%Y")
    except (IndexError, ValueError, KeyError):
        reply += "Невірна дата: " + arguments[0] + "\n"
        failed = True
    if int(arguments[1]) != 1 and int(arguments[1]) != 2:
        reply += "Невірна група: " + arguments[1]+"\n"
        failed = True
    try:
        datetime.strptime(arguments[2], "%H:%M")
    except (IndexError, ValueError, KeyError):
        reply += "Невірний час: " + arguments[2] + "\n"
        failed = True
    if arguments[3] == "REMOVE":
        if failed:
            update.message.reply_text(reply, parse_mode = ParseMode.HTML)
        return not failed
    if arguments[3] not in pary:
        reply += "Невірна пара: " + arguments[3]+"\n"
        failed = True
    if arguments[4] not in pary_type:
        reply += "Невірний тип пари : " + arguments[4]+"\n"
        failed = True
    if arguments[5] not in vycladachi:
        reply += "Невірний вчитель: " + arguments[5]+"\n"
        failed = True
    if failed:
        update.message.reply_text(reply, parse_mode = ParseMode.HTML)
    return not failed

def change_rozklad_temp(update, context):
    try:
        if update.message.chat_id not in groups:
            update.message.reply_text('Використання цієї команди доступне лише в чаті групи!')
            return
        if int(update.message.from_user.id) not in administrators:
            update.message.reply_text('Ви не входите в список тих хто може редагувати розклад!')
            return
        if len(context.args) < 4:
            update.message.reply_text('Замало аргументів!')
            return
        if len(context.args) < 6 and context.args[3] != "REMOVE":
            update.message.reply_text('Замало аргументів!')
            return
        if not sanity_check(update, context.args):
            return
        changes = {}
        # Load data so we can merge later
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), str(update.message.chat_id)+"_changes.json"), "r") as file:
            changes = json.load(file)
        context.args[0] = datetime.strptime(context.args[0], "%d.%m.%Y").strftime("%d.%m.%Y")
        subgroup = int(context.args[1])-1
        context.args[2] = datetime.strptime(context.args[2], "%H:%M").strftime("%H:%M")
        if context.args[3] == "REMOVE":
            if context.args[0] in changes:
                if context.args[2] in changes[context.args[0]][subgroup]:
                    del changes[context.args[0]][subgroup][context.args[2]]
                    if len(changes[context.args[0]][0]) <= 0 and len(changes[context.args[0]][0]) <= 0:
                        del changes[context.args[0]]
                else:
                    changes[context.args[0]][subgroup][context.args[2]] = "REMOVE"
            else:
                changes[context.args[0]] = [{}, {}]
                changes[context.args[0]][subgroup][context.args[2]] = "REMOVE"
        else:
            if context.args[0] not in changes:
                changes[context.args[0]] = [{}, {}]
            if len(context.args) >= 7:
                changes[context.args[0]][subgroup][context.args[2]] = [context.args[3], context.args[4], context.args[5], context.args[6]]
            else:
                changes[context.args[0]][subgroup][context.args[2]] = [context.args[3], context.args[4], context.args[5]]
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), str(update.message.chat_id)+"_changes.json"), "w") as file:
            json.dump(changes, file)
        update.message.reply_text('Розклад на '+context.args[0]+' змінено успішно')
    except (IndexError, ValueError, KeyError):
        update.message.reply_text('Ви зробили крінж!')

def sanity_check_perm(update, arguments):
    failed = False
    reply = "<b>Невірні аргументи:</b>\n\n"

    if int(arguments[0]) != 1 and int(arguments[0]) != 2:
        reply += "Невірна група: " + arguments[0]+"\n"
        failed = True
    if int(arguments[1]) != 1 and int(arguments[1]) != 2:
        reply += "Невірний тиждень: " + arguments[1]+"\n"
        failed = True
    if int(arguments[2]) < 1 or int(arguments[2]) > 5:
        reply += "Невірний день тижня: " + arguments[2]+"\n"
        failed = True
    try:
        datetime.strptime(arguments[3], "%H:%M")
    except (IndexError, ValueError, KeyError):
        reply += "Невірний час: " + arguments[3] + "\n"
        failed = True
    if arguments[4] == "REMOVE":
        if failed:
            update.message.reply_text(reply, parse_mode = ParseMode.HTML)
        return not failed
    if arguments[4] not in pary:
        reply += "Невірна пара: " + arguments[4]+"\n"
        failed = True
    if arguments[5] not in pary_type:
        reply += "Невірний тип пари : " + arguments[5]+"\n"
        failed = True
    if arguments[6] not in vycladachi:
        reply += "Невірний вчитель: " + arguments[6]+"\n"
        failed = True
    if failed:
        update.message.reply_text(reply, parse_mode = ParseMode.HTML)
    return not failed

def permanent_rozkl_change(update, context):
    try:
        if update.message.chat_id not in groups:
            update.message.reply_text('Використання цієї команди доступне лише в чаті групи!')
            return
        if int(update.message.from_user.id) not in administrators:
            update.message.reply_text('Ви не входите в список тих хто може редагувати розклад!')
            return
        if (len(context.args) < 5) or (len(context.args) < 7 and context.args[4] != "REMOVE"):
            update.message.reply_text('Замало аргументів!')
            return
        if not sanity_check_perm(update, context.args):
            return
        rozklad = {}
        # Load data so we can merge later
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), str(update.message.chat_id)+".json"), "r") as file:
            rozklad = json.load(file)
        subgroup = int(context.args[0])-1
        week = int(context.args[1])-1
        weekday = int(context.args[2])-1
        time = datetime.strptime(context.args[3], "%H:%M").strftime("%H:%M")
        if context.args[4] == "REMOVE":
            if time in rozklad[subgroup][week][weekday]:
                del rozklad[subgroup][week][weekday][time]
        else:
            if len(context.args) >= 8:
                rozklad[subgroup][week][weekday][time] = [context.args[4], context.args[5], context.args[6], context.args[7]]
            else:
                rozklad[subgroup][week][weekday][time] = [context.args[4], context.args[5], context.args[6]]
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), str(update.message.chat_id)+".json"), "w") as file:
            json.dump(rozklad, file)
        update.message.reply_text('Перманентні зміни до розкладу внесено успішно.')
    except (IndexError, ValueError, KeyError):
        update.message.reply_text('Ви зробили крінж!')

def display_changes(update, context):
    users_languages = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_languages.json"), "r") as file:
        users_languages = json.load(file)
    english_group = False
    if(update.message.chat_id in english_groups):
        english_group = True
    elif(str(update.message.from_user.id) in users_languages):
        english_group = users_languages[str(update.message.from_user.id)]
    try:
        if update.message.chat_id not in groups:
            if(english_group):
                update.message.reply_text('You can only use this command in your group chat!')
            else:
                update.message.reply_text('Використання цієї команди доступне лише в чаті групи!')
            return
        changes = {}
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), str(update.message.chat_id)+"_changes.json"), "r") as file:
            changes = json.load(file)
        if len(changes) != 0:
            response = ""
            for date in changes:
                response += date+": "+json.dumps(changes[date])+"\n"
            update.message.reply_text(response)
        else:
            update.message.reply_text('Ніяких змін до розкладу внесено не було')
    except (IndexError, ValueError, KeyError):
        if(english_group):
            update.message.reply_text('What you did was cringe!')
        else:
            update.message.reply_text('Ви зробили крінж!')

def help(update, context):
    users_languages = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_languages.json"), "r") as file:
        users_languages = json.load(file)
    english_group = False
    if(update.message.chat_id in english_groups):
        english_group = True
    elif(str(update.message.from_user.id) in users_languages):
        english_group = users_languages[str(update.message.from_user.id)]
    if len(context.args) < 1:
        if (english_group):
            update.message.reply_text('Missing argument! Enter name of the command! For a list of commands use /help commands')
        else:
            update.message.reply_text('Відсутній аргумент! Введіть назву команди для допомоги! Для списку комманд введіть /help commands')
        return
    if context.args[0] == "commands":
        if(english_group):
            update.message.reply_text('<b>List of commands:</b> help, timetable, te, timetable_tomorrow, choose_subgroup, change_rozklad_temp, change_rozklad_perm, display_changes', parse_mode = ParseMode.HTML)
        else:
            update.message.reply_text('<b>Список команд:</b> help, rozklad, rozklad_tomorrow, choose_subgroup, change_rozklad_temp, change_rozklad_perm, display_changes', parse_mode = ParseMode.HTML)
    elif context.args[0] == "te":
        if(english_group):
            update.message.reply_text('<b>Syntaxis:</b> date (format: day.month) (optional) | subgroup (optional, value 0 shows timetable for both subgroups)', parse_mode = ParseMode.HTML)
        else:
            update.message.reply_text('<b>Синтаксис:</b> дата (формат: день.місяць) (optional) | підгрупа (optional, значення 0 показує розклад обох підгруп)', parse_mode = ParseMode.HTML)
    elif context.args[0] == "rozklad":
        if(english_group):
            update.message.reply_text('<b>Syntaxis:</b> date (format: day.month) (optional) | subgroup (optional, value 0 shows timetable for both subgroups)', parse_mode = ParseMode.HTML)
        else:
            update.message.reply_text('<b>Синтаксис:</b> дата (формат: день.місяць) (optional) | підгрупа (optional, значення 0 показує розклад обох підгруп)', parse_mode = ParseMode.HTML)
    if context.args[0] == "timetable":
        if(english_group):
            update.message.reply_text('<b>Syntaxis:</b> date (format: day.month) (optional) | subgroup (optional, value 0 shows timetable for both subgroups)', parse_mode = ParseMode.HTML)
        else:
            update.message.reply_text('<b>Синтаксис:</b> дата (формат: день.місяць) (optional) | підгрупа (optional, значення 0 показує розклад обох підгруп)', parse_mode = ParseMode.HTML)
    elif context.args[0] == "change_rozklad_perm":
        if (english_group):
            update.message.reply_text('<b>Syntaxis:</b> sugbroup | week | week day (format: number from 1 to 5) | time (format: hour:minute) | <b>(discipline (encoded) | lesson type (optional) | teacher (encoded) | link (optional))</b> or <b>REMOVE</b>', parse_mode = ParseMode.HTML)
        else:
            update.message.reply_text('<b>Синтаксис:</b> підгрупа | тиждень | день тижня (формат: число від 1 до 5) | час (формат: година:хвилина) | <b>(дисципліна (encoded) | вид пари (optional) | викладач (encoded) | посилання на міт (optional))</b> або <b>REMOVE</b>', parse_mode = ParseMode.HTML)
    elif context.args[0] == "change_rozklad_temp":
        if (english_group):
            update.message.reply_text('<b>Syntaxis:</b> date (format: day.month.year) | subgroup | time (format: hour:minute) | <b>(discipline (encoded) | lesson type (optional) | teacher (encoded) | link (optional)</b> or <b>REMOVE</b>', parse_mode = ParseMode.HTML)
        else:
            update.message.reply_text('<b>Синтаксис:</b> дата (формат: день.місяць.рік) | підгрупа | час (формат: година:хвилина) | <b>(дисципліна (encoded) | вид пари (optional) | викладач (encoded) | посилання на міт (optional)</b> або <b>REMOVE</b>', parse_mode = ParseMode.HTML)
    elif context.args[0] == "display_changes":
        if (english_group):
            update.message.reply_text('No arguments are needed')
        else:
            update.message.reply_text('Ніяких аргументів непотрібно')
    elif context.args[0] == "choose_subgroup":
        if (english_group):
            update.message.reply_text('No arguments are needed')
        else:
            update.message.reply_text('Ніяких аргументів непотрібно')
    elif context.args[0] == "rozklad_tomorrow":
        if (english_group):
            update.message.reply_text('<b>Syntaxis:</b> subgroup (optional, value 0 shows timetable for both subgroups)', parse_mode = ParseMode.HTML)
        else:
            update.message.reply_text('<b>Синтаксис:</b> підгрупа (optional, значення 0 показує розклад обох підгруп)', parse_mode = ParseMode.HTML)
    elif context.args[0] == "help":
        if (english_group):
            update.message.reply_text('<b>Syntaxis:</b> command', parse_mode = ParseMode.HTML)
        else:
            update.message.reply_text('<b>Синтаксис:</b> команда', parse_mode = ParseMode.HTML)
    else:
        if (english_group):
            update.message.reply_text("Such command doesn't exist!")
        else:
            update.message.reply_text('Такої команди не існує!')

def choose_subgroup(user_id, remove, subgroup):
    # Перша підгрупа - 0
    # Друга підгрупа - 1
    if (not user_id) or (not remove and (subgroup != 0 and subgroup != 1)):
        return 
    users_subgroup = {}
    # Load data so we can merge later
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_subgroups.json"), "r") as file:
        users_subgroup = json.load(file)
    if remove:
        del users_subgroup[str(user_id)]
    else:
        users_subgroup[str(user_id)] = subgroup
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_subgroups.json"), "w") as file:
        json.dump(users_subgroup, file)
    return True

def button_callback(update, context):
    users_languages = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_languages.json"), "r") as file:
        users_languages = json.load(file)
    english_group = False
    if(update.callback_query.message.chat_id in english_groups):
        english_group = True
    elif(str(update.callback_query.from_user.id) in users_languages):
        english_group = users_languages[str(update.callback_query.from_user.id)]
    try:
        callback = json.loads(update.callback_query.data)
        if callback:
            if (callback[0] == "UpdateSubgroup"):
                remove = False
                if int(callback[1]) == 3:
                    remove = True
                if choose_subgroup(update.callback_query.from_user.id, remove, int(callback[1])-1):
                    if(english_group):
                        update.callback_query.edit_message_text("Your subgroup was successfully changed")
                    else:
                        update.callback_query.edit_message_text("Вашу підгрупу змінено успішно")
                else:
                    if(english_group):
                        update.callback_query.edit_message_text("What you did was cringe")
                    else:
                        update.callback_query.edit_message_text("Ви зробили крінж")
            elif (callback[0] == "ChangeRozkladPerm"):
                stage = int(callback[1])
            elif (callback[0] == "UpdateLanguage"):
                users_languages = {}
                with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_languages.json"), "r") as file:
                    users_languages = json.load(file)
                users_languages[str(update.callback_query.from_user.id)] = callback[1]
                with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_languages.json"), "w") as file:
                    json.dump(users_languages, file)
                update.callback_query.edit_message_text("Language was successfully changed")
    except (IndexError, ValueError, KeyError):
        if(english_group):
            update.callback_query.edit_message_text("What you did was cringe")
        else:
            update.callback_query.edit_message_text("Ви зробили крінж")

def display_chat_id(update, context):
    update.message.reply_text(str(update.message.chat_id))

def subgroup_preferences(update, context):
    users_languages = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_languages.json"), "r") as file:
        users_languages = json.load(file)
    english_group = False
    if(update.message.chat_id in english_groups):
        english_group = True
    elif(str(update.message.from_user.id) in users_languages):
        english_group = users_languages[str(update.message.from_user.id)]
    if(english_group):
        keyboard = [
            [
                InlineKeyboardButton("First subgroup", callback_data=json.dumps(["UpdateSubgroup", 1])),
                InlineKeyboardButton("Second subgroup", callback_data=json.dumps(["UpdateSubgroup", 2])),
            ],
            [
                InlineKeyboardButton("Remove preference", callback_data=json.dumps(["UpdateSubgroup", 3]))
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Choose your subgroup', reply_markup=reply_markup)
    else:
        keyboard = [
            [
                InlineKeyboardButton("Перша підгрупа", callback_data=json.dumps(["UpdateSubgroup", 1])),
                InlineKeyboardButton("Друга підгрупа", callback_data=json.dumps(["UpdateSubgroup", 2])),
            ],
            [
                InlineKeyboardButton("Прибрати підгрупу", callback_data=json.dumps(["UpdateSubgroup", 3]))
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Виберіть свою підгрупу', reply_markup=reply_markup)

def pick_group_preference(update, context):
    users_languages = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_languages.json"), "r") as file:
        users_languages = json.load(file)
    english_group = False
    if(update.message.chat_id in english_groups):
        english_group = True
    elif(str(update.message.from_user.id) in users_languages):
        english_group = users_languages[str(update.message.from_user.id)]
    if update.message.chat_id not in groups:
        if(english_group):
            update.message.reply_text('You can use this command only in your group chat!')
        else:
            update.message.reply_text('Використання цієї команди доступне лише в чаті групи!')
        return
    users_groups = {}
    # Load data so we can merge later
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_groups.json"), "r") as file:
        users_groups = json.load(file)
    if (str(update.message.from_user.id) in users_groups) and (users_groups[str(update.message.from_user.id)] == update.message.chat.id):
        del users_groups[str(update.message.from_user.id)]
        if(english_group):
            update.message.reply_text(update.message.chat.title + ' is not going to be your main group anymore!')
        else:
            update.message.reply_text(update.message.chat.title + ' більше не буде вашою основною групою!')
    else:
        users_groups[str(update.message.from_user.id)] = update.message.chat_id
        if(english_group):
            update.message.reply_text(update.message.chat.title + ' is your main group now!')
        else:
            update.message.reply_text(update.message.chat.title + ' тепер ваша основна група!')
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "users_groups.json"), "w") as file:
        json.dump(users_groups, file)

def reschedule_lessons(job_queue: JobQueue):
    today = datetime.now(TimeZone)
    global_week = int(today.strftime("%W"))
    week_day = int(today.strftime("%w"))-1

    # Wether it's 1st or 2nd week rn
    array_week = not ((global_week - starting_week) & 1)
    for group in groups:
        rozkl = []
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), str(group)+'.json'), "r") as file:
            rozkl = json.load(file)

        changes = {}
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), str(group)+"_changes.json"), "r") as file:
            changes = json.load(file)

        today_changes = []
        if today.strftime("%d.%m.%Y") in changes:
            today_changes = changes[today.strftime("%d.%m.%Y")]

        if len(today_changes) >= 1:
            for hours in today_changes[0]:
                if today_changes[0][hours] == "REMOVE":
                    del rozkl[0][array_week][week_day][hours]
                else:
                    rozkl[0][array_week][week_day][hours] = today_changes[0][hours]

            if len(today_changes) >= 2:
                for hours in today_changes[1]:
                    if today_changes[1][hours] == "REMOVE":
                        del rozkl[1][array_week][week_day][hours]
                    else:
                        rozkl[1][array_week][week_day][hours] = today_changes[1][hours]

        for subgroup in range(0, len(rozkl)-1):
            loop_array = rozkl[subgroup][array_week][week_day]
            loop_datetime = []

            for hours in loop_array:
                loop_datetime.append(datetime.strptime(hours, "%H:%M"))

            loop_datetime = sorted(loop_datetime)

            for para_time in loop_datetime:
                para_time = para_time.strftime("%H:%M")
                data_array = loop_array[para_time]
                lesson = pary[data_array[0]]
                lesson_type = pary_type[data_array[1]]
                teacher = vycladachi[data_array[2]]
                link = "Посилання Відсутнє"
                if len(data_array) >= 4:
                    link = data_array[3]

                job_queue.run_once(send_lessons(group, subgroup, lesson, lesson_type, teacher, link),
                    when=time.time(2022, 9, 19, 0, 0, 0, 0, tzinfo=TimeZone))

def send_lessons(group, subgroup, lesson, lesson_type, teacher, link):
    ""

def choose_language(update, context):
    keyboard = [
        [
            InlineKeyboardButton("Ukranian", callback_data=json.dumps(["UpdateLanguage", 0])),
            InlineKeyboardButton("English", callback_data=json.dumps(["UpdateLanguage", 1])),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose prefered language', reply_markup=reply_markup)

# Enter your token here
botToken = None

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(
        botToken,
        use_context=True,
        defaults=Defaults(disable_notification=True, disable_web_page_preview=True, run_async=True)
    )

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("rozklad", rozklad))
    dp.add_handler(CommandHandler("rozklad_tomorrow", rozklad_tomorrow))
    dp.add_handler(CommandHandler("te", rozklad))
    dp.add_handler(CommandHandler("timetable", rozklad))
    dp.add_handler(CommandHandler("timetable_tomorrow", rozklad_tomorrow))
    dp.add_handler(CommandHandler("change_rozklad_temp", change_rozklad_temp))
    dp.add_handler(CommandHandler("change_rozklad_perm", permanent_rozkl_change))
    dp.add_handler(CommandHandler("display_changes", display_changes))
    # dp.add_handler(CommandHandler("show_id", display_chat_id))
    dp.add_handler(CommandHandler("choose_group", pick_group_preference))
    dp.add_handler(CommandHandler("choose_subgroup", subgroup_preferences))
    dp.add_handler(CommandHandler("choose_language", choose_language))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CallbackQueryHandler(button_callback))

    # log all errors
    dp.add_error_handler(error)

    # j = updater.job_queue

    # scheduling = j.run_repeating(reschedule_lessons,
        #interval=timedelta(days = 1), first=datetime(2022, 9, 19, 0, 0, 0, 0, tzinfo=TimeZone))

    # reschedule_lessons(j)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
