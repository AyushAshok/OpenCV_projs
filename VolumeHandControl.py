import cv2
import numpy as np
import time
import warnings
import os
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume



warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf.symbol_database')
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

cap=cv2.VideoCapture(0)
pTime=0
detector=htm.handDetector(detectionCon=0.7)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange=volume.GetVolumeRange()
minVol=volRange[0]
maxVol=volRange[1]
vol=0
volBar=400
volPer=0


while True:
    success, img=cap.read()
    img=detector.findHands(img)
    lmList=detector.findPosition(img,draw=False)
    if(len(lmList)!=0):

        x1,y1=lmList[4][1],lmList[4][2]
        x2,y2=lmList[8][1],lmList[8][2]
        cx,cy=(x1+x2)//2,(y1+y2)//2
        length=math.hypot(x2-x1,y2-y1)

        cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
        cv2.circle(img,(x2,y2),15,(255,0,255),cv2.FILLED)
        if(length<30):
            cv2.circle(img,(cx,cy),15,(255,255,0),cv2.FILLED)
        elif(length>240):
            cv2.circle(img,(cx,cy),15,(0,0,255),cv2.FILLED)
        else:
            cv2.circle(img,(cx,cy),15,(255,0,120),cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3)


        length=math.hypot(x2-x1,y2-y1)

        vol=np.interp(length,[30,240],[minVol,maxVol])
        volBar=np.interp(length,[30,240],[400,150])
        volPer=np.interp(length,[30,240],[0,100])
        volume.SetMasterVolumeLevel(vol, None)
        print(f'Setting volume to: {vol} (percent: {volPer})')



    cv2.rectangle(img,(50,150),(85,400),(255,0,0),3)
    cv2.rectangle(img,(50,int(volBar)),(85,400),(0,255,255),cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 0), 3)
    cv2.putText(img, f'{int(volPer)}%', (40,450), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255,0,0), 3)

    cv2.imshow("Image",img)
    if cv2.waitKey(1) & 0xFF==ord('q'):
        break

cap.release()
cv2.destroyAllWindows()