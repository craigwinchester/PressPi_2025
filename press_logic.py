# press_logic.py

import asyncio
import RPi.GPIO as GPIO
import threading
from hardware import setup_gpio
import hardware
from config import PIN_SPIN_LEFT, PIN_SPIN_RIGHT, PIN_INFLATE, PIN_DEFLATE, SPIN_ROTATION
from utils import printBox
from controller import running_tasks
import pressure
import time

# System flags
spinning_flag = 0
pressure_flag = 0
program_flag = 0
emerg_flag = 0

setup_gpio()

class Spin:
    async def left():
        task = asyncio.current_task()
        running_tasks.add(task)
        global spinning_flag, pressure_flag, program_flag
        try:
            if pressure_flag == 0 and program_flag == 0:
                if GPIO.input(PIN_SPIN_RIGHT):
                    if GPIO.input(PIN_SPIN_LEFT):
                        printBox("Turning Left")
                        GPIO.output(PIN_SPIN_LEFT, GPIO.LOW)
                        spinning_flag = 1
                        while not task.cancelled():  # Keep spinning until cancelled
                            await asyncio.sleep(0.1)
                    else:
                        printBox("Stop Turning Left")
                        GPIO.output(PIN_SPIN_LEFT, GPIO.HIGH)
                        spinning_flag = 0
            else:
                printBox("ERROR: Can't spin while adjusting pressure!")
        finally:
            GPIO.output(PIN_SPIN_LEFT, GPIO.HIGH)
            spinning_flag = 0
            running_tasks.discard(task)

    async def right():
        task = asyncio.current_task()
        running_tasks.add(task)
        global spinning_flag, pressure_flag, program_flag
        try:
            if pressure_flag == 0 and program_flag == 0:
                if GPIO.input(PIN_SPIN_LEFT):
                    if GPIO.input(PIN_SPIN_RIGHT):
                        printBox("Turning Right")
                        GPIO.output(PIN_SPIN_RIGHT, GPIO.LOW)
                        spinning_flag = 1
                        while not task.cancelled():  # Keep spinning until cancelled
                            await asyncio.sleep(0.1)
                    else:
                        printBox("Stop Turning Right")
                        GPIO.output(PIN_SPIN_RIGHT, GPIO.HIGH)
                        spinning_flag = 0
            else:
                ("ERROR: Can't spin while adjusting pressure!")
        finally:
            GPIO.output(PIN_SPIN_RIGHT, GPIO.HIGH)
            spinning_flag = 0
            running_tasks.discard(task)


class Pressure:
    async def inflate():
        global spinning_flag, pressure_flag, program_flag
        task = asyncio.current_task()
        running_tasks.add(task)
        try:
            if spinning_flag == 0 and pressure_flag != 2 and program_flag == 0:
                if all(GPIO.input(pin) for pin in PIN_INFLATE):
                    pressure_flag = 1
                    printBox("Pressure On")
                    for pin in PIN_INFLATE:
                        GPIO.output(pin, GPIO.LOW)
                    for pin in PIN_DEFLATE:
                        GPIO.output(pin, GPIO.HIGH)
                    while not task.cancelled():
                        await asyncio.sleep(0.1)  # Keeps task alive
                else:
                    pressure_flag = 0
                    printBox("Pressure Off")
                    for pin in PIN_INFLATE:
                        GPIO.output(pin, GPIO.HIGH)
            else:
                printBox("ERROR: Can't inflate while spinning or changing pressure")
        finally:
            pressure_flag = 0
            for pin in PIN_INFLATE:
                GPIO.output(pin, GPIO.HIGH)
            running_tasks.discard(task)
            #printBox("Inflate task cleaned up")

    async def deflate():
        global spinning_flag, pressure_flag, program_flag
        task = asyncio.current_task()
        running_tasks.add(task)
        try:
            if spinning_flag == 0 and pressure_flag != 1 and program_flag == 0:
                if all(GPIO.input(pin) for pin in PIN_DEFLATE):
                    pressure_flag = 2
                    printBox("Vacuum On")
                    for pin in PIN_INFLATE:
                        GPIO.output(pin, GPIO.HIGH)
                    for pin in PIN_DEFLATE:
                        GPIO.output(pin, GPIO.LOW)
                    while not task.cancelled():
                        await asyncio.sleep(0.1)
                else:
                    pressure_flag = 0
                    printBox("Vacuum Off")
                    for pin in PIN_DEFLATE:
                        GPIO.output(pin, GPIO.HIGH)
            else:
                printBox("ERROR: Can't deflate while spinning or changing pressure")
        finally:
            pressure_flag = 0
            for pin in PIN_DEFLATE:
                GPIO.output(pin, GPIO.HIGH)
            running_tasks.discard(task)
            #printBox("Deflate task cleaned up")

    @staticmethod
    async def inflateToBar(target_bar, get_current_bar):
        global pressure_flag, emerg_flag
        printBox(f"target = {target_bar}")
        
        task = asyncio.current_task()
        running_tasks.add(task)
        pressure_flag = 1
        start_time = asyncio.get_event_loop().time()

        try:
            while True:
                current_bar = pressure.pressure_data
                if emerg_flag == 1 or task.cancelled():
                    printBox("Emergency detected. Cancelling inflation.")
                    break
                if current_bar >= target_bar:
                    break
                for pin in PIN_INFLATE:
                    GPIO.output(pin, GPIO.LOW)
                await asyncio.sleep(1)
        finally:
            for pin in PIN_INFLATE:
                GPIO.output(pin, GPIO.HIGH)
            pressure_flag = 0
            running_tasks.discard(task)
        if emerg_flag == 1 or task.cancelled():
            return None
        elapsed_time = asyncio.get_event_loop().time() - start_time
        return elapsed_time
    
    @staticmethod
    async def deflateToBar(target_bar, get_current_bar):
        global pressure_flag, emerg_flag
        printBox(f"Deflating to: {target_bar}")
        
        task = asyncio.current_task()
        running_tasks.add(task)
        pressure_flag = 1
        start_time = asyncio.get_event_loop().time()

        try:
            while True:
                current_bar = pressure.pressure_data
                if emerg_flag == 1 or task.cancelled():
                    printBox("Emergency detected. Cancelling inflation.")
                    break
                if current_bar <= target_bar:
                    break
                for pin in PIN_DEFLATE:
                    GPIO.output(pin, GPIO.LOW)
                await asyncio.sleep(1)
        finally:
            for pin in PIN_DEFLATE:
                GPIO.output(pin, GPIO.HIGH)
            pressure_flag = 0
            running_tasks.discard(task)
        if emerg_flag == 1 or task.cancelled():
            return None
        elapsed_time = asyncio.get_event_loop().time() - start_time
        return elapsed_time



async def spin_to_location(loc, label):
    printBox(f"spin_to_location - {label}, time: {loc}")
    global spinning_flag, pressure_flag, program_flag
    
    spinning_flag = 1
    GPIO.output(SPIN_ROTATION, GPIO.LOW)
    printBox("Waiting for bump to start timing")

    # Reset rotation count to 0 and wait for it to reach 1
    hardware.rotationCount = 0
    while hardware.rotationCount < 1:
        #printBox(f"rotation count: {hardware.rotationCount}")
        await asyncio.sleep(0.01)

    printBox(f"Bump detected - spinning for {loc:.2f} seconds")

    task = asyncio.current_task()
    running_tasks.add(task)
    try:
        await asyncio.sleep(loc)
    except asyncio.CancelledError:
        printBox(f"spin_to_location ({label}) cancelled")
    finally:
        GPIO.output(SPIN_ROTATION, GPIO.HIGH)
        hardware.rotationCount = 0
        spinning_flag = 0
        running_tasks.discard(task)
        printBox(f"Arrived at {label}")

async def hold_pressure(max_pressure, reset_pressure, pressure_time):
    printBox(f"⏱ Holding pressure at {max_pressure:.2f} BAR for {pressure_time:.1f} sec (reset if < {reset_pressure:.2f})")
    start_time = time.time()
    try:
        while time.time() - start_time < pressure_time:
            current_bar = pressure.pressure_data
            printBox(f"🔍 Current BAR: {current_bar:.2f}")
            if current_bar < reset_pressure:
                printBox(f"⚠️ Pressure dropped to {current_bar:.2f} — re-inflating to {max_pressure:.2f}")
                await Pressure.inflateToBar(max_pressure, pressure.pressure_data)
            await asyncio.sleep(0.5)
        printBox("hold pressure time reached.")
    except asyncio.CancelledError:
        printBox("⛔ hold_pressure cancelled")   

async def breakup_rotations(n):
    hardware.rotationCount = 0
    GPIO.output(SPIN_ROTATION, GPIO.LOW)
    printBox(f"BREAKUP ROTATIONS x {n}")
    while True:
        if hardware.rotationCount >= n:
            await asyncio.sleep(1)  # brief pause
            GPIO.output(SPIN_ROTATION, GPIO.HIGH)
            break
