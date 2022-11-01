#pip install pyTelegramBotAPI
import telebot
import pandas as pd
import requests
from datetime import date
import os
import time
import contextlib
import hashlib

API_TOKEN = '5681868224:AAGvXXQYU0jbxL6lh53bPCfqbDDOZ4vlsVg'
bot = telebot.TeleBot(API_TOKEN)

@contextlib.contextmanager
def report_time(test):
    t0 = time.time()
    yield
    print("Time needed for `%s' called: %.2fs" % (test, time.time() - t0))


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! 👋'
                                      '\nЯ бот для хэширования в md5 🤖'
                                      '\nЯ создан, чтобы преобразовывать номера телефонов '
                                      'в их хэши для отправки в рекламные системы.'
                                      '\nВы можете отправить список номеров телефонов в файле по шаблону:')
    bot.send_document(chat_id=message.chat.id, document=open("default/Шаблон.xlsx", 'rb'))
    bot.send_message(message.chat.id, 'Либо вы можете просто отправить номер телефона в сообщении '
                                      'и в ответ вы получите его хэш.')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Для конвертации номеров телефонов в хэши '
                                      'вы можете отправить список по шаблону:')
    bot.send_document(chat_id=message.chat.id, document=open("default/Шаблон.xlsx", 'rb'))
    bot.send_message(message.chat.id, 'Либо просто отправить номер телефона в сообщении и в ответ вы получите его хэш.')


@bot.message_handler(content_types=['text'])
def echo_msg(message):
    phone = message.text
    phone_md5 = hashlib.md5(str(phone).encode()).hexdigest()
    bot.send_message(message.chat.id, "#️⃣ md5 хэш: {}".format(phone_md5))


@bot.message_handler(content_types=['document'])
def send_text(message):
    try:
        bot.send_message(message.chat.id, '⏳ Подождите, преобразуем номера')
        file_id = message.document.file_name
        file_name = message.document.file_name
        file_id_info = bot.get_file(message.document.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(API_TOKEN, file_id_info.file_path))
        downloaded_file = bot.download_file(file_id_info.file_path)
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        new_file.close()
        if file_name[-5:] == ".xlsx":
            phones = pd.read_excel(file_name)
            if phones.shape[1] == 1:
                phones.columns = ["phone"]
                phones['md5'] = [hashlib.md5(str(num).encode()).hexdigest() for num in phones['phone']]
                output_file_name = 'md5_hashes_{}.xlsx'.format(str(date.today()))
                phones['md5'].to_excel(output_file_name, index=False)
                bot.send_message(message.chat.id, '✅ Готово! '
                                                  '\nОбработано номеров: {}'.format(len(phones["phone"])))
                bot.send_document(chat_id=message.chat.id, document=open(output_file_name, 'rb'))
                os.remove(output_file_name)
                os.remove(file_name)
            else:
                bot.send_message(message.chat.id, '⛔️ Ошибка!'
                                                  '\nНеправильный формат файла.'
                                                  '\nВоспользуйтесь шаблоном ниже:')
                bot.send_document(chat_id=message.chat.id, document=open("default/Шаблон.xlsx", 'rb'))
                os.remove(file_name)
        else:
            bot.send_message(message.chat.id, '⛔️ Ошибка!'
                                              '\nНеправильный формат файла.'
                                              '\nВоспользуйтесь шаблоном ниже:')
            bot.send_document(chat_id=message.chat.id, document=open("default/Шаблон.xlsx", 'rb'))
            os.remove(file_name)
    except AttributeError:
        bot.send_message(message.chat.id, '⛔️ Ошибка!'
                                          '\nНеправильный формат файла.'
                                          '\nВоспользуйтесь шаблоном ниже:')
        bot.send_document(chat_id=message.chat.id, document=open("default/Шаблон.xlsx", 'rb'))
    except Exception as e:
        bot.send_message(message.chat.id, '⛔️ Ошибка!'
                                          '\nКод ошибки: {} '
                                          '\n❗️Сообщите о ней @amurylev'.format(e))


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as err:
        print('⛔️Ошибка! Код ошибки: {} ⛔️'.format(err))
        bot.polling(none_stop=True)
