#!/bin/bash
# Script that will run both the server and the game

python audio_processing.py &
bash game_prototype.sh &
