# main.py
import asyncio
import threading
import gui  # this runs your full Tkinter UI setup
from drum_position_editor import positions

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Create a new asyncio event loop
asyncio_loop = asyncio.new_event_loop()
t = threading.Thread(target=start_loop, args=(asyncio_loop,), daemon=True)
t.start()
    