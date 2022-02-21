import telebot
from config import API
import os

bot = telebot.TeleBot(API)

@bot.message_handler(commands=['start'])
def send_hello_message(message):
    user = message.from_user

    bot.send_message(message.chat.id,
                    f'Hello, {user.username}! This bot can extend png files with the prefered text without changing original image.')

@bot.message_handler(content_types='photo')
def get_image(message):
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(f"images/{fileID}.png", 'wb') as new_file:
        new_file.write(downloaded_file)

if __name__ == '__main__':
    if not os.path.exists('images'):
        os.mkdir('images')
        print('Successfully created images directory!')
    print('Bot started!')
    bot.polling()
    


