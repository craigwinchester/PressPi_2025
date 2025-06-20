import asyncio
import RPi.GPIO as GPIO
import time
import tkinter as tk
from program_editor import programs
from controller import inflate_to_bar, deflate_to_bar, run_spin_to_location, run_async_task
from press_logic import Spin, spin_to_location, hold_pressure, breakup_rotations
from config import SPIN_ROTATION, FULL_DEFLATE, TELEGRAM_MESSAGING, SMS_MESSAGING, EMAIL_MESSAGING
from gui import printBox
from drum_position_editor import positions
import status
from sms_alerts import load_contacts, send_sms, get_contact_by_name, send_telegram_message, send_email_message, get_email_contact_by_name
from utils import convertTime

topTime = positions["drum_positions"]["fill_position_seconds"]
drainTime = positions["drum_positions"]["drain_position_seconds"]
bottomTime = positions["drum_positions"]["door_down_position_seconds"]
cam_hold_time = positions.get("cam_hold_time", 1.0)

if SMS_MESSAGING:
    contacts = load_contacts()
else:
    print("No SMS messaging")

async def run_program(name, program_data):
    
    tk.messagebox.showwarning(title = "!", message = "Door Closed?")
    tk.messagebox.showwarning(title = "!", message = "Valve Closed?")
    
    printBox(f"Running Program: {name}")
    status.current_program_data = name
    
    start_time = time.time()
    
    status.current_action = "Spinning to Drain location" 
    await spin_to_location(drainTime, "drain") 

    status.total_stage_data = len(program_data)

    for stage_len in range(len(program_data)):
        printBox(f"STAGE - {stage_len + 1}")
        status.current_stage_data = stage_len + 1
        status.total_cycle_data = program_data[stage_len]["cycles"]   
        for cycle_len in range(program_data[stage_len]["cycles"]):
            printBox(f"----Cycle: {cycle_len + 1} - ")
            status.current_cycle_data = cycle_len + 1
            max_pressure = program_data[stage_len]["maxPressure"]
            reset_pressure = program_data[stage_len]["resetPressure"]
            pressure_time = program_data[stage_len]["pressureTime"]
            num_rotations = program_data[stage_len]["breakUpRotations"]
            status.current_action = "Inflating"   
            await inflate_to_bar(max_pressure, status.pressure_data)
            await asyncio.sleep(2) 
            status.current_action = (f"Holding at pressure: {max_pressure}")  
            await hold_pressure(max_pressure, reset_pressure, pressure_time)
            await asyncio.sleep(2) 
            status.current_action = "deflating"   
            await deflate_to_bar(FULL_DEFLATE, status.pressure_data)
            await asyncio.sleep(2) 
            status.current_action = (f"Breakup Rotations: {num_rotations}"  )
            await breakup_rotations(num_rotations)
           
            printBox(f"Cycle {cycle_len + 1} finished")
        printBox(f"Stage {stage_len + 1} finished")
    
    await asyncio.sleep(2) 
    await run_spin_to_location(topTime, "top")
    printBox(f"Program {name} finished")
    
    total_time = time.time() - start_time
    converted_time = convertTime(total_time)

    status.current_action = (f"Program Finished. Elapsed Time: {converted_time}")
    printBox(f"Elapsed Time: {converted_time}")

    #send SMS/Telegram
    if SMS_MESSAGING:
        contact = get_contact_by_name("Craig")
        send_sms(contact, f"Press program {name} completed. \nElapsed time: {converted_time}")
    else:
        print ("No SMS")

    if TELEGRAM_MESSAGING:
        send_telegram_message(f"🍷 Press program {name} complete! \nElapsed Time: {converted_time}")
    else:
        print ("No Telegram")     
   
    if EMAIL_MESSAGING:
        contact = get_email_contact_by_name("Craig")
        send_email_message(contact, f"🍷 Press program {name} complete! \nElapsed Time: {converted_time}" )
    else:
        print ("No Email")

    return

   
