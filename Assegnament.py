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
    LEFT_POS_INT =[ 133,158,160,33,144,153]
    # Right eye indices list
    RIGHT_POS_INT=[ 362,385,387,263,373,380]

    left_eye_pos_2d = []
    right_eye_pos_2d = []
    

    closed = False
    responsive = False

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):

                if idx == LEFT_POS_INT[0]:
                    left_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 0])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 0, 255), thickness=-1)
                if idx == LEFT_POS_INT[1]:
                    left_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 1])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 0, 255), thickness=-1)
                if idx == LEFT_POS_INT[2]:  
                    left_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 2])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 0, 255), thickness=-1)
                if idx == LEFT_POS_INT[3]:
                    left_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 3])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 0, 255), thickness=-1)
                if idx == LEFT_POS_INT[4]:
                    left_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 4])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 0, 255), thickness=-1)
                if idx == LEFT_POS_INT[5]:
                    left_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 5])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 0, 255), thickness=-1)
                
                if idx == RIGHT_POS_INT[0]:
                    right_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 0])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 255, 0), thickness=-1)
                if idx == RIGHT_POS_INT[1]:         
                    right_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 1])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 255, 0), thickness=-1)
                if idx == RIGHT_POS_INT[2]:
                    right_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 2])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 255, 0), thickness=-1)
                if idx == RIGHT_POS_INT[3]:
                    right_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 3])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 255, 0), thickness=-1)
                if idx == RIGHT_POS_INT[4]:
                    right_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 4])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 255, 0), thickness=-1)
                if idx == RIGHT_POS_INT[5]:
                    right_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h), 5])
                    cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 255, 0), thickness=-1)
    
    
		


    cv2.imshow('output window', image)       

    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()
