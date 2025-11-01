import pydirectinput as pd
from screeninfo import get_monitors
from time import sleep, time
from keyboard import is_pressed
import cv2 as cv
import pyautogui
import numpy as np

template = cv.imread("joy.png")

if template.shape[-1] == 4:
    template = cv.cvtColor(template, cv.COLOR_BGRA2GRAY)
else:
    template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)

h, w = template.shape

pd.PAUSE = 0.001

screen_size = (0, 0)

for m in get_monitors():
    if m.is_primary == True:
        screen_size = (m.width, m.height)

infected_template = cv.imread("curse.png", cv.IMREAD_GRAYSCALE)

def start_trial():
    pd.click(int(screen_size[0] * .67), int(screen_size[1] * 0.50))
    pd.press("e")
        
    start_time = time()
    max_time = 1 * 60 #the longest the program will wait for the alt to get infected
    infected = False

    while True:
        if infected == True or time() - start_time > max_time:
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
            pd.click(int(screen_size[0] * .67), int(screen_size[1] * 0.50)) # clicks on the alt account
            pd.press("7") #pulls out weapon
            sleep(0.4)
            pd.mouseDown() # starts hold swinging
            pd.press("esc") # makes hold swing continue out of tab
            sleep(.3)
            pd.mouseUp()
            sleep(.3)
            pd.press("esc")
            sleep(.3)
            pd.keyDown("right")
            sleep(10)
            pd.keyUp("right")
            pd.click()
            sleep(.4)
            pd.press("7") # puts weapon away to cleanly reset for next run
            break

    sleep(.2)
    pd.click(int(screen_size[0] * 0.25), int(screen_size[1] * 0.585)) # clicks into main account window

def check_for_finished():
    screenshot = pyautogui.screenshot()
    screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)

    result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
    thresh = 0.85
    loc = np.where(result >= thresh)

    found = False
    for pt in zip(*loc[::-1]):
        print(f"Found at: {pt}")
        found = True

    return found




move_range = 100
increment = 5

stop_key = "h"

def autoclick(): #autoclicks but also moves the mouse around to account for skippers getting stuck in the building
    x = 0
    direction = 1 # 1 = right, -1 = left
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

thirst_bar_color = "#76AFBE"
thirst_template = cv.imread("Thirst.png")
thirst_template = cv.cvtColor(thirst_template, cv.COLOR_BGR2GRAY)

thirst_h, thirst_w = thirst_template.shape

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
        pd.click(int(screen_size[0] * .67), int(screen_size[1] * 0.50))
        pd.press("1")
        pd.click()
        sleep(1)
        pd.press("2")
        pd.click()

def main():
    global times_ran

    sleep(4)
    start_trial()

    sleep(1)
    autoclick()
    
    check_hunger()

    sleep(61)
    main()


main()
