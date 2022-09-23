#!/usr/bin/python3

import telebot

token = ''
bot = telebot.TeleBot(token)
@bot.message_handler(commands=['start'])


def start_message(message):
    bot.send_message(message.chat.id,"Hellow!,-1001567707361")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
	bot.reply_to(message, message.text)
bot.infinity_polling()
