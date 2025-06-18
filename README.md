# 🍇 PressPi: Automated Wine Press Control System 🍇 

PressPi is a Python-based automation system designed to control a pneumatic wine press using a Raspberry Pi, Arduino (or ESP32), and a set of relays, sensors, and GUI components. It’s built to support both manual and automated pressing cycles with safety features like emergency stop and pressure monitoring.

What started as a pandemic side project to pass the time has recently been completely rewritten, with a help from ChatGPT. I’ll admit it: I’m not a programmer... I’m a winemaker.

I haven’t connected the system to the actual wine press yet — but that’s coming soon. If you’re reading this and have experience with motor controllers and wiring, get in touch. I could use some help in that department. Will pay in wine!

---

## Features

- Full GUI built with Tkinter
- Fully editable press cycle programs.   
- Real-time pressure monitoring via ADS1115 & pressure transducer
- Drum position control using bump-detection and timed rotation
- Emergency stop support (software + physical button)  
    > ⚠️ *Still under development – not yet fully functional!*
- Async control loop using `asyncio`
- Web interface (Flask-based) for remote monitoring (optional)

---

## Hardware Requirements

- An old wine press! 
        Mine is a 1993 Velo 2100 Liter. We will reuse all it's old motor starters, etc...
- Raspberry Pi (tested with a 4 Model B)
- Arduino Uno or ESP32 (tested with ESP32-S3)  
    > Currently using Arduino for better stability
- ADS1115 analog-to-digital converter
- Pressure transducer (0–30 PSI)  
    > 3-wire, 1/8" NPT  
    > Add 0.1 µF and 10 µF ceramic capacitors to filter noise  
    > Use push-connect pneumatic fittings (6mm)
- Relay board (to control valves, pump, etc. 8 channel)
- OLED screen (optional, 0.96" I2C for local BAR Pressure display)
- Touchscreen (Im using a 7 inch)
- "Bump detector" button for drum position reference. 
    > I'm reusing the original roller plunger limit switch from the press. 
    > Also using a small momentary switch and a resistor for testing with the breadboard.
- 3D-printed mounts and enclosures (see `3d_prints/` directory)  
    > More designs coming soon
- Wires 
- breadboard for testing purposes
- a large Syringe (at least 50ml) plus small hoses to connect to the pressure transducer, for testing.

---

## Software Stack

- Python 3.x
- Tkinter
- `pyserial` for serial comms
- `aiofiles`, `asyncio` for async control loop
- Arduino/ESP32 sketch to handle sensor readings & display
- Flask web server for remote monitoring

---

## Development Tools

- VS Code (Python)
- Arduino IDE
- VNC Viewer (for remote Pi access)
- WinSCP or other FTP client
- MU or Thonny on the Pi

---

## System Diagram

*Coming soon – this will show how the Pi, Arduino, sensors, and relays are all connected.*


