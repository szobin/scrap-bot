#!/usr/bin/python
# -*- coding: utf-8 -*-
import redis
import os
import threading
from lib.sbot_lib import ScrapeBot

BOOKIE_REDIS_HOST = "127.0.0.1"
BOOKIE_REDIS_PORT = 6379

REDIS_CONN = redis.StrictRedis(host=BOOKIE_REDIS_HOST, port=BOOKIE_REDIS_PORT)
TABTOUCH_SCRAPE_CHANNEL = 'TABTOUCHSCRAPECHANNEL'


def scrape_race(args):
    bot = ScrapeBot(os.path.dirname(os.path.abspath(__file__)), args.split(','))
    try:
        if bot.errors == 0:
            bot.execute()
    finally:
        bot.finalize()


def subscribe_to_scrape_channel():
    ps = REDIS_CONN.pubsub()
    ps.subscribe(TABTOUCH_SCRAPE_CHANNEL)
    for item in ps.listen():
        data = str(item['data'])
        if not data.startswith('tabtouch'):
            continue
        threading.Thread(target=scrape_race, args=(data,)).start()


if __name__ == '__main__':
    subscribe_to_scrape_channel()