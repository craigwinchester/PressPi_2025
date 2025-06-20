# gui.py
import tkinter as tk
from tkinter import scrolledtext as ScrolledText
from tkinter import Button as TkButton
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import animation
import threading
import atexit
import RPi.GPIO as GPIO
import asyncio
from asyncio import new_event_loop, set_event_loop, run_coroutine_threadsafe
from program_editor import open_program_editor, programs
from drum_position_editor import open_positions_editor
from config import SERIAL_PORT, SERIAL_BAUDRATE, PIN_SPIN_LEFT, PIN_SPIN_RIGHT, PIN_INFLATE, PIN_DEFLATE, MAX_PRESSURE, TOUCHSCREEN_ENABLED
from press_logic import Spin, Pressure, spin_to_location
from hardware import cleanup_gpio, pressure_updater
from utils import set_text_box, set_root_window, printBox, set_control_buttons
from controller import inflate_to_bar, connect_emergency_button, run_spin_left, run_spin_right, run_pressure_deflate, run_pressure_inflate, run_async_task, run_spin_to_location
from drum_position_editor import positions
from program import run_program
import status
from web_server import shutdown_flask
from touchscreen_keypad import NumericKeypad
import time
 
# --- ASYNCIO SETUP ---
asyncio_loop = new_event_loop()
def start_async_loop():
    set_event_loop(asyncio_loop)
    asyncio_loop.run_forever()

threading.Thread(target=start_async_loop, daemon=True).start()

topTime = positions["drum_positions"]["fill_position_seconds"]
drainTime = positions["drum_positions"]["drain_position_seconds"]
bottomTime = positions["drum_positions"]["door_down_position_seconds"]
cam_hold_time = positions.get("cam_hold_time", 1.0)

pinList = [PIN_SPIN_LEFT, PIN_SPIN_RIGHT] + PIN_INFLATE + PIN_DEFLATE

def shutdown_relays():
    try:
        for pin in pinList:
            GPIO.output(pin, GPIO.HIGH)
        print("All Relays turned off")
        cleanup_gpio()
    except RuntimeError as e:
        print(f"[Shutdown skipped] {e}")

def on_closing():
    shutdown_relays()
    root.destroy()

atexit.register(shutdown_relays)
atexit.register(shutdown_flask)

bar_gauge = None

Button_pressure = None
Button_vacuum = None
Button_left = None
Button_right = None
Button_top = None
Button_drain = None
Button_bottom = None
Button_setToBar = None
Button_programOne = None
Button_programTwo = None
Button_programThree = None
Button_editor = None

button_original_colors = {}

emergency_active = False

def any_gpio_active():
    try:
        if GPIO.input(PIN_SPIN_LEFT) == GPIO.LOW: return True
        if GPIO.input(PIN_SPIN_RIGHT) == GPIO.LOW: return True
        if any(GPIO.input(pin) == GPIO.LOW for pin in PIN_INFLATE): return True
        if any(GPIO.input(pin) == GPIO.LOW for pin in PIN_DEFLATE): return True
    except Exception as e:
        printBox(f"[any_gpio_active error] {e}")
    return False

def refresh_button_colors_from_gpio():
    global emergency_active
    try:
        active_any = any_gpio_active()
        set_to_bar_disabled = active_any or emergency_active
        for btn, pin, is_multi in [
            (Button_left, PIN_SPIN_LEFT, False),
            (Button_right, PIN_SPIN_RIGHT, False),
            (Button_pressure, PIN_INFLATE, True),
            (Button_vacuum, PIN_DEFLATE, True)
        ]:
            active = any(GPIO.input(p) == GPIO.LOW for p in pin) if is_multi else GPIO.input(pin) == GPIO.LOW
            if active:
                btn.config(fg="red")
            elif active_any or emergency_active:
                btn.config(fg="gray")
                btn.config(state=tk.DISABLED)
                Button_top.config(state=tk.DISABLED)
                Button_drain.config(state=tk.DISABLED)
                Button_bottom.config(state=tk.DISABLED)
                Button_programOne.config(state=tk.DISABLED)
                Button_programTwo.config(state=tk.DISABLED)
                Button_programThree.config(state=tk.DISABLED)
            else:
                btn.config(fg="black")
                btn.config(state=tk.NORMAL)
                Button_top.config(state=tk.NORMAL)
                Button_drain.config(state=tk.NORMAL)
                Button_bottom.config(state=tk.NORMAL)
                Button_programOne.config(state=tk.NORMAL)
                Button_programTwo.config(state=tk.NORMAL)
                Button_programThree.config(state=tk.NORMAL)
        if Button_setToBar:
            Button_setToBar.config(state=tk.DISABLED if set_to_bar_disabled else tk.NORMAL)
    except Exception as e:
        printBox(f"[GPIO color check error] {e}")

def button_color_poll_loop():
    refresh_button_colors_from_gpio()
    root.after(300, button_color_poll_loop)

def update_gauge():
    try:
        bar_gauge.config(text=f"{status.pressure_data:.2f} BAR")
    except Exception as e:
        printBox(f"[update_gauge error] {e}")
    root.after(250, update_gauge)

def button_settobar():
    try:
        target = float(Entry_bar.get())
        if not(0.0 < target <= MAX_PRESSURE):
            printBox(f"❌ BAR must be between 0.0 and {MAX_PRESSURE}")
            return
        printBox(f"▶️ Starting async inflate to {target} BAR")
        run_async_task(lambda: inflate_to_bar(target, lambda: status.pressure_data))
    except ValueError:
        printBox("❌ Invalid BAR entry.")

def update_clock():
    current_time = time.strftime("%H:%M:%S")
    clock_label.config(text=current_time)
    root.after(1000, update_clock)


root = tk.Tk()
root.title("Wine Press 2025")
root.geometry("1280x720")
root.configure(bg="SteelBlue3")

Button_left = tk.Button(root, text='<-Left', height=2, width=16, bg="light slate gray",
                        command=lambda: run_async_task(run_spin_left))
Button_left.grid(row=1, column=0, padx=25, pady=10)

Button_right = tk.Button(root, text='Right->', height=2, width=16, bg="light slate gray",
                         command=lambda: run_async_task(run_spin_right))
Button_right.grid(row=2, column=0, padx=25, pady=10)

Button_top = tk.Button(
    root,
    text='Top',
    height=2,
    width=16,
    bg="light slate gray",
    command=lambda: run_async_task(lambda: run_spin_to_location(topTime, "top"))
)
Button_top.grid(row=0, column=1, padx=25, pady=10)

Button_drain = tk.Button(
    root,
    text='Drain',
    height=2,
    width=16,
    bg="light slate gray",
    command=lambda: run_async_task(lambda: run_spin_to_location(drainTime, "drain"))
)
Button_drain.grid(row=1, column=1, padx=25, pady=10)

Button_bottom = tk.Button(
    root,
    text='Bottom',
    height=2,
    width=16,
    bg="light slate gray",
    command=lambda: run_async_task(lambda: run_spin_to_location(bottomTime, "bottom"))
)
Button_bottom.grid(row=2, column=1, padx=25, pady=10)

Entry_bar = tk.Spinbox(root, from_=0.0, to=MAX_PRESSURE, increment=0.1, format="%.1f", width=4)
Entry_bar.grid(row=0, column=2)

if TOUCHSCREEN_ENABLED:
    def open_keypad(e, widget=Entry_bar):
        original_bg = widget.cget("background")
        try:
            widget.configure(background="yellow")
        except tk.TclError:
            pass
        def restore():
            try:
                widget.configure(background=original_bg)
            except tk.TclError:
                pass
        NumericKeypad(root, widget, on_close=restore)

    Entry_bar.bind("<Button-1>", open_keypad)

Button_setToBar = tk.Button(root, text='Set To BAR', height=2, width=16, bg="light slate gray",
                             command=lambda: button_settobar())
Button_setToBar.grid(row=1, column=2, padx=25, pady=10)

Button_vacuum = tk.Button(
    root,
    text='Vacuum',
    height=2,
    width=16,
    bg="light slate gray",
    command=lambda: run_async_task(run_pressure_deflate)  
)
Button_vacuum.grid(row=2, column=2, padx=25, pady=10)

Button_pressure = tk.Button(
    root,
    text='Pressure',
    height=2,
    width=16,
    bg="light slate gray",
    command=lambda: run_async_task(run_pressure_inflate)  
)
Button_pressure.grid(row=3, column=2, padx=25, pady=10)

Button_emergency = tk.Button(root, text='EMERGENCY STOP!', height=2, width=42,
                              bg="#d81125", activebackground="#ededed",
                              command=lambda: emergencyStop())
Button_emergency.grid(row=3, column=0, columnspan=2, padx=25, pady=10)
connect_emergency_button(Button_emergency)

# Button for White Program
Button_programOne = tk.Button()
Button_programOne.grid(row=0, column=3, padx=(25, 25), pady=(10, 10))
Button_programOne.configure(bg="light slate gray")
Button_programOne.configure(
    text='''White''',
    height="2", width="16",
    command=lambda: asyncio.run_coroutine_threadsafe(run_program("White", programs[1]), asyncio_loop)
)

# Button for Red Program
Button_programTwo = tk.Button()
Button_programTwo.grid(row=1, column=3, padx=(25, 25), pady=(10, 10))
Button_programTwo.configure(bg="light slate gray")
Button_programTwo.configure(
    text='''Red''',
    height="2", width="16",
    command=lambda: asyncio.run_coroutine_threadsafe(run_program("Red", programs[1]), asyncio_loop)
)

# Button for Custom Program
Button_programThree = tk.Button()
Button_programThree.grid(row=2, column=3, padx=(25, 25), pady=(10, 10))
Button_programThree.configure(bg="light slate gray")
Button_programThree.configure(
    text='''Custom''',
    height="2", width="16",
    command=lambda: asyncio.run_coroutine_threadsafe(run_program("Custom", programs[2]), asyncio_loop)
)

Button_editor = tk.Button(root, text='Editor', height=2, width=16, bg="light slate gray",
                           command=lambda: open_program_editor(root))
Button_editor.grid(row=3, column=3, padx=25, pady=10)

bar_gauge = tk.Label(root,
                     text="0.00 BAR",
                     font=("ds-digital", 52, "bold"),  # if not insatlled use ("Courier", 52, "bold")
                     bg="black",
                     fg="lime green",
                     width=10,
                     height=1,
                     relief="ridge",
                     bd=10,
                     anchor="center")
bar_gauge.grid(row=4, column=0, columnspan=2, pady=20)

clock_label = tk.Label(root, font=("ds-digital", 24, "bold"), bg="SteelBlue3")
clock_label.place(x=620, y=340)


text_box = ScrolledText.ScrolledText(root, background="#000000", foreground="#08ff31",
                                     wrap="word", height=8, width=42)
text_box.grid(row=4, column=2, columnspan=2, pady=10)
text_box.insert(tk.INSERT, "Lo-Fi Wines - Wine Press 2025\n")

set_root_window(root)
set_text_box(text_box)

lbl = tk.Label(root, bg="SteelBlue3")
lbl.grid(row=0, column=0)

gear_button = TkButton(root, text="⚙️", font=("Arial", 12), command=lambda: open_positions_editor(root))
gear_button.place(relx=0.02, rely=0.02, anchor="nw")

style.use('dark_background')

x_len = 1000
y_range = [-0.5, 2]
fig = Figure()
ax = fig.add_subplot(1, 1, 1)
ax.grid(linestyle='-', linewidth='0.5', color='gray')
ax.set_title("BAR / time")
xs = list(range(0, 1000))
ys = [0] * x_len
ax.set_ylim(y_range)
line, = ax.plot(xs, ys)

def animate(i):
    ys.append(status.pressure_data)
    del ys[0]
    line.set_ydata(ys)
    return line,

canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().configure(height=200, width=1300)
canvas.get_tk_widget().grid(row=5, column=0, columnspan=4)

set_control_buttons([
    Button_left, Button_right, Button_top, Button_drain, Button_bottom,
    Button_setToBar, Button_vacuum, Button_pressure,
    Button_programOne, Button_programTwo, Button_programThree
])

root.protocol("WM_DELETE_WINDOW", on_closing)

def start_main_gui_logic():
    global ani
    threading.Thread(target=pressure_updater, daemon=True).start()
    print("starting main gui logic")
    ani = animation.FuncAnimation(fig, animate, interval=250, blit=True)
    update_gauge()

update_clock()

root.after(100, start_main_gui_logic)
root.after(200, button_color_poll_loop)
root.mainloop()
