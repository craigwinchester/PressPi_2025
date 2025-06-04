import asyncio
import RPi.GPIO as GPIO
import time
import tkinter as tk
from program_editor import programs
from controller import inflate_to_bar, deflate_to_bar, run_spin_to_location, run_async_task
from press_logic import Spin, spin_to_location, hold_pressure, breakup_rotations
from config import SPIN_ROTATION, FULL_DEFLATE
from gui import printBox
from drum_position_editor import positions
import pressure
from sms_alerts import load_contacts, send_sms, get_contact_by_name

topTime = positions["drum_positions"]["fill_position_seconds"]
drainTime = positions["drum_positions"]["drain_position_seconds"]
bottomTime = positions["drum_positions"]["door_down_position_seconds"]
cam_hold_time = positions.get("cam_hold_time", 1.0)

contacts = load_contacts()

async def run_program(name, program_data):
    
    tk.messagebox.showwarning(title = "!", message = "Door Closed?")
    tk.messagebox.showwarning(title = "!", message = "Valve Closed?")
    
    printBox(f"Running Program: {name}")
    
    start_time = time.time()
    
    await spin_to_location(drainTime, "drain") 
        
    for stage_len in range(len(program_data)):
        printBox(f"STAGE - {stage_len + 1}")
        for cycle_len in range(program_data[stage_len]["cycles"]):
            printBox(f"----Cycle: {cycle_len + 1} - ")
            max_pressure = program_data[stage_len]["maxPressure"]
            reset_pressure = program_data[stage_len]["resetPressure"]
            pressure_time = program_data[stage_len]["pressureTime"]
            num_rotations = program_data[stage_len]["breakUpRotations"]
               
            await inflate_to_bar(max_pressure, pressure.pressure_data)
            await asyncio.sleep(2) 
            await hold_pressure(max_pressure, reset_pressure, pressure_time)
            await asyncio.sleep(2) 
            await deflate_to_bar(FULL_DEFLATE, pressure.pressure_data)
            await asyncio.sleep(2) 
            await breakup_rotations(num_rotations)
           
            printBox(f"Cycle {cycle_len + 1} finished")
        printBox(f"Stage {stage_len + 1} finished")
    
    await asyncio.sleep(2) 
    await run_spin_to_location(topTime, "top")
    printBox(f"Program {name} finished")
   
    total_time = time.time() - start_time
    printBox(f"Elapsed Time: {total_time}")

    #send SMS
    contact = get_contact_by_name("Craig")
    send_sms(contact, f"Press program completed. Elapsed time: {total_time}")
             
    return
   
