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

    elif not image_ok and not text_ok:
        bot.send_message(message.chat.id, "Both of your text and your image are missing")
    elif not image_ok:
        bot.send_message(message.chat.id, "You haven't uploaded any images yet")
    elif not text_ok:
        bot.send_message(message.chat.id, "You haven't sent me any text messages yet")

@bot.message_handler(commands=['decode'])
def decode_image(message):
    global image_ok, image_path

    if image_ok:
        result = retrieve_message_from_png(image_path)

        if isinstance(result, int):
            bot.send_message(message.chat.id, "There are no secret messages in this image")
        else:
            bot.send_message(message.chat.id, "Found secret message!! Here it is:")
            bot.send_message(message.chat.id, result)

        image_ok = False

    else:
        bot.send_message(message.chat.id, "Seems like you haven't uploaded any images yet")


@bot.message_handler(content_types='photo')
def get_image(message):
    global image_ok, image_path
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)

    image_path = f"images/{fileID}.png"

    with open(image_path, 'wb') as new_file:
        new_file.write(downloaded_file)
        new_file.close()

    bot.send_message(message.chat.id, "Got your image!")

    image_ok = True


@bot.message_handler(content_types='text')
def get_text(message):
    global text_ok, message_to_encode
    message_to_encode = message.json['text']
    bot.send_message(message.chat.id, f"Your secret message is: {message_to_encode}")
    text_ok = True

if __name__ == '__main__':
    if not os.path.exists('images'):
        os.mkdir('images')
        print('Successfully created images directory!')
    print('Bot started!')
    bot.polling()
