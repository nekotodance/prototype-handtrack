import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"    #logicoolのWEBカメラの起動が遅い問題対応
import math
import cv2
import mediapipe as mp
import subfunc

#----------------------------------------
# !!! Setup for the webcam to be used !!!
#----------------------------------------
# Device ID: Also assigned to virtual cameras and other devices, so please try in order from 0
# デバイスID: 仮想カメラなどにも割り振られるので、0から順番に試してください
WEBCUM_DEVICE_ID = 0        # 0, 1, ...
# Video size: 1920,1080 for FullHD, 1280,720 for HD, etc., depending on the webcam used.
# 映像幅: FullHDなら1920,1080、HDなら1280,720など利用するWebカメラに合わせてください
WEBCUM_WIDTH = 1920
WEBCUM_HEIGHT = 1080
# Frame rate: 60fps, 30fps, 24fps, etc., depending on the webcam used
# フレームレート: 60fps、30fps、24fpsなど利用するWebカメラに合わせてください
WEBCUM_FPS = 30

#----------------------------------------
# sub function
#----------------------------------------
def point_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return (int)(distance)

def point_center(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    pointret = (x1+x2)/2, (y1+y2)/2
    return pointret

def point_to_string(point):
    x, y = point
    sret = str((int)(x)) + ", " + str((int)(y))
    return sret

pointline = []  #線を引くためのバッファ
def pbuf_apend_point(point):
    pointline.append(point)

def pbuf_get_point(num):
    return pointline[num]

hisc = 3    #過去n回分のポイントをマージ
def pbuf_get_his(num):
    mnum = 0    #マージ個数
    rpos = (0,0)
    #return pointline[num]
    for i in range (num-hisc+1, num):
        if num < 0: continue
        if pointline[i][0] == 0 or pointline[i][1] == 0: continue
        rpos = (rpos[0] + pointline[i][0], rpos[1] + pointline[i][1])
        mnum += 1
    if mnum > 0:
        rpos = (rpos[0] / mnum, rpos[1] / mnum)
    return rpos

def pbuf_count():
    return len(pointline)

def pbuf_clear():
    pointline.clear()

subfunc.dbgprint("prg start.")
#----------------------------------------
# variable
#----------------------------------------
isDrawHands = 1         # Hand tracking information display
isDrawFace = 2          # Face tracking information display
isReverse = True        # reverse video
isDrawWebCam = False    # Camera image on/off
fing0 = (0, 0)  # wrist 手首
fingA = (0, 0)  # Tip of thumb 親指の先端
finga = (0, 0)  # First joint of thumb 親指の第一関節
fingB = (0, 0)  # Tip of index finger 人差し指の先端
fingC = (0, 0)  # Tip of middle finger 中指の先端
fingD = (0, 0)  # Tip of ring finger 薬指の先端
fingE = (0, 0)  # Tip of pinky finger 小指の先端

isclick = False
isclickold = False

subfunc.dbgprint("cv video init.")
#----------------------------------------
# init
#----------------------------------------
cap = cv2.VideoCapture(WEBCUM_DEVICE_ID)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WEBCUM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WEBCUM_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, WEBCUM_FPS)

subfunc.dbgprint("media pipe init.")
mp_draw = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1,refine_landmarks=True,min_detection_confidence=0.5,min_tracking_confidence=0.5)

#resizable window
#cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

subfunc.dbgprint("LOOP start.")
#----------------------------------------
# loop
#----------------------------------------
while True:
    _, img = cap.read()
    tick = cv2.getTickCount()

    if isReverse:
        img = cv2.flip(img, 1)

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    res_hand = hands.process(imgRGB)
    res_face = face_mesh.process(imgRGB)

    if not isDrawWebCam:
        iw = (int)(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        ih = (int)(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cv2.rectangle(img, (0,0), (iw,ih), (20, 20, 20), cv2.FILLED)

    linex = 10
    liney = 20
    lineyofs = 12

    # draw hands
    if res_hand.multi_hand_landmarks:
        for hand_landmarks in res_hand.multi_hand_landmarks:
            for i, lm in enumerate(hand_landmarks.landmark):
                height, width, channel = img.shape
                cx, cy = int(lm.x * width), int(lm.y * height)
                if isDrawHands > 1:
                    cv2.putText(img, str(i), (cx+20, cy+10), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                    cv2.circle(img, (cx, cy), 8, (0, 0, 200), 1)
                #finger position
                if i == 0: fing0 = (cx, cy)     # wrist 手首
                if i == 4: fingA = (cx, cy)     # Tip of thumb 親指の先端
                if i == 3: finga = (cx, cy)     # First joint of thumb 親指の第一関節
                if i == 8: fingB = (cx, cy)     # Tip of index finger 人差し指の先端
                if i == 12: fingC = (cx, cy)    # Tip of middle finger 中指の先端
                if i == 16: fingD = (cx, cy)    # Tip of ring finger 薬指の先端
                if i == 20: fingE = (cx, cy)    # Tip of pinky finger 小指の先端
            if isDrawHands > 0:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Calculate the greater distance between the wrist and thumb or middle finger
            # 手首と親指か中指の距離の大きい方を算出
            pdis0 = point_distance(fing0, fingA)    # Distance between wrist and thumb 手首と親指の距離
            pdis1 = point_distance(fing0, fingC)    # Distance between wrist and middle finger手首と中指の距離
            pdisTh0 = point_distance(fingA, finga)  # Distance between the tip of the thumb and the first joint 親指の先と第一関節の距離
            if (pdis0 < pdis1):
                pdis0 = pdis1
            # Distance between thumb and index finger
            # 親指と人差指の距離
            pdisAB = point_distance(fingA, fingB)
            pdisTh1 = (pdis0 / 8)

            # Distance between thumb and pinky finger
            # 親指と小指の距離
            pdisAE = point_distance(fingA, fingE)

            isclickold = isclick
            # Thumb and index finger click judgment
            # 親指と人差指のクリック判定
            isclick = (pdisAB < pdisTh1) or (pdisAB < pdisTh0)
            # Thumb and pinky click judgment
            # 親指と小指のクリック判定
            isclear = (pdisAE < pdisTh1) or (pdisAE < pdisTh0)

            # Show the midpoint between thumb and index finger
            # 親指と人差指の中間点を表示
            pcenter = point_center(fingA, fingB)
            if isclick:
                cv2.circle(img, ((int)(pcenter[0]), (int)(pcenter[1])), 5, (0, 255, 128), 5)
            else:
                cv2.circle(img, ((int)(pcenter[0]), (int)(pcenter[1])), 5, (0, 255, 128), 2)
            cv2.putText(img, point_to_string(pcenter) + " dis:" + str(pdisAB) + " th0:" + str(pdisTh0) + " th1:" + str(pdisTh1),
                        (linex, liney), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
            liney += lineyofs*2

            # Drawing the line being clicked
            # クリック中のラインを描画
            if isclick and (isclickold == False):
                pbuf_apend_point((0, 0))
            if isclick:
                cv2.putText(img, "click! : " + str(pbuf_count()), (linex, liney), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                pbuf_apend_point(pcenter)
            if isclear:
                pbuf_clear()
            liney += lineyofs

    # draw face
    if res_face.multi_face_landmarks:
      for face_landmarks in res_face.multi_face_landmarks:
        if isDrawFace > 2:
            mp_draw.draw_landmarks(
                image=img,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_tesselation_style())
        if isDrawFace > 1:
            mp_draw.draw_landmarks(
                image=img,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_contours_style())
        if isDrawFace > 0:
            mp_draw.draw_landmarks(
                image=img,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_iris_connections_style())

    # draw fps
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - tick)
    cv2.putText( img, "FPS: " + str(int(fps)), (img.shape[1] - 80, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0),1)

    # draw line
    if pbuf_count() > 0:
        slog = ""
        lposbase = pbuf_get_point(0)
        lpos = lposbase
        #for lpos in pointline:
        for i in range(1, pbuf_count()):
            lposbase = lpos
            lpos = pbuf_get_point(i)
            if (lposbase[0] != 0 and lposbase[1] != 0 and lpos[0] != 0 and lpos[1] != 0):
                lpos = pbuf_get_his(i)
                cv2.line(img, ((int)(lposbase[0]), (int)(lposbase[1])),
                            ((int)(lpos[0]), (int)(lpos[1])), (0, 255, 128), thickness=2)
    liney += lineyofs

    cv2.imshow("Image", img)

    # key check
    key = cv2.waitKey(1)
    prop_val = cv2.getWindowProperty('Image', cv2.WND_PROP_ASPECT_RATIO)
    if key != -1:
        subfunc.dbgprint(f"key pushed. keyid : {key}")
    if key == 27:       # esc
        break
    if key == 113:      # q
        break
    if prop_val < 0: break  # close button
    if key == 114:      # r
        isReverse = not isReverse
    if key == 104:      # h
        isDrawHands += 1
        if isDrawHands > 2: isDrawHands = 0
    if key == 102:      # f
        isDrawFace += 1
        if isDrawFace > 3: isDrawFace = 0
    if key == 99:       # c
        isDrawWebCam = not isDrawWebCam

cap.release()
subfunc.dbgprint("LOOP end.")
