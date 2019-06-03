import ctypes
import random
import time
import sys


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

keystrokes = 0
mouse_clicks = 0
double_clicks = 0

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint),
                ("dwTime", ctypes.c_ulong)
                ]
    def get_last_input(self):

        struct_lastinputinfo = LASTINPUTINFO()
        struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)

        # get the last input registered
        user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))

        # now determine how long the machine has been running
        run_time = kernel32.GetTickCount()

        elapsed = run_time - struct_lastinputinfo.dwTime

        print("[*] It's been %d milliseconds since the last input event." % elapsed)

        return elapsed


# Test Code remove after this paragraph!
while True:
    get_lastinput()
    time.sleep(1)
    