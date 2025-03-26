import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Configurazione parametri
ALERT_THRESHOLD = 50  # Soglia di distanza in pixel
ALERT_COLOR = (0, 0, 255)  # Colore ROSSO per l'allerta

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Disegna landmark e connessioni
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Coordinate punti chiave
            h, w, _ = image.shape
            point4 = hand_landmarks.landmark[4]
            point12 = hand_landmarks.landmark[12]
            
            # Conversione a coordinate immagine
            x4, y4 = int(point4.x * w), int(point4.y * h)
            x12, y12 = int(point12.x * w), int(point12.y * h)
            
            # Calcola distanza euclidea
            distance = math.hypot(x12 - x4, y12 - y4)
            
            # Visualizza distanza
            cv2.putText(image, f"Distance: {int(distance)}px", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (255, 255, 255), 2)
            
            # Controllo allerta
            if distance < ALERT_THRESHOLD:
                # Linea di connessione tra i punti
                cv2.line(image, (x4, y4), (x12, y12), ALERT_COLOR, 3)
                
                # Cerchi colorati sui punti
                cv2.circle(image, (x4, y4), 10, ALERT_COLOR, -1)
                cv2.circle(image, (x12, y12), 10, ALERT_COLOR, -1)
                
                # Testo di allerta lampeggiante
                cv2.putText(image, "CONTACT DETECTED!", (w//2 - 150, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, ALERT_COLOR, 3, cv2.LINE_AA)

    cv2.imshow('Hand Proximity Alert', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
