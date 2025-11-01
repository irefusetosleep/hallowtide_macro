import pyautogui
import pydirectinput as pd
import cv2 as cv
from screeninfo import get_monitors
import numpy as np
from time import sleep

screen_size = (0, 0)

for m in get_monitors():
    if m.is_primary == True:
        screen_size = (m.width, m.height)


def check_hunger(): #check alt accounts hunger since it cant regain from carnivore
    #yeah im ngl fuck allat image recognition ima just hardcode this

    thirst_bar_height = int((screen_size[1] * 0.199))
    thirst_bar_width = int((screen_size[0]/2) * 0.006)
    thirst_bar_region = (screen_size[0] * 0.52, screen_size[1] - thirst_bar_height)
    screenshot = pyautogui.screenshot(imageFilename="Alt_Screenshot.png", region=(
        int(thirst_bar_region[0]), #left
        int(thirst_bar_region[1] * 0.904), #top
        thirst_bar_width, # width
        thirst_bar_height)) # height

    frame = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)

    lower = np.array([85,30,40])
    upper = np.array([130,255,255]) #upper and lower blue for pixel counting

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, lower, upper)

    blue_pixels = cv.countNonZero(mask)
    total = thirst_bar_width * thirst_bar_height
    fill_ratio = blue_pixels / total

    print(f"Thirst bar about: {fill_ratio * 100:.1f}% full!")

    if fill_ratio < 0.3:
        pd.press("1")
        sleep(1)
        pd.click()
        sleep(1)
        pd.press("2")
        sleep(1)
        pd.press("3")
        sleep(1)
        pd.click()

while True:
    sleep(1)
    check_hunger()


