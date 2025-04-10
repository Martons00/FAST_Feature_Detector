import cv2
import mediapipe as mp
import numpy as np 
import time
import statistics as st
import asyncio
from telegram.ext import ApplicationBuilder


distraction_start_time = None
alert_sent = False
telegram_alert = True


async def send_alert(message):
    # Crea l'applicazione del bot
    with open("token.txt", "r") as file:
        token = file.readline().strip()
        chat_id = file.readline().strip()


    application = ApplicationBuilder().token(token).build()

    # Invia il messaggio al chat_id specificato
    await application.bot.send_message(chat_id=chat_id, text=message)


def calculateClosedEyeRatio(eye):
    A = np.sqrt(abs(eye[1][0] - eye[5][0])**2 + abs(eye[1][1] - eye[5][1])**2)
    B = np.sqrt(abs(eye[2][0] - eye[4][0])**2 + abs(eye[2][1] - eye[4][1])**2)
    C = np.sqrt(abs(eye[0][0] - eye[3][0])**2 + abs(eye[0][1] - eye[3][1])**2)

    # Calculate the EAR
    ear = (A + B) / (2.0 * C)
    
    return ear 

def calculateEAR(image, left_eye_pos_2d, right_eye_pos_2d,ears):
    ear_sx = calculateClosedEyeRatio(left_eye_pos_2d)
    cv2.putText(image, "EAR SX: {:.2f}".format(ear_sx), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
    ear_dx = calculateClosedEyeRatio(right_eye_pos_2d)
    cv2.putText(image, "EAR DX: {:.2f}".format(ear_dx), (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0,255), 2)
    ear = (ear_sx + ear_dx) / 2.0
    ear = min(ear, 0.34)  
    ear = (ear / 0.34) * 100  

    ears.append(ear)
    if len(ears) > 300:
        ears.pop(0)
    cv2.putText(image, "MEAN EAR : {:.2f} %".format(ear), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return ear_sx, ear_dx, ear

def check_driver_distraction(pitch_left_eye, yaw_left_eye, pitch_right_eye, yaw_right_eye, pitch, yaw, roll, image, img_w):
    """
    Verifica se il conducente è distratto e invia un messaggio solo dopo 5 secondi consecutivi di distrazione.
    """
    global distraction_start_time, alert_sent

    avg_pitch_eyes = (pitch_left_eye + pitch_right_eye) / 2
    avg_yaw_eyes = (yaw_left_eye + yaw_right_eye) / 2

    combined_pitch = pitch + avg_pitch_eyes
    combined_yaw = yaw + avg_yaw_eyes

    is_distracted = abs(combined_pitch) > 30 or abs(combined_yaw) > 30 or abs(roll) > 30

    if is_distracted:
        cv2.putText(image, "Distracted", (int(img_w * 0.5), 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if distraction_start_time is None:
            distraction_start_time = time.time()
            alert_sent = False  # Reset dell'allarme

        distraction_duration = time.time() - distraction_start_time

        if distraction_duration >= 5 and not alert_sent:
            global telegram_alert
            if telegram_alert:
                asyncio.run(send_alert("ATTENZIONE: Il conducente sembra distratto da più di 5 secondi!"))
            alert_sent = True  

        cv2.putText(image, f"Distracted: {int(distraction_duration)}s", (int(img_w * 0.5), 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    else:
        cv2.putText(image, "Not Distracted", (int(img_w * 0.5), 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        distraction_start_time = None
        alert_sent = False




def plotStats(image, ears, statusIn10s, img_w, img_h):

    # Dimensioni del grafico
    graph_width = int(img_w * 0.3)
    graph_height = int(img_h * 0.2)
    graph_x_start = int(img_w - graph_width - (img_h * 0.05))
    graph_y_start = int(img_h * 0.75)

    # Disegna il rettangolo di sfondo per il grafico
    cv2.rectangle(image, (graph_x_start, graph_y_start), 
                  (graph_x_start + graph_width, graph_y_start + graph_height), 
                  (255, 255, 255), -1)

    # Disegna il grafico EAR
    for i in range(1, len(ears)):
        x1 = graph_x_start + int((i - 1) * graph_width / len(ears))
        y1 = graph_y_start + graph_height - int(ears[i - 1] * graph_height / 100)
        x2 = graph_x_start + int(i * graph_width / len(ears))
        y2 = graph_y_start + graph_height - int(ears[i] * graph_height / 100)
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # Disegna le linee di soglia EAR
    threshold_80_y = graph_y_start + graph_height - int(80 * graph_height / 100)
    threshold_20_y = graph_y_start + graph_height - int(20 * graph_height / 100)
    cv2.line(image, (graph_x_start, threshold_80_y), 
             (graph_x_start + graph_width, threshold_80_y), 
             (0, 255, 0), 1)  # Soglia superiore
    cv2.line(image, (graph_x_start, threshold_20_y), 
             (graph_x_start + graph_width, threshold_20_y), 
             (0, 0, 255), 1)  # Soglia inferiore

    # Disegna il grafico dello stato di sonnolenza
    for i in range(1, len(statusIn10s)):
        x1 = graph_x_start + int((i - 1) * graph_width / len(statusIn10s))
        y1 = graph_y_start + int(graph_height * (1 - statusIn10s[i - 1]))
        x2 = graph_x_start + int(i * graph_width / len(statusIn10s))
        y2 = graph_y_start + int(graph_height * (1 - statusIn10s[i]))
        cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # Etichette e titolo del grafico
    cv2.putText(image, "EAR Over Time", 
                (graph_x_start + int(graph_width / 3), graph_y_start - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(image, "Drowsiness Status", 
                (graph_x_start + int(graph_width / 3), 
                 graph_y_start + graph_height + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    

def checkAwake(ear, ears, start, statusIn10s, image, img_w, img_h):
    if ear < 20:
        statusIn10s.append(1)
    else:
        statusIn10s.append(0)
    
    if len(statusIn10s) > 300:
        statusIn10s.pop(0)
    if st.mean(statusIn10s) > 0.8 and len(statusIn10s) > 300:
        cv2.putText(image, "DROWSY", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if telegram_alert:
            asyncio.run(send_alert("ATTENZIONE: Il conducente sembra assonnato!"))
    else:
        cv2.putText(image, "AWAKE", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    plotStats(image, ears, statusIn10s, img_w, img_h)
    cv2.putText(image, "Time: {:.2f}".format(time.time() - start),  (50, 950), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(image, "Mean: {:.2f}".format(st.mean(statusIn10s)), (50, 1000), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

def checkGaze(image, face_pos_2d, face_pos_3d, left_eye_pos_2d, left_eye_pos_3d, right_eye_pos_2d, right_eye_pos_3d):
    # The camera matrix
    focal_length = 1 * img_w
    cam_matrix = np.array([ [focal_length, 0, img_h / 2],
    [0, focal_length, img_w / 2],
    [0, 0, 1]])
    # The distorsion parameters
    dist_matrix = np.zeros((4, 1), dtype=np.float64)
    # Solve PnP
    success, rot_vec, trans_vec = cv2.solvePnP(face_pos_3d, face_pos_2d, cam_matrix, dist_matrix)
    success_left_eye, rot_vec_left_eye, trans_vec_left_eye = cv2.solvePnP(left_eye_pos_3d, left_eye_pos_2d, cam_matrix, dist_matrix)
    success_right_eye, rot_vec_right_eye, trans_vec_right_eye =cv2.solvePnP(right_eye_pos_3d, right_eye_pos_2d, cam_matrix, dist_matrix)
    # Get rotational matrix
    rmat, jac = cv2.Rodrigues(rot_vec)
    rmat_left_eye, jac_left_eye = cv2.Rodrigues(rot_vec_left_eye)
    rmat_right_eye, jac_right_eye = cv2.Rodrigues(rot_vec_right_eye)
    # Get angles
    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
    angles_left_eye, mtxR_left_eye, mtxQ_left_eye, Qx_left_eye, Qy_left_eye, Qz_left_eye = cv2.RQDecomp3x3(rmat_left_eye)
    angles_right_eye, mtxR_right_eye, mtxQ_right_eye, Qx_right_eye, Qy_right_eye, Qz_right_eye = cv2.RQDecomp3x3(rmat_right_eye)
    # Get angles
    pitch = angles[0] * 1800
    yaw = -angles[1] * 1800
    # Define point_RER and point_LEL based on eye landmarks
    point_RER = right_eye_pos_2d[0]  
    point_LEL = left_eye_pos_2d[0]   
    roll = 180 + (np.arctan2(point_RER[1] - point_LEL[1], point_RER[0] - point_LEL[0]) * 180 / np.pi)
    if roll > 180:
        roll = roll - 360
    pitch_left_eye = angles_left_eye[0] * 1800
    yaw_left_eye = angles_left_eye[1] * 1800
    pitch_right_eye = angles_right_eye[0] * 1800
    yaw_right_eye = angles_right_eye[1] * 1800
    nose_3d_projection, jacobian = cv2.projectPoints(nose_pos_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)
    cv2.putText(image, "Roll: {:.2f}".format(roll), (int(img_w * 0.85), 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(image, "Pitch: {:.2f}".format(pitch), (int(img_w * 0.85), 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(image, "Yaw: {:.2f}".format(yaw), (int(img_w * 0.85), 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(image, "Pitch LE: {:.2f}".format(pitch_left_eye), (int(img_w * 0.85), 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(image, "Yaw LE: {:.2f}".format(yaw_left_eye), (int(img_w * 0.85), 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(image, "Pitch RE: {:.2f}".format(pitch_right_eye), (int(img_w * 0.85), 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(image, "Yaw RE: {:.2f}".format(yaw_right_eye), (int(img_w * 0.85), 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return roll, pitch, yaw, pitch_left_eye, yaw_left_eye, pitch_right_eye, yaw_right_eye, nose_3d_projection

def plotDirections(image, nose_pos_2d, pitch, yaw, left_pupil_pos_2d, pitch_left_eye, yaw_left_eye, right_pupil_pos_2d, pitch_right_eye, yaw_right_eye, ear):
    p1 = (int(nose_pos_2d[0]), int(nose_pos_2d[1]))
    p2 = (int(nose_pos_2d[0] + yaw * 10), int(nose_pos_2d[1] - pitch * 10))
    cv2.line(image, p1, p2, (255, 0, 0), 3)
    if ear > 20:
        p3 = (int(left_pupil_pos_2d[0]), int(left_pupil_pos_2d[1]))
        p4 = (int(left_pupil_pos_2d[0] + yaw_left_eye * 10), int(left_pupil_pos_2d[1] - pitch_left_eye * 10))
        cv2.line(image, p3, p4, (255, 0, 0), 3)
        p5 = (int(right_pupil_pos_2d[0]), int(right_pupil_pos_2d[1]))
        p6 = (int(right_pupil_pos_2d[0] + yaw_right_eye * 10), int(right_pupil_pos_2d[1] - pitch_right_eye * 10))
        cv2.line(image, p5, p6, (255, 0, 0), 3)

if __name__ == "__main__":
    FACE_POS_INT = [33, 263, 1, 61, 291, 199] 
    RIGHT_POINT_INT = [468, 33, 145, 133, 159,158]
    LEFT_POINT_INT = [473, 362, 374, 263, 386, 387]

    LEFT_POS_INT = [133, 158, 160, 33, 144, 153]
    RIGHT_POS_INT = [362, 385, 387, 263, 373, 380]

    
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True, # Enables  detailed eyes points
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_drawing = mp.solutions.drawing_utils

    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    cap = cv2.VideoCapture(0)


    statusIn10s = []
    ears = []


    start = time.time()

    while cap.isOpened():
        success, image = cap.read()
        
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



        left_eye_pos = []
        right_eye_pos = []

        face_pos_2d = []
        face_pos_3d = []
        left_eye_pos_2d = []
        right_eye_pos_2d = []
        left_eye_pos_3d = []
        right_eye_pos_3d = []
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx in FACE_POS_INT:
                        face_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h)])
                        face_pos_3d.append([int(lm.x * img_w), int(lm.y * img_h), lm.z])
                        cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(255, 0, 0), thickness=-1)
                    if idx in LEFT_POINT_INT:
                        left_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h)])
                        left_eye_pos_3d.append([int(lm.x * img_w), int(lm.y * img_h), lm.z])
                        cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 255, 0), thickness=-1)
                    if idx in RIGHT_POINT_INT:
                        right_eye_pos_2d.append([int(lm.x * img_w), int(lm.y * img_h)])
                        right_eye_pos_3d.append([int(lm.x * img_w), int(lm.y * img_h), lm.z])
                        cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 0, 255), thickness=-1)

                    if idx in LEFT_POS_INT:
                        left_eye_pos.append([int(lm.x * img_w), int(lm.y * img_h), LEFT_POS_INT.index(idx)])
                        cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(255, 255, 0), thickness=-1)
                        cv2.putText(image, str(LEFT_POS_INT.index(idx)), (int(lm.x * img_w), int(lm.y * img_h)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    if idx in RIGHT_POS_INT:
                        right_eye_pos.append([int(lm.x * img_w), int(lm.y * img_h), RIGHT_POS_INT.index(idx)])
                        cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(255, 0, 255), thickness=-1)
                        cv2.putText(image, str(RIGHT_POS_INT.index(idx)), (int(lm.x * img_w), int(lm.y * img_h)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                    
                    if idx == 1:
                        nose_pos_2d = ([int(lm.x * img_w), int(lm.y * img_h), idx])
                        nose_pos_3d = ([int(lm.x * img_w), int(lm.y * img_h), lm.z * 3000])
                        cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 255, 255), thickness=-1)
                    if idx == 473:
                        left_pupil_pos_2d = ([int(lm.x * img_w), int(lm.y * img_h)])
                        left_pupil_pos_3d = ([int(lm.x * img_w), int(lm.y * img_h), lm.z * 3000])
                        cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(128, 128, 0), thickness=-1)
                    if idx == 468:
                        right_pupil_pos_2d = ([int(lm.x * img_w), int(lm.y * img_h), idx])
                        right_pupil_pos_3d = ([int(lm.x * img_w), int(lm.y * img_h), lm.z * 3000])
                        cv2.circle(image, (int(lm.x * img_w), int(lm.y * img_h)), radius=5, color=(0, 128, 128), thickness=-1)

            #Task 1-2
            left_eye_pos.sort(key=lambda x: x[2])
            right_eye_pos.sort(key=lambda x: x[2]) 

            ear_sx ,ear_dx , ear = calculateEAR(image,left_eye_pos, right_eye_pos,ears)
            checkAwake(ear,ears, start, statusIn10s, image, img_w, img_h)

            #Task 3 in poi 
            face_pos_2d = np.array(face_pos_2d, dtype=np.float64)
            face_pos_3d = np.array(face_pos_3d, dtype=np.float64)
            left_eye_pos_2d = np.array(left_eye_pos_2d, dtype=np.float64)
            right_eye_pos_2d = np.array(right_eye_pos_2d, dtype=np.float64)
            left_eye_pos_3d = np.array(left_eye_pos_3d, dtype=np.float64)
            right_eye_pos_3d = np.array(right_eye_pos_3d, dtype=np.float64)
            nose_pos_2d = np.array(nose_pos_2d, dtype=np.float64)
            nose_pos_3d = np.array(nose_pos_3d, dtype=np.float64)
            left_pupil_pos_2d = np.array(left_pupil_pos_2d, dtype=np.float64)
            left_pupil_pos_3d = np.array(left_pupil_pos_3d, dtype=np.float64)
            right_pupil_pos_2d = np.array(right_pupil_pos_2d, dtype=np.float64)
            right_pupil_pos_3d = np.array(right_pupil_pos_3d, dtype=np.float64)



            roll, pitch, yaw , pitch_left_eye, yaw_left_eye, pitch_right_eye, yaw_right_eye, nose_3d_projection = checkGaze(image,face_pos_2d, face_pos_3d, left_eye_pos_2d, left_eye_pos_3d, right_eye_pos_2d, right_eye_pos_3d)
            check_driver_distraction(pitch_left_eye, yaw_left_eye, pitch_right_eye, yaw_right_eye, pitch, yaw, roll, image, img_w)
            plotDirections(image, nose_pos_2d, pitch, yaw, left_pupil_pos_2d, pitch_left_eye, yaw_left_eye, right_pupil_pos_2d, pitch_right_eye, yaw_right_eye, ear)

            


        cv2.imshow('output window', image)       
        if cv2.waitKey(5) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()