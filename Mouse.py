import cv2
import numpy as np
import Mouse_HandTracking as th
import time
import autopy
import pyautogui
import mouse

########### Variables ###############
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7  # Can set any value according to the functionality.
#####################################

### For Smoothening ###
pTime = 0
plocX, plocY = 0, 0  # Previous Location of X and Y
clocX, clocY = 0, 0  # Current Location of X and Y

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = th.HandDetector()

wScr, hScr = autopy.screen.size()
# print(wScr, hScr) #To get screen size

while True:

    # Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # print(lmList)

    # Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        # print(x1, y1, x2, y2)

        # Check which fingers are up
        fingers = detector.fingersUp()
        # print(fingers)

        # For frame reduction
        cv2.rectangle(img, pt1=(frameR, frameR), pt2=(wCam - frameR, hCam - frameR), color=(0, 255, 255),
                      thickness=2)

        # Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. Convert Coordinates [coordinate theory refer ppt]
            '''x3 = np.interp(x1, (0, wCam), (0, wScr))
            y3 = np.interp(y1, (0, hCam), (0, hScr))'''
            ### But the mouse does not reach at the top corners and extreme parts of the screen. Hence,
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # Smoothen Values (We can multiply smpthening value and include decimal no's or else divide and use whole no's)
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # Move Mouse
            # autopy.mouse.move(x3, y3)  #issue of opposite left and right movement
            # autopy.mouse.move(wScr - x3, y3) #need smoothening
            autopy.mouse.move(wScr - clocX, clocY)

            # The circle shows that we are in moving mode
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            # Need smoothening
            plocX, plocY = clocX, clocY

        # Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:

            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12,
                                                          img)  # lineInfo - used to add clicking circle in the center (refering findDidtance in Mouse_HandTracking.py)
            # print(length)     #To set the min distance

            # Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                           15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()  # To actually click (Left click)

            # For right click
            if fingers[3] == 1 and length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                           15, (0, 255, 0), cv2.FILLED)
                mouse.click('right')  # To actually click (Left click)

        # Scroll up  and Down
        if fingers[4] == 1 and fingers[0] == 1:
            pyautogui.scroll(50)
        elif fingers[4] == 1 and fingers[0] == 0:
            pyautogui.scroll(-50)

    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)

    # 12.   Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)
