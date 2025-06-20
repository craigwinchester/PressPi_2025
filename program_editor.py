# program_editor.py

import tkinter as tk
from tkinter import messagebox
import json
import os
from config import PROGRAMS_FILE_PATH, TOUCHSCREEN_ENABLED
from touchscreen_keypad import NumericKeypad

programs = []

def load_programs():
    global programs
    print(f"Attempting to open: {PROGRAMS_FILE_PATH}")
    try:
        with open(PROGRAMS_FILE_PATH, "r") as f:
            loaded_programs = json.load(f)
            if isinstance(loaded_programs, list):
                programs.clear()
                programs.extend(loaded_programs)
            else:
                messagebox.showerror("File Error", "Invalid JSON format: Expected a list but found a dictionary.")
    except FileNotFoundError:
        messagebox.showerror("File Error", f"programs.json not found at {PROGRAMS_FILE_PATH}. Creating a default configuration.")
        programs.append([{
            "stage": 1, "cycles": 3, "maxPressure": 0.2, "resetPressure": 0.16,
            "pressureTime": 180, "breakUpRotations": 3
        }])
    except json.JSONDecodeError as e:
        messagebox.showerror("File Error", f"programs.json is corrupted or improperly formatted: {e}")
    except Exception as e:
        messagebox.showerror("File Error", f"Unexpected error loading programs.json: {e}")

def save_programs():
    try:
        with open(PROGRAMS_FILE_PATH, "w") as f:
            json.dump(programs, f, indent=4)
            print("Successfully saved programs.json")
    except Exception as e:
        messagebox.showerror("File Error", f"Error saving programs.json: {e}")

def open_program_editor(root):
    global cycles_entries, maxPressure_entries, resetPressure_entries, pressureTime_entries, breakUpRotations_entries

    program_names = {0: "White", 1: "Red", 2: "Custom"}

    def get_selected_program_index():
        return list(program_names.keys())[list(program_names.values()).index(program_var.get())]

    def load_program():
        selected_program = get_selected_program_index()

        for widget in editor.winfo_children():
            if isinstance(widget, tk.Entry) or isinstance(widget, tk.Label):
                widget.destroy()

        column_titles = ["Stage", "Cycles", "Max Pressure", "Reset Pressure", "Pressure Time", "Break Up Rotations"]
        for col, title in enumerate(column_titles):
            tk.Label(editor, text=title, font=("Arial", 10, "bold")).grid(row=1, column=col)

        cycles_entries.clear()
        maxPressure_entries.clear()
        resetPressure_entries.clear()
        pressureTime_entries.clear()
        breakUpRotations_entries.clear()

        for i, stage in enumerate(programs[selected_program]):
            tk.Label(editor, text=f"Stage {i+1}").grid(row=i+2, column=0)

            def create_entry(value, row, column):
                entry = tk.Entry(editor)
                entry.insert(0, value)
                entry.grid(row=row, column=column)
                if TOUCHSCREEN_ENABLED:
                    entry.bind("<Button-1>", lambda e, widget=entry: open_keypad(editor, widget))
                return entry

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

            cycles_entries.append(create_entry(stage.get("cycles", ""), i+2, 1))
            maxPressure_entries.append(create_entry(stage.get("maxPressure", ""), i+2, 2))
            resetPressure_entries.append(create_entry(stage.get("resetPressure", ""), i+2, 3))
            pressureTime_entries.append(create_entry(stage.get("pressureTime", ""), i+2, 4))
            breakUpRotations_entries.append(create_entry(stage.get("breakUpRotations", ""), i+2, 5))

    def add_stage():
        selected_program = get_selected_program_index()
        programs[selected_program].append({
            "stage": len(programs[selected_program]) + 1,
            "cycles": 0, "maxPressure": 0.0, "resetPressure": 0.0,
            "pressureTime": 0, "breakUpRotations": 0
        })
        load_program()

    def remove_stage():
        selected_program = get_selected_program_index()
        if programs[selected_program]:
            programs[selected_program].pop()
        load_program()

    def save_changes():
        try:
            selected_program = get_selected_program_index()
            programs[selected_program] = []
            for i in range(len(cycles_entries)):
                new_stage = {
                    "stage": i + 1,
                    "cycles": int(cycles_entries[i].get()),
                    "maxPressure": float(maxPressure_entries[i].get()),
                    "resetPressure": float(resetPressure_entries[i].get()),
                    "pressureTime": int(pressureTime_entries[i].get()),
                    "breakUpRotations": int(breakUpRotations_entries[i].get())
                }
                programs[selected_program].append(new_stage)

            save_programs()
            root.attributes("-topmost", True)
            messagebox.showinfo("Success", "Program updated successfully!")
            editor.destroy()
            root.attributes("-topmost", False)
        except ValueError:
            root.attributes("-topmost", True)
            messagebox.showerror("Error", "Please enter valid numbers.")
            root.attributes("-topmost", False)

    editor = tk.Toplevel(root)
    screen_width = editor.winfo_screenwidth()
    screen_height = editor.winfo_screenheight()
    x = (screen_width // 2) - (950 // 2)
    y = (screen_height // 2) - (300 // 2)
    editor.title("Program Editor")
    editor.geometry(f"950x300+{x}+{y}")

    tk.Label(editor, text="Select Program: ").grid(row=0, column=0)
    program_var = tk.StringVar(editor)
    program_var.set("White")

    program_dropdown = tk.OptionMenu(editor, program_var, *program_names.values(), command=lambda _: load_program())
    program_dropdown.grid(row=0, column=3)

    tk.Button(editor, text="Add Stage", command=add_stage).grid(row=12, column=1)
    tk.Button(editor, text="Remove Stage", command=remove_stage).grid(row=12, column=2)
    tk.Button(editor, text="Save", command=save_changes).grid(row=12, column=4)

    cycles_entries = []
    maxPressure_entries = []
    resetPressure_entries = []
    pressureTime_entries = []
    breakUpRotations_entries = []

    load_program()

# Automatically load on import
load_programs()