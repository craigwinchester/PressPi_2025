# controller.py
import asyncio
import RPi.GPIO as GPIO
import tkinter as tk
from config import PIN_SPIN_LEFT, PIN_SPIN_RIGHT, PIN_INFLATE, PIN_DEFLATE
from utils import printBox
from main import asyncio_loop

# Track all running tasks that can be cancelled
running_tasks = set()

def run_async_task(coro_func):
    try:
        asyncio.run_coroutine_threadsafe(coro_func(), asyncio_loop)
    except Exception as e:
        printBox(f"[run_async_task error] {e}")

async def run_spin_to_location(loc, label):
    from press_logic import spin_to_location
    printBox("run_spin_to_location")
    await spin_to_location(loc, label)
    

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

async def deflate_to_bar(target_bar, get_current_bar):
    from press_logic import Pressure
    task = asyncio.current_task()
    running_tasks.add(task)
    try:
        elapsed = await Pressure.deflateToBar(target_bar, get_current_bar)
        if elapsed is not None:
            printBox(f"✅ Reached {target_bar:.2f} BAR in {elapsed:.2f} seconds")
        else:
            printBox("⚠️ Deflation was interrupted")
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
    tk.messagebox.showwarning(title = "!", message = "Clear Emergency")

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
