#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys


if __name__ == '__main__':
    from lib.sbot_lib import ScrapeBot

    bot = ScrapeBot(os.path.dirname(os.path.abspath(__file__)), sys.argv)
    try:
        if bot.errors == 0: 
            bot.execute()
    finally:
        bot.finalize()
        del bot
