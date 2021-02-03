#!/usr/bin/env python3

import sys
import logging.config
import argparse
from configparser import ConfigParser
import platform
import mailparser
import telebot
import re

if __name__ == '__main__':
    exit_code = 0

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--config',
                            default='/etc/telegram-mailgate/main.cf',
                            help='use a custom configuration file')
    arg_parser.add_argument('--from',
                            help='overwrite field "From" from the header. '
                                 'Ignored if --raw is specified.')
    arg_parser.add_argument('--queue-id',
                            default=0,
                            help='specify the queue ID of the message for logging')
    arg_parser.add_argument('to',
                            nargs='+',
                            help='the recipients')
group = arg_parser.add_mutually_exclusive_group()
args = arg_parser.parse_args()

cfg = ConfigParser()
cfg.read(args.config)

logging.config.fileConfig(cfg['core']['logging_conf_file'])
logger = logging.getLogger()

logger.debug('%s: Reading aliases', args.queue_id)
aliases = open(cfg['core']['aliases'], encoding='utf8').readlines()
aliases = dict([x.strip().split(' ') for x in aliases])

logger.debug('%s: Validating API key', args.queue_id)
api_key = cfg['api']['key']
bot = telebot.TeleBot(api_key, parse_mode=None)

logger.debug('%s: Reading message content', args.queue_id)
raw_content = sys.stdin.read()

for rcpt in args.to:
    try:
        chat_id = aliases[rcpt]
    except KeyError as e:
        print(e)
        exit_code = 69  # EX_UNAVAILABLE
    logger.info('%s: Sending to %s(%s)', args.queue_id, chat_id, rcpt)

    mail = mailparser.mailparser.parse_from_string(raw_content)
    body = mail.text_plain

    #try:
    #    if re.search(r'\\u', body[0]):
    #        body_txt = str(body[0]).encode().decode('unicode_escape')
    #    else:
    #        body_txt = str(body[0])
    #except KeyError as e:
    #        print(e)
    #    exit_code = 69  # EX_UNAVAILABLE
    body_txt = str(body[0])

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(telebot.types.InlineKeyboardButton(text='Подробнее...', callback_data=2),
               telebot.types.InlineKeyboardButton(text='Список файлов...', callback_data=3))
    for item in mail.attachments:
        markup.add(telebot.types.InlineKeyboardButton(text=item['filename'], callback_data=5))

    bot.send_message(chat_id,
                     mail.from_[0][0] + ' ' +  mail.from_[0][1] + '\n' +
                     'ТЕМА: ' + str(mail.subject) + '\n' +
                     body_txt,
                     reply_markup=markup)

exit(exit_code)
