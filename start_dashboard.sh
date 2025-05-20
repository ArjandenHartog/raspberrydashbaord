#!/bin/bash

# Wacht tot de grafische omgeving volledig is opgestart
sleep 10

# Zet de DISPLAY variabele
export DISPLAY=:0

# Zet de XAUTHORITY variabele (belangrijk voor grafische toegang)
export XAUTHORITY=/home/pi/.Xauthority

# Ga naar de juiste directory waar de scripts staan
cd "$(dirname "$0")"

# Start het dashboard
python3 main.py 