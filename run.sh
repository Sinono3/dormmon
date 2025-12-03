#!/bin/sh
export DISPLAY=":0.0"
flask run -h 0.0.0.0 -p 5000 &
cd acn_ui
python ui.py
