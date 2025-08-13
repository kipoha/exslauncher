#!/bin/bash

if [ "$1" == "--reload" ]; then
  python $HOME/.config/fabric_launcher/src/main.py --reload
else
  python $HOME/.config/fabric_launcher/src/main.py
fi
