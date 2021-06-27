import cv2
import mediapipe as mp
import numpy as np
import json
import pyautogui

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils
onButton = False
displayButtons = False
programButtons = False
buttonCoord = []
countOnButton = 0
buttonNum = []
data = {}
availableKeys = ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
'8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
'browserback', 'browserfavorites', 'browserforward', 'browserhome',
'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen',
'command', 'option', 'optionleft', 'optionright']


def declareMacros(buttonCoord, data):
    for i in range(1, len(buttonCoord) + 1):
        command = []
        raw = input('Input keys for button {}: '.format(str(i)))
        # add spaces between each input
        # use () to indicate hold, [] to let go
        # eg. (ctrl) c [ctrl] is the function to paste
        keystrokes = raw.split()
        for key in keystrokes:
            if key[0] == '(':
                parsed = key[key.find("(") + 1:key.find(")")]
                if parsed in availableKeys:
                    print("held key:", parsed)
                    command.append("pyautogui.keyDown('{}')".format(parsed))
                else:
                    print("no valid key inputted")
            elif key[0] == '[':
                parsed = key[key.find("[") + 1:key.find("]")]
                if parsed in availableKeys:
                    print("released key:", parsed)
                    command.append("pyautogui.keyUp('{}')".format(parsed))
                else:
                    print("no valid key inputted")
            else:
                if key in availableKeys:
                    print("pressed key:", key)
                    command.append("pyautogui.press('{}')".format(key))
                else:
                    print("no valid key inputted")
        data.update({str(i): command})

        with open('macros.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def runMacros(buttonNum, data):
    for command in data[str(buttonNum)]:
        exec(command)

def getContours(img, imgContour, coord):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4:
                cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
                x, y, w, h = cv2.boundingRect(approx)
                coord.append([x, y, x + w, y + h])

def findButtonID(btn, buttonNum):
    buttonNum.clear()
    buttonNum.append(btn)

def checkIfIn(cX1, cY1, coord, buttonNum):
    for pt in coord:
        if pt[0] < cX1 < pt[2] and pt[1] < cY1 < pt[3]:
            btn = coord.index(pt) + 1
            findButtonID(btn, buttonNum)
            return True

def drawButtons(coord):
    for pt in coord:
        cv2.rectangle(img, (pt[0], pt[1]), (pt[2], pt[3]), (0, 255, 0), 5)
        cv2.putText(img, 'Button' + str(coord.index(pt) + 1), (pt[0], pt[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


while cap.isOpened():
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    lmList = []
    if displayButtons:
        drawButtons(buttonCoord)
    if programButtons:
        reset = input('Do you want to reprogram buttons? y/n: ')
        if reset == "y":
            declareMacros(buttonCoord, data)
            programButtons = False
        else:
            with open('macros.json') as f:
                data = json.load(f)
            print("Proceeding with previous JSON config")
            programButtons = False

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id, cx, cy])
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            if lmList[8][1] < lmList[12][1]:
                cX1 = lmList[8][1]
                cY1 = lmList[8][2]
                cv2.circle(img, (cX1, cY1), 25, (255, 0, 255), cv2.FILLED)
                onButton = checkIfIn(cX1, cY1, buttonCoord, buttonNum)
                if onButton:
                    if countOnButton == 0:
                        runMacros(buttonNum[0], data)
                        print("pressed", buttonNum[0])
                        onButton = False
                        countOnButton = 25
                    else:
                        onButton = True
                        countOnButton -= 1
                else:
                    onButton = False
                    countOnButton = 3

    cv2.imshow("Image", img)
    k = cv2.waitKey(20) & 0xFF
    if k == 27:
        cap.release()
        cv2.destroyAllWindows()
        break
    elif k == ord('c'):
        buttonCoord = []
        imgContour = img.copy()
        imgBlur = cv2.GaussianBlur(img, (7, 7), 1)
        imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
        threshold1 = 241
        threshold2 = 73
        imgCanny = cv2.Canny(imgGray, threshold1, threshold2)
        kernel = np.ones((5, 5))
        imgDil = cv2.dilate(imgCanny, kernel, iterations=1)
        getContours(imgDil, imgContour, buttonCoord)
        displayButtons = True
        programButtons = True

