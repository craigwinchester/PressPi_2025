# controller.py
import asyncio
import RPi.GPIO as GPIO
from config import PIN_SPIN_LEFT, PIN_SPIN_RIGHT, PIN_INFLATE, PIN_DEFLATE
from utils import printBox, enable_all_buttons, disable_all_buttons
import tkinter as tk

# Track all running tasks that can be cancelled
running_tasks = set()

def run_async_task(coro):
    try:
        loop = asyncio.get_running_loop()
        task = loop.create_task(coro)
        running_tasks.add(task)
        task.add_done_callback(lambda t: running_tasks.discard(t))
    except RuntimeError:
        printBox("[run_async_task error] No running event loop")

async def run_spin_left():
    from press_logic import Spin
    await Spin.left()

async def run_spin_right():
    from press_logic import Spin
    await Spin.right()

async def run_pressure_inflate():
    from press_logic import Pressure
    await Pressure.inflate()

async def run_pressure_deflate():
    from press_logic import Pressure
    await Pressure.deflate()

async def inflate_to_bar(target_bar, get_current_bar):
    from press_logic import Pressure
    task = asyncio.current_task()
    running_tasks.add(task)
    try:
        elapsed = await Pressure.inflateToBar(target_bar, get_current_bar)
        if elapsed is not None:
            printBox(f"✅ Reached {target_bar:.2f} BAR in {elapsed:.2f} seconds")
        else:
            printBox("⚠️ Inflation was interrupted")
    finally:
        running_tasks.discard(task)

def connect_emergency_button(button):
    import tkinter as tk
    from functools import partial

    def on_emergency_click():
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(emergency_stop())
        except RuntimeError:
            # Fallback if no event loop is running — try to start one manually
            asyncio.run(emergency_stop())

    button.config(command=on_emergency_click, fg="white", bg="red", activebackground="#ededed")

async def emergency_stop():
    printBox("🚨 EMERGENCY STOP ACTIVATED")
    cancel_all_tasks()
    shutdown_all_relays()
    printBox("⚡ All relays OFF. Async tasks cancelled.")
    show_clear_emergency_popup()

def show_clear_emergency_popup():
    popup = tk.Toplevel()
    popup.title("Clear Emergency")
    popup.geometry("300x150")
    popup.configure(bg="red")

    label = tk.Label(popup, text="Emergency Active!", font=("Arial", 14), bg="red", fg="white")
    label.pack(pady=10)

    def clear_emergency():
        enable_all_buttons()  # This function should re-enable all relevant buttons
        popup.destroy()

    clear_button = tk.Button(popup, text="Clear Emergency", command=clear_emergency, font=("Arial", 12), bg="white")
    clear_button.pack(pady=10)

    # Disable all relevant buttons in your GUI
    disable_all_buttons()

def cancel_all_tasks():
    for task in list(running_tasks):
        if not task.done():
            task.cancel()

def shutdown_all_relays():
    try:
        for pin in [PIN_SPIN_LEFT, PIN_SPIN_RIGHT] + PIN_INFLATE + PIN_DEFLATE:
            GPIO.output(pin, GPIO.HIGH)
        #cleanup_gpio()
    except Exception as e:
        printBox(f"[Emergency GPIO Error] {e}")
