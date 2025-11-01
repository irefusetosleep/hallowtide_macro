import pyautogui
import pydirectinput as pd
import cv2 as cv
from screeninfo import get_monitors
import numpy as np
from time import sleep

screen_size = (0, 0)

for m in get_monitors():
    if m.is_primary == True: # if you want this to be your second monitor change "True" to "False"
        screen_size = (m.width, m.height)

def check_hunger(): #check alt accounts hunger since it cant regain from carnivore
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
        if __name__ != "__main__":
            pd.click(int(screen_size[0] * .67), int(screen_size[1] * 0.50))
            sleep(.1)
        pd.press("1")
        sleep(1)
        pd.click()
        sleep(1)
        pd.press("2")
        sleep(1)
        pd.press("3")
        sleep(1)
        pd.click()


if __name__ == "__main__":   
    template = cv.imread("joy.png")

    if template.shape[-1] == 4:
        template = cv.cvtColor(template, cv.COLOR_BGRA2GRAY)
    else:
        template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)

    h, w = template.shape

    pd.PAUSE = 0.001

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

        return found

    while True:
        sleep(.1)
        finished = check_for_finished()
            
        print(f"Finished: {finished}")
        if finished:
            for i in range(5):
                pd.click()
                sleep(0.02)
            check_hunger()


