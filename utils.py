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

def disable_all_buttons():
    for btn in all_control_buttons:
        try:
            btn.config(state=tk.DISABLED, fg="gray")
        except Exception:
            pass

def enable_all_buttons():
    for btn in all_control_buttons:
        try:
            btn.config(state=tk.NORMAL, fg="black")
        except Exception:
            pass

def _process_print_queue():
    try:
        while not print_queue.empty():
            msg = print_queue.get_nowait()
            if _text_box:
                _text_box.insert(tk.END, f"{msg}\n")
                _text_box.see(tk.END)
    except Exception as e:
        print(f"[printBox error] {e}")
    finally:
        if _root:
            _root.after(100, _process_print_queue)