import cv2
import mediapipe as mp
import numpy as np 
import time
import statistics as st
import os
#from calculateSD import calculateSD #does not work on macOS

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_drawing_styles = mp.solutions.drawing_styles
mp_drawing = mp.solutions.drawing_utils

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

cap = cv2.VideoCapture(0)
thresholdSleepy = 3 
thresholdMSleepy = 2
thresholdUnresponsive = 3
currentWindowS = 0
currentWindowU = 0
totalTime = 0

while cap.isOpened():
    success, image = cap.read()
    
    if currentWindowS == 0:
        start = time.time()
    if currentWindowU == 0:
        startU = time.time()

    # Flip the image horizontally for a later selfie-view display
    # Also convert the color space from BGR to RGB
    if image is None:
        break
        #continue
    else:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # To improve performace
    image.flags.writeable = False
    
    # Get the result
    results = face_mesh.process(image)

    # To improve performance
    image.flags.writeable = True

    # Convert the color space from RGB to BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    img_h, img_w, img_c = image.shape

    # Left eye indices list
    #LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
    # Right eye indices list
    #RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]
    #LEFT_IRIS = [473, 474, 475, 476, 477]
    #RIGHT_IRIS = [468, 469, 470, 471, 472]
    LEFT_POS_INT = [386, 374]
    RIGHT_POS_INT = [159,145]

    left_eye_pos = []
    right_eye_pos = []
    closed = False
    responsive = False

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):

                if idx in LEFT_POS_INT:
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 0, 255), thickness=-1)
                    left_eye_pos.append( int(lm.y * img_h))
                

                if idx in RIGHT_POS_INT:
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 255, 0), thickness=-1)
                    right_eye_pos.append( int(lm.y * img_h))
                
                if idx == 4:
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(255, 0, 0), thickness=-1)
                    responsive = True
		

        #condizione di chiusura occhio
        if left_eye_pos and right_eye_pos:
            left_eye = np.array(left_eye_pos)
            right_eye = np.array(right_eye_pos)

            distance_left = np.linalg.norm(left_eye[0] - left_eye[1])
            distance_right = np.linalg.norm(right_eye[0] - right_eye[1])
            cv2.putText(image, "Distance left: " + str(distance_left), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(image, "Distance right: " + str(distance_right), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


            if distance_left < 15 and distance_right < 15:
                closed = True
                currentWindowS = time.time() - start
            elif currentWindowS > 0 :
                closed = False
                currentWindowS = 0
                end = time.time()
                totalTime = end-start

       

        
        cv2.putText(image, "Current Window: " + str(currentWindowS), (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(image, "Last Total Time: " + str(totalTime), (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(image, "Current Window Unresponsive Driver: " + str(currentWindowU), (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if currentWindowS > thresholdMSleepy and currentWindowS < thresholdSleepy:  
            cv2.putText(image, "MicroSleepy", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif currentWindowS > thresholdSleepy:  
            cv2.putText(image, "Sleepy", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif currentWindowS > 6:
            cv2.putText(image, "Unresponsive Driver", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if responsive == False:
            currentWindowU = time.time() - startU
    else:
            currentWindowU = 0
    if currentWindowU > thresholdUnresponsive:
        cv2.putText(image, "Unresponsive Driver", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('output window', image)       

    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()
