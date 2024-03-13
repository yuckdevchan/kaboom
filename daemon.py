from global_hotkeys import *
import time, sys, subprocess

# Define the function to be called when hotkey is pressed
def on_activate():
    print("Windows+Space pressed!")
    subprocess.run([sys.executable, "main.py"])

# Define a dummy function for the release_callback
def on_release():
    pass

# Define the hotkey
hotkey = ("window+space", on_activate, on_release)

# Register the hotkey
register_hotkey(*hotkey)

# Start the event loop
start_checking_hotkeys()

# Keep the script running
while True:
    pass
