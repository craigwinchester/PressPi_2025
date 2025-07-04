# utils.py
import tkinter as tk
import queue

_root = None
_text_box = None
print_queue = queue.Queue()

all_control_buttons = []

def set_control_buttons(buttons):
    global all_control_buttons
    all_control_buttons = buttons

def set_root_window(root):
    global _root
    _root = root
    # Start the polling loop for printBox queue
    _root.after(100, _process_print_queue)

def set_text_box(widget):
    global _text_box
    _text_box = widget

def printBox(msg):
    print_queue.put(msg)

def _process_print_queue():
    try:
        while not print_queue.empty():
            msg = print_queue.get_nowait()
            if _text_box:
                _text_box.insert(tk.END, f"{msg}\n")
                _text_box.see(tk.END)
                _text_box.update()
    except Exception as e:
        print(f"[printBox error] {e}")
    finally:
        if _root:
            _root.after(100, _process_print_queue)

def convertTime(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)