import subprocess
import platform
import sys
import os
import shutil

to_ensure = {"pydirectinput",
             "screeninfo",
             "keyboard",
             "opencv-python",
             "cv2",
             "pyautogui",
             "numpy",
             "Pillow",
             "os",
             "sys",
             "tkinter"}

def ensure_packages():
    if getattr(sys, "frozen", False) == True: #if we are running from an exe then dont do this
        return
    for package in to_ensure:
        try:
            __import__(package)
            print(f"{package} already installed!")
        except ImportError:
            print(f"[INFO] Installing missing depenency: {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])

ensure_packages()

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
import sys

joy_gained = 0
start_time = time()

macro_running = False  # global flag
def run_overlay():
    global joy_label, time_label, toggle_button, macro_running

    root = tk.Tk()
    root.title("Macro Stats")
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.configure(bg="#111111")
    root.geometry("220x100+50+50")  # leave space for close button
    root.minsize(200, 90)
    
    drag_data = {"x": 0, "y": 0}
    def start_drag(event):
        drag_data["x"] = event.x
        drag_data["y"] = event.y
    def drag_motion(event):
        dx = event.x - drag_data["x"]
        dy = event.y - drag_data["y"]
        geom = root.geometry().split('+')[1:]
        x, y = int(geom[0]), int(geom[1])
        root.geometry(f"+{x + dx}+{y + dy}")
    root.bind("<Button-1>", start_drag)
    root.bind("<B1-Motion>", drag_motion)

    # Labels
    joy_label = tk.Label(root, text="Joy gained: 0", fg="white", bg="#111111", font=("Consolas", 12, "bold"))
    joy_label.pack(anchor="w", padx=10, pady=(10, 0))
    time_label = tk.Label(root, text="Runtime: 0s", fg="gray", bg="#111111", font=("Consolas", 11))
    time_label.pack(anchor="w", padx=10, pady=(0, 10))

    # Start/Stop Button
    def toggle_macro():
        global macro_running
        macro_running = not macro_running
        if macro_running:
            toggle_button.config(text="Stop", bg="red")
        else:
            toggle_button.config(text="Start", bg="green")

    toggle_button = tk.Button(root, text="Start", bg="green", fg="white", font=("Consolas", 12, "bold"),
                              command=toggle_macro)
    toggle_button.pack(pady=(0, 10), fill="x", padx=10)

    # Custom Close Button (Red X)
    def close_overlay():
        print("[INFO] Overlay closed - stopping program")
        root.destroy()
        os._exit(0)

    close_button = tk.Button(root, text="✖", bg="#111111", fg="red", font=("Courier New", 10, "bold"),
                             borderwidth=0, command=close_overlay)
    close_button.place(x=200, y=0)  # top-right corner

    # Periodic time update
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

if template.shape[-1] == 4: #shut up pyright 
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

sword = cv.imread(resource_path("sword.png"), cv.IMREAD_GRAYSCALE)

def find_sword():
    ss = pyautogui.screenshot()
    ss = cv.cvtColor(np.array(ss), cv.COLOR_RGB2BGR)
    ss = cv.cvtColor(ss, cv.COLOR_BGR2GRAY)

    result = cv.matchTemplate(ss, sword, cv.TM_CCOEFF_NORMED)
    thresh = 0.7
    loc = np.where(result >= thresh)

    sword_found = False
    for pt in zip(*loc[::-1]):
        print(f"Sword found {pt}")
        sword_found = True
        for i in range(10):
            pd.click(int(pt[0]), int(pt[1]))
            pd.click(int(pt[0] + 1), int(pt[1] + 10))
    return sword_found

def start_trial():
    global macro_running

    pd.click(int(screen_size[0] * .67), int(screen_size[1] * 0.50))
    pd.press("e")
    start_time = time()
    max_time = 45
    infected = False

    pd.keyDown("i")
    sleep(1)
    pd.keyUp("i") #full zooms in


    x, y = pd.position()
    for i in range(100):
        y -= 1
        pd.moveTo(x, y)

    while True:
        if infected or time() - start_time > max_time:
            break
        if not macro_running or is_pressed(stop_key):
            macro_running = False
            toggle_button.config(text="Start", bg="green")
            return  # exit the function

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
            pd.keyDown("o")
            sleep(1)
            pd.keyUp("o")


            sleep(1)
            infected = True
            pd.click(int(screen_size[0] * .67), int(screen_size[1] * 0.50))
            sleep(.3)
            sword_found = find_sword()
            sleep(.1)
            pd.press("shift")

            if sword_found == False:
                print("Couldnt find sword")
                while True:
                    sleep(1)

            sleep(0.4)
            x, y = pd.position()
            drag_step = 1
            for i in range(3000): # spins around to hit any lingering gourdskippers
                if not macro_running or is_pressed(stop_key):
                    macro_running = False
                    toggle_button.config(text="Start", bg="green")
                    return  # exit the function
                x += drag_step
                y -= drag_step
                pd.moveTo(x, y)
                pd.click()
            
            pd.press("shift")
            sleep(.1)
            sword_found = find_sword()
            if not sword_found:
                print("Couldnt find sword!")
            break

    sleep(.2)
    pd.click(int(screen_size[0] * 0.23), int(screen_size[1] * 0.57))

subsides = cv.imread(resource_path("subsides.png"), cv.IMREAD_GRAYSCALE)

def check_for_finished():
    screenshot = pyautogui.screenshot()
    screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)

    result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    thresh = 0.86
    loc = np.where(result >= thresh)

    found = False
    for pt in zip(*loc[::-1]):
        print(f"Found at: {pt}")
        found = True
    
    if found == False:
        result = cv.matchTemplate(screenshot, subsides, cv.TM_CCOEFF_NORMED)
        thresh = 0.84
        loc = np.where(result >= thresh)

        for pt in zip(*loc[::-1]):
            print(f"Found at {pt}")
            found = True

    if found:
        update_joy_overlay()

    return found

move_range = 100
increment = 5

def autoclick():
    global macro_running

    x = 0
    direction = 1
    while True:
        if not macro_running or is_pressed(stop_key):
            macro_running = False
            toggle_button.config(text="Start", bg="green")
            return  # exit the function
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
    global macro_running
    while True:
        sleep(0.1)
        if is_pressed(stop_key):
            macro_running = False
            toggle_button.config(text="Start", bg="green")

        if not macro_running:
            continue  # wait until macro is started

        sleep(4)
        start_trial()
        sleep(1)
        autoclick()
        check_hunger(side="Left")
        sleep(.4)
        check_hunger(side="Right")
        sleep(58)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("Fatal error:", e)
        traceback.print_exc()
        input("Press Enter to exit...")

