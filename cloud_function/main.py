import os
import requests
import telebot
from telebot import types

import resources.captions as cap

color_to_index_dict = {
    0: 'GREEN',
    1: 'BLUE',
    2: 'PURPLE',
    3: 'YELLOW',
    4: 'ORANGE'
}

CLOUD_RUN_URL = os.environ["CLOUD_RUN_URL"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]


def generate_full_caption(num_ranges):
    full_value = 100
    range_size = full_value / num_ranges
    start = 0
    ranges = []

    for i in range(num_ranges):
        end = start + range_size
        ranges.append((i, (start, end)))
        start = end

    color_ranges = []
    for index, num_range in ranges:
        color_name = color_to_index_dict.get(index)
        color_ranges.append((color_name, num_range))

    general_caption = cap.start_results_caption + "\n" + cap.fabricated_entities_caption + "\n"
    for color, (start, end) in color_ranges:
        probability_range = f"{start:.2f}% to {end:.2f}%"
        general_caption += "\n" + cap.general_caption.format(color, probability_range)
    general_caption += "\n" + "\n" + cap.end_results_caption
    return general_caption


def get_file_content(bot, file_id):
    file_info = bot.get_file(file_id)
    file_url = f'https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}'
    response = requests.get(file_url)
    return response.content


def get_processed_file_name(original_file_name):
    file_name, file_extension = get_file_name_parts(original_file_name)
    return file_name + '_analyzed' + '.' + file_extension


def get_file_name_parts(original_file_name):
    last_dot_index = original_file_name.rfind('.')
    if last_dot_index == -1:
        return original_file_name, ''
    else:
        base_name = original_file_name[:last_dot_index]
        extension = original_file_name[last_dot_index + 1:]
        return base_name, extension


def handle_start_message(bot, chat_id):
    message_text = cap.start_message
    bot.send_message(chat_id=chat_id, text=message_text)


def handle_started_processing(bot, chat_id, file_name, message_id):
    started_processing_text = cap.started_processing_message.format(file_name)

    gif_file_path = "resources/searching.gif"
    if os.path.exists(gif_file_path):
        with open(gif_file_path, "rb") as gif_file:
            bot.send_document(chat_id=chat_id, document=gif_file, reply_to_message_id=message_id,
                              caption=started_processing_text)
    else:
        bot.send_message(chat_id=chat_id, text=started_processing_text)


def handle_available_settings(bot, chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2)

    buttons = [types.KeyboardButton(str(i)) for i in range(2, 6)]
    markup.row(buttons[0], buttons[1])
    markup.row(buttons[2], buttons[3])
    bot.send_message(chat_id=chat_id, text="Please, choose number of ranges:", reply_markup=markup)


def handle_choosing_of_settings(bot, chat_id, value):
    formatted_url = CLOUD_RUN_URL + "/settings"
    data = {
        'chatId': str(chat_id),
        'probabilityRangesCount': int(value)
    }
    response = requests.post(formatted_url, json=data)
    if response.status_code == 201:
        bot.send_message(chat_id=chat_id,
                         text="Settings were saved successfully! Please send CV in .pdf format for analyzing by bot")
    else:
        bot.send_message(chat_id=chat_id, text="Failed to save settings. Please try again")


def telegram_bot(request):
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.get_data(as_text=True))

        chat_id = update.message.chat.id
        message_id = update.message.message_id

        if update.message.document:
            document = update.message.document
            full_file_name = document.file_name
            file_extension = get_file_name_parts(full_file_name)
            if file_extension[1] != "pdf":
                bot.send_message(chat_id=chat_id, reply_to_message_id=message_id,
                                 text="Upload file with {} extension, please".format("pdf"))
                return "OK"
            handle_started_processing(bot, chat_id, full_file_name, message_id)

            file_content = get_file_content(bot, document.file_id)
            formatted_url = CLOUD_RUN_URL + "/process" + "?chatId=" + str(chat_id)
            response = requests.post(formatted_url, files={'file': file_content})
            ranges_num = int(response.headers.get('Ranges-Count'))
            general_probability = str(response.headers.get('General-Probability'))
            formatted_probability = "{:.2f}".format(float(general_probability))
            if response.ok:
                bot.send_document(chat_id=chat_id, visible_file_name=get_processed_file_name(full_file_name),
                                  document=response.content,
                                  reply_to_message_id=message_id,
                                  caption=generate_full_caption(ranges_num),
                                  parse_mode="HTML")
                bot.send_message(chat_id=chat_id, reply_to_message_id=message_id,
                                 text="Percentage of AI generated content in analyzed text: {} %".format(
                                     formatted_probability))
        elif '/start' in update.message.text:
            handle_start_message(bot, chat_id)
        elif '/set_ranges' in update.message.text:
            handle_available_settings(bot, chat_id)
        elif update.message.text in ["2", "3", "4", "5"]:
            handle_choosing_of_settings(bot, chat_id, update.message.text)

    return "OK"
