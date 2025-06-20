# drum_position_editor.py 

import json
import tkinter as tk
from tkinter import Toplevel, Label, Button as TkButton
from config import POSITIONS_FILE_PATH, TOUCHSCREEN_ENABLED
from touchscreen_keypad import NumericKeypad

positions = {}

def load_positions():
    global positions
    print(f"Attempting to open: {POSITIONS_FILE_PATH}")
    try:
        with open(POSITIONS_FILE_PATH, "r") as f:
            positions = json.load(f)
    except FileNotFoundError:
        positions = {
            "drum_positions": {
                "fill_position_seconds": 0.0,
                "drain_position_seconds": 0.0,
                "door_down_position_seconds": 0.0
            },
            "cam_hold_time": 1.0
        }
    return positions

def save_positions(updated):
    with open(POSITIONS_FILE_PATH, "w") as f:
        json.dump(updated, f, indent=4)

def open_positions_editor(root):
    global positions
    editor = Toplevel(root)
    editor.title("Edit Drum Timing Settings")

    def create_field(label_text, var_name, row):
        Label(editor, text=label_text).grid(row=row, column=0, padx=10, pady=5)

        default_value = (
            positions["drum_positions"].get(var_name, "")
            if var_name != "cam_hold_time"
            else positions.get("cam_hold_time", 1.0)
        )

        spinbox = tk.Spinbox(
            editor, from_=0.0, to=120.0, increment=0.1,
            format="%.1f", width=10
        )
        spinbox.delete(0, tk.END)
        spinbox.insert(0, default_value)
        spinbox.grid(row=row, column=1, padx=10)

        if TOUCHSCREEN_ENABLED:
            spinbox.bind("<Button-1>", lambda e, widget=spinbox: open_keypad(editor, widget))

        return spinbox
    
    def open_keypad(master, widget):
        original_bg = widget.cget("background")
        if hasattr(widget, 'configure'):
            try:
                widget.configure(background="yellow")
            except tk.TclError:
                pass
        def restore():
            if hasattr(widget, 'configure'):
                try:
                    widget.configure(background=original_bg)
                except tk.TclError:
                    pass
        NumericKeypad(master, widget, on_close=restore)

    fill_entry = create_field("Fill Position (sec)", "fill_position_seconds", 0)
    drain_entry = create_field("Drain Position (sec)", "drain_position_seconds", 1)
    door_entry = create_field("Door Down Position (sec)", "door_down_position_seconds", 2)
    cam_hold_entry = create_field("Cam Hold Time (sec)", "cam_hold_time", 3)

    def save():
        positions["drum_positions"]["fill_position_seconds"] = float(fill_entry.get())
        positions["drum_positions"]["drain_position_seconds"] = float(drain_entry.get())
        positions["drum_positions"]["door_down_position_seconds"] = float(door_entry.get())
        positions["cam_hold_time"] = float(cam_hold_entry.get())

        save_positions(positions)
        load_positions()
        editor.destroy()

    TkButton(editor, text="Save Settings", command=save).grid(row=4, column=0, columnspan=2, pady=10)

# Automatically load config on import
positions = load_positions()
