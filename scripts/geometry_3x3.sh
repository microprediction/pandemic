# Illustrates how to run simultaneous simulations
# pkill -f shell.py


nohup python3 pandemic/shell.py large_town &
nohup python3 pandemic/shell.py large_town &
nohup python3 pandemic/shell.py large_town geometry n 1.5 &
nohup python3 pandemic/shell.py large_town geometry n 0.7 &
nohup python3 pandemic/shell.py large_town geometry r 1.2 &
nohup python3 pandemic/shell.py large_town geometry r 0.8 &
nohup python3 pandemic/shell.py large_town geometry s 1.5 &
nohup python3 pandemic/shell.py large_town geometry s 0.5 &









