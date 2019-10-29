#!/bin/bash

source virtenv/bin/activate
nohup python3 ./willBot.py >> bot_launcher.log &
#while :
#do
#   size="$(stat -c %s "bot.log")"
#   if [ "$size" -gt 2000 ]; then
#      tail -c 2000 bot.log > "bot.log"
#   fi;
#done
