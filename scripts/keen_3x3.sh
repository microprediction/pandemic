# Illustrates how to run simultaneous simulations
# pkill -f shell.py

nohup python3 pandemic/shell.py large_town motion k 0.6 &
nohup python3 pandemic/shell.py large_town motion k 0.7 &
nohup python3 pandemic/shell.py large_town motion k 0.8 &
nohup python3 pandemic/shell.py large_town motion k 0.9 &
nohup python3 pandemic/shell.py large_town &
nohup python3 pandemic/shell.py large_town motion k 1.1 &
nohup python3 pandemic/shell.py large_town motion k 1.2 &
nohup python3 pandemic/shell.py large_town motion k 1.3 &
nohup python3 pandemic/shell.py large_town motion k 1.4 &










