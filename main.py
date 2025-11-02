import subprocess
import platform
import sys
import shutil

def ensure_packages():
    to_ensure = {"pydirectinput", "screeninfo", "keyboard", "opencv-python", "cv2", "pyautogui", "numpy", "Pillow"}
    
    for package in to_ensure:
        try:
            __import__(package)
            print(f"{package} already installed!")
        except ImportError:
            print(f"[INFO] Installing missing depenency: {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])

ensure_packages()

def check_compiler(compiler_name: str) -> bool:
    """Check if a compiler is available on PATH."""
    path = shutil.which(compiler_name)
    if path:
        print(f"[OK] Found {compiler_name} at {path}")
        return True
    else:
        print(f"[MISSING] {compiler_name} not found.")
        return False

def ensure_compilers():
    system = platform.system().lower()

    gcc_installed = check_compiler("gcc")
    clang_installed = check_compiler("clang")

    # Windows
    if system == "windows":
        if not gcc_installed:
            print("[INFO] Installing MinGW (GCC)...")
            os.system("winget install -e --id=GnuWin32.Mingw")
        if not clang_installed:
            print("[INFO] Installing LLVM/Clang...")
            os.system("winget install -e --id=LLVM.LLVM")

    # macOS
    elif system == "darwin":
        if not gcc_installed or not clang_installed:
            print("[INFO] Installing Xcode Command Line Tools...")
            os.system("xcode-select --install")

    else:
        print("[WARN] Unsupported OS for auto-install.")

ensure_compilers()

import pydirectinput as pd
from screeninfo import get_monitors
from time import sleep, time
from keyboard import is_pressed
import cv2 as cv
import pyautogui
import numpy as np
import threading
import tkinter as tk
from auto_hunger import check_hunger, resource_path
import os
import sys

joy_gained = 0
start_time = time()


def run_overlay():
    global joy_label, time_label

    root = tk.Tk()
    root.title("Macro Stats")
    root.attributes("-topmost", True)
    root.overrideredirect(True)  # removes title bar
    root.configure(bg="#111111")

    # make resizable manually
    root.geometry("200x70+50+50")
    root.minsize(180, 60)
    
    drag_data = {"x": 0, "y": 0}

    # enable dragging
    def start_drag(event):
        drag_data["x"] = event.x
        drag_data["y"] = event.y

    def drag_motion(event):
        dx = event.x - drag_data["x"]
        dy = event.y - drag_data["y"]
        geom = root.geometry()
        geom = geom.split('+')[1:]
        x, y = int(geom[0]), int(geom[1])
        root.geometry(f"+{x + dx}+{y + dy}")

    root.bind("<Button-1>", start_drag)
    root.bind("<B1-Motion>", drag_motion)

    # labels
    joy_label = tk.Label(root, text="Joy gained: 0", fg="white", bg="#111111", font=("Consolas", 12, "bold"))
    joy_label.pack(anchor="w", padx=10, pady=(10, 0))

    time_label = tk.Label(root, text="Runtime: 0s", fg="gray", bg="#111111", font=("Consolas", 11))
    time_label.pack(anchor="w", padx=10, pady=(0, 10))

    # periodic update
    def update_time():
        elapsed = int(time() - start_time)
        time_label.config(text=f"Runtime: {elapsed // 60}m {elapsed % 60}s")
        root.after(1000, update_time)

    update_time()
    root.mainloop()

def update_joy_overlay():
    global joy_gained
    joy_gained += 37
    if joy_label:
        joy_label.config(text=f"Joy gained: {joy_gained}")

# Run overlay in its own thread so it doesn’t block the macro
threading.Thread(target=run_overlay, daemon=True).start()

template = cv.imread(resource_path("joy.png"))

if template.shape[-1] == 4:
    template = cv.cvtColor(template, cv.COLOR_BGRA2GRAY)
else:
    template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)

h, w = template.shape
pd.PAUSE = 0.001

screen_size = (0, 0)
for m in get_monitors():
    if m.is_primary:
        screen_size = (m.width, m.height)

infected_template = cv.imread(resource_path("curse.png"), cv.IMREAD_GRAYSCALE)

stop_key = "h"

def start_trial():
    pd.click(int(screen_size[0] * .67), int(screen_size[1] * 0.50))
    pd.press("e")
    start_time = time()
    max_time = 30
    infected = False

    while True:
        if is_pressed(stop_key):
            quit()
        if infected or time() - start_time > max_time:
            break

        sleep(.01)
        ss = pyautogui.screenshot()
        ss = cv.cvtColor(np.array(ss), cv.COLOR_RGB2BGR)
        ss = cv.cvtColor(ss, cv.COLOR_BGR2GRAY)

        result = cv.matchTemplate(ss, infected_template, cv.TM_CCOEFF_NORMED)
        thresh = 0.85
        loc = np.where(result >= thresh)
        
        found = False
        for pt in zip(*loc[::-1]):
            print("Alt account infected!")
            found = True

        if found:
            sleep(1)
            infected = True
            pd.click(int(screen_size[0] * .67), int(screen_size[1] * 0.50))
            sleep(.3)
            pd.press("shift")
            pd.press("7")
            sleep(0.4)
            x, y = pd.position()
            drag_step = 1
            for i in range(3000): # spins around to hit any lingering gourdskippers
                if is_pressed(stop_key):
                    quit()
                x += drag_step
                pd.moveTo(x, y)
                pd.click()
            
            sleep(.4)
            pd.press("7")
            pd.press("shift")
            break

    sleep(.2)
    pd.click(int(screen_size[0] * 0.23), int(screen_size[1] * 0.57))

def check_for_finished():

    screenshot = pyautogui.screenshot()
    screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)

    result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    thresh = 0.83
    loc = np.where(result >= thresh)

    found = False
    for pt in zip(*loc[::-1]):
        print(f"Found at: {pt}")
        found = True

    if found:
        update_joy_overlay()

    return found

move_range = 100
increment = 5

def autoclick():
    x = 0
    direction = 1
    while True:
        if is_pressed(stop_key):
            quit()
        pd.click()
        pd.moveRel(increment * direction, 0)
        x += increment * direction

        if abs(x) >= move_range:
            direction *= -1
            x = 0
        
        sleep(0.05)
        finished = check_for_finished()
        if finished:
            break

def main():
    sleep(4)
    start_trial()
    sleep(1)
    autoclick()
    check_hunger()
    sleep(61)
    main()

main()

