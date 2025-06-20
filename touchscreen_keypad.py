# touchscreen_keypad.py

import tkinter as tk

class NumericKeypad(tk.Toplevel):
    def safe_grab_set(self):
        try:
            self.grab_set()
        except tk.TclError:
            self.after(100, self.safe_grab_set)
    def __init__(self, master, target_widget, on_close=None):
        super().__init__(master)
        self.target_widget = target_widget
        self.on_close = on_close
        self.input_value = tk.StringVar()
        self.configure(bg="black")
        self.title("Enter Number")
        self.geometry("300x400+0+0")

        display = tk.Entry(self, textvariable=self.input_value, font=("Courier", 24), justify="right")
        display.pack(fill="x", padx=10, pady=10)

        button_grid = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', '←'],
            ['Clear', 'OK']
        ]

        for row_values in button_grid:
            row_frame = tk.Frame(self, bg="black")
            row_frame.pack(expand=True, fill="both")
            for value in row_values:
                btn = tk.Button(
                    row_frame, text=value, font=("Courier", 20),
                    height=2, width=4,
                    command=lambda v=value: self.handle_input(v)
                )
                btn.pack(side="left", expand=True, fill="both", padx=2, pady=2)

        # Delay grab_set until window is visible
        self.after(100, self.safe_grab_set)
        self.transient(master)
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def handle_input(self, label):
        if label == '←':  # Backspace
            self.input_value.set(self.input_value.get()[:-1])
        elif label == 'Clear':
            self.input_value.set("")
        elif label == 'OK':
            self.target_widget.delete(0, tk.END)
            self.target_widget.insert(0, self.input_value.get())
            if self.on_close:
                self.on_close()
            self.destroy()
        else:
            self.input_value.set(self.input_value.get() + label)

    def on_closing(self):
        if self.on_close:
            self.on_close()
        self.destroy()