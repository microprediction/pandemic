# Illustrates how to run simultaneous simulations
# pkill -f cmd.py

nohup python3 pandemic/cmd.py large_town geometry r 0.6 &
nohup python3 pandemic/cmd.py large_town geometry r 0.8 &
nohup python3 pandemic/cmd.py large_town geometry r 1.2 &
nohup python3 pandemic/cmd.py large_town geometry r 1.4 &










