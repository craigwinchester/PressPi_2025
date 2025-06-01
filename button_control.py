# button_control.py

def set_program_buttons_enabled(state):
    from gui import (
        Button_top, Button_drain, Button_bottom,
        Button_programOne, Button_programTwo, Button_programThree
    )
    mode = "NORMAL" if state else "DISABLED"
    Button_top.config(state=mode)
    Button_drain.config(state=mode)
    Button_bottom.config(state=mode)
    Button_programOne.config(state=mode)
    Button_programTwo.config(state=mode)
    Button_programThree.config(state=mode)