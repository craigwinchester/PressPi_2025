import asyncio
import RPi.GPIO as GPIO
import time
import hardware
import tkinter as tk
from program_editor import programs
from controller import inflate_to_bar, deflate_to_bar, run_spin_to_location, run_async_task
from press_logic import Spin, spin_to_location
from config import SPIN_ROTATION
from gui import printBox
#from button_control import set_program_buttons_enabled
from drum_position_editor import positions

topTime = positions["drum_positions"]["fill_position_seconds"]
drainTime = positions["drum_positions"]["drain_position_seconds"]
bottomTime = positions["drum_positions"]["door_down_position_seconds"]
cam_hold_time = positions.get("cam_hold_time", 1.0)

async def breakup_rotations(n):
    hardware.rotation_count = 0
    GPIO.output(SPIN_ROTATION, GPIO.LOW)
    printBox(f"ðŸ” Rotating for {n} bumps...")

    while hardware.rotation_count() < n:
        await asyncio.sleep(0.1)

    GPIO.output(SPIN_ROTATION, GPIO.HIGH)
    await asyncio.sleep(1)  # brief pause

async def run_program(name, program_data):
    #turn off all buttons except emergency here
    #set_program_buttons_enabled(False)
    
    tk.messagebox.showwarning(title = "!", message = "Door Closed?")
    tk.messagebox.showwarning(title = "!", message = "Valve Closed?")
    
    printBox(f"Running Program: {name}")
    
    start_time = time.time()
    
    #move to drain position
    await spin_to_location(drainTime, "drain")
    
    
    for stage_len in range(len(program_data)):
        printBox(f"STAGE - {stage_len + 1}")
        for cycle_len in range(program_data[stage_len]["cycles"]):
            printBox(f"----Cycle: {cycle_len + 1} - ")
            max_pressure = program_data[stage_len]["maxPressure"]
            reset_pressure = program_data[stage_len]["resetPressure"]
            pressure_time = program_data[stage_len]["pressureTime"]
            num_rotations = program_data[stage_len]["breakUpRotations"]
            #Inflate to max_pressure
            #Hold at max_pressure for pressure_time. Repressurize if below reset_pressure
            #need to create hold_pressure(max_pressure, reset_pressure, pressure_time)
            #deflate_to_pressure(zero) after pressure_time has elapsed
            #breakup_rotations(num_rotations)
            printBox(f"Cycle {cycle_len + 1} finished")
        printBox(f"Stage {stage_len + 1} finished")
    printBox(f"Program {name} finished")
    await run_spin_to_location(topTime, "top")
    total_time = time.time() - start_time
    printBox(f"Elapsed Time: {total_time}")
    #set_program_buttons_enabled(True)
         
    return
   
