#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This file is part of RogueTG.

RogueTG is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

RogueTG is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with RogueTG.  If not, see <http://www.gnu.org/licenses/>.
'''

from datetime import timedelta
from time import sleep
from twx.botapi import TelegramBot
import json
import requests
import uptime

__author__ = "NotoriousDev Team"
__copyright__ = "Copyright 2015, NotoriousDev"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "NotoriousDev Team"
__email__ = "dev@notoriousdev.com"


try:
    import config
except:
    print "Config not found! Please copy config.py.dist to config.py and edit the values as necessary."
    exit(1)

last_update = 0

bot = TelegramBot(config.BOT_API_KEY)
bot.update_bot_info().wait()

updates = bot.get_updates().wait()
if updates is not None:
    for update in updates:
        if update.update_id > last_update:
            last_update = update.update_id


def loop():
    global last_update
    global bot
    updates = bot.get_updates().wait()
    if updates is not None:
        for update in updates:
            if update is None:
                continue
            if update.update_id is None:
                continue
            if update.update_id <= last_update:
                continue
            if update.message.text is None:
                continue

            print update
            last_update = update.update_id
            text_split = update.message.text.split(' ')
            cmd = text_split[0].split("@")[0]
            args = text_split[1:] or None
            chat_id = update.message.chat.id
            sender = update.message.sender

            if cmd == '/ping':
                bot.send_message(chat_id, 'Pong!').wait()

            if cmd == '/uptime':
                bot.send_message(chat_id, str(timedelta(seconds=uptime.uptime())).rsplit('.', 1)[0]).wait()

            if cmd == '/idme':
                bot.send_message(chat_id, '%s, your user ID is %s' % (sender.first_name, sender.id)).wait()

            if cmd == '/mcstatus':
                status = requests.get('http://status.mojang.com/check').text
                status = json.loads(status)
                message = '-- Mojang Service Status --\n\n'
                for i in status:
                    k, v = list(i.items())[0]
                    message += "%s: %s\n" % (k, v.replace('green', u'✅').replace('red', u'🚫').replace('yellow', u'⚠️'))
                bot.send_message(chat_id, message, True).wait()

if __name__ == '__main__':
    while True:
        sleep(0.5)
        try:
            loop()
        except:
            continue
