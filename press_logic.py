# press_logic.py

import asyncio
import RPi.GPIO as GPIO
from hardware import setup_gpio
from config import PIN_SPIN_LEFT, PIN_SPIN_RIGHT, PIN_INFLATE, PIN_DEFLATE
from utils import printBox
from controller import running_tasks

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
        printBox(f"[controller] ✅ coroutine started: target = {target_bar}")
        
        task = asyncio.current_task()
        running_tasks.add(task)
        pressure_flag = 1
        start_time = asyncio.get_event_loop().time()

        try:
            while True:
                current_bar = get_current_bar()

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

