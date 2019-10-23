#!/bin/bash
a=`date +%y-%m-%d-%H-%M-%S`
echo "bot-start: "$a  >> /home/ubuntu/scrapbot/call_log.txt
cd /home/ubuntu/scrapbot
/home/ubuntu/scrapbot/bot_run_horses.bat
cd /home/ubuntu
a=`date +%y-%m-%d-%H-%M-%S`
echo "bot-fin: "$a >> /home/ubuntu/scrapbot/call_log.txt

