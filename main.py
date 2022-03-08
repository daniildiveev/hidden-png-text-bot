import telebot
from config import API
import os
from image_processing import *

bot = telebot.TeleBot(API)
image_ok, text_ok = False, False
message_to_encode = ''
image_path = ''

@bot.message_handler(commands=['start'])
def send_hello_message(message):
    user = message.from_user

    bot.send_message(message.chat.id,
                    f'Hello, {user.username}! This bot can extend png files with the prefered text without changing the look of the original image.')


@bot.message_handler(content_types='photo')
def get_image(message):
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)

    image_path = f"images/{fileID}.png"

    with open(image_path, 'wb') as new_file:
        new_file.write(downloaded_file)
        new_file.close()

    image_ok = True


@bot.message_handler(content_types='text')
def get_text(message):
    message_to_encode = message.json.text
    text_ok = True


@bot.message_handler(commands=['encode'])
def hide_message_in_png(message):
    global image_ok, text_ok
    if image_ok and text_ok:
        result = encode_and_hide_message_in_png(image_path, message_to_encode)

        if isinstance(result, str):
            bot.send_message(message.chat.id, f'Something went wrong: {result}')
        else:
            bot.send_message(message.chat.id, "Everything went smooth!")

            with open(result[1], 'rb') as f:
                bot.send_document(message.chat.id, f)
                f.close()

        image_ok, text_ok = False, False

if __name__ == '__main__':
    if not os.path.exists('images'):
        os.mkdir('images')
        print('Successfully created images directory!')
    print('Bot started!')
    bot.polling()