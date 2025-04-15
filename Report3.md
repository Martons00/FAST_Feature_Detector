# Implementation of a Driver Monitoring System Using MediaPipe

In this report, I describe the implementation of a driver monitoring system based on computer vision techniques, developed using Python and the MediaPipe library. The main objective was to develop a system capable of detecting driver drowsiness and distraction by analyzing camera images in real-time.

## Methodology and Tools

I implemented the system using Python 3 with the following main libraries:
- MediaPipe for facial landmark detection
- OpenCV for image processing and visualization
- NumPy for mathematical operations
- TelegramBot API for sending remote notifications

MediaPipe provides a pre-trained neural network that identifies 468 facial landmarks, enabling detailed analysis of the eyes, mouth, and general face orientation. I leveraged these capabilities to implement the functionalities required by the assignment.

## Eye Aspect Ratio (EAR) Calculation

To determine the state of eye openness, I implemented the Eye Aspect Ratio (EAR) calculation, which measures the ratio between the height and width of the eye. The formula used is:

```
EAR = (|Y₂-Y₆| + |Y₃-Y₅|) / (2·|X₁-X₄|)
```

In my code, I implemented this formula in the `calculateClosedEyeRatio` function:

```python
def calculateClosedEyeRatio(eye):
    A = np.sqrt(abs(eye[1][0] - eye[5][0])**2 + abs(eye[1][1] - eye[5][1])**2)
    B = np.sqrt(abs(eye[2][0] - eye[4][0])**2 + abs(eye[2][1] - eye[4][1])**2)
    C = np.sqrt(abs(eye[0][0] - eye[3][0])**2 + abs(eye[0][1] - eye[3][1])**2)
    ear = (A + B) / (2.0 * C)
    return ear
```

I calculate the EAR for both eyes and then average them to obtain a more robust value. Additionally, I normalized the value on a percentage scale to facilitate interpretation and comparison with thresholds:

```python
ear = (ear_sx + ear_dx) / 2.0
ear = min(ear, 0.34)
ear = (ear / 0.34) * 100
```

## PERCLOS Implementation

PERCLOS (PERcentage of eye CLOSure) is a standard metric for evaluating drowsiness, measuring the percentage of time the eyes are closed in a given interval. I implemented the PERCLOS calculation according to the formula:

```
PERCLOS = (t₃-t₂) / (t₄-t₁)
```

where:
- t₁: moment when eyes go from fully open to 80% open
- t₂: moment when eyes go from 80% to 20% open
- t₃: moment when eyes go from 20% closed to 20% open
- t₄: moment when eyes go from 20% to 80% open

In the code, I implemented this logic in the `calculateDeltaTime` function:

```python
def calculateDeltaTime(earsWindow):
    t2, t3, t4 = 0, 0, 0
    t2_1, t2_2, t3_1, t3_2, t4_1, t4_2 = 0, 0, 0, 0, 0, 0
    
    for i in range(len(earsWindow)):
        # Calculation of t3 (from 20% closed to 20% open)
        if earsWindow[i]  20:
            t3_1 = i
        if earsWindow[i] >= 20 and earsWindow[i-1]  180:
    roll = roll - 360
```

I applied the same approach to determine eye orientation, thus obtaining a complete representation of head orientation and gaze direction.

## Driver Distraction Detection

To detect driver distraction, I combined information about head and eye orientation. If this combination deviates more than 30° from the rest position (0,0,0), I consider the driver distracted:

```python
def check_driver_distraction(pitch_left_eye, yaw_left_eye, pitch_right_eye, yaw_right_eye, pitch, yaw, roll, image, img_w):
    avg_pitch_eyes = (pitch_left_eye + pitch_right_eye) / 2
    avg_yaw_eyes = (yaw_left_eye + yaw_right_eye) / 2
    combined_pitch = pitch + avg_pitch_eyes
    combined_yaw = yaw + avg_yaw_eyes
    
    is_distracted = abs(combined_pitch) > 30 or abs(combined_yaw) > 30 or abs(roll) > 30
    
    # Distraction state management and alert sending
    # ...
```

To increase system robustness, I implemented a temporal system that sends an alarm only if the distraction persists for more than 5 seconds.

## Visualization and User Interface

To facilitate real-time monitoring, I implemented various visualizations:

1. A graph of EAR over time showing the 20% and 80% thresholds
2. Visual indicators of head orientation and gaze direction
3. Numerical display of pitch, yaw, roll, and EAR values
4. Alarm messages in case of drowsiness or distraction

```python
def plotStats(image, ears, statusIn10s, img_w, img_h):
    # Draw the EAR graph over time
    # ...
    
    # Draw thresholds
    threshold_80_y = graph_y_start + graph_height - int(80 * graph_height / 100)
    threshold_20_y = graph_y_start + graph_height - int(20 * graph_height / 100)
    cv2.line(image, (graph_x_start, threshold_80_y),
            (graph_x_start + graph_width, threshold_80_y),
            (0, 255, 0), 1)
    cv2.line(image, (graph_x_start, threshold_20_y),
            (graph_x_start + graph_width, threshold_20_y),
            (0, 0, 255), 1)
```

## Conclusions

The implemented system meets all the requirements of the assignment, providing a functional and responsive driver monitoring system. The system can detect drowsiness through EAR and PERCLOS analysis, and distractions through head and gaze orientation calculations. Integration with Telegram also allows sending remote notifications in case of potentially dangerous situations.

The system could be further improved by implementing filtering techniques to reduce false positives and machine learning algorithms to adapt to the specific characteristics of different drivers.

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/45403030/9f8e2911-b6fd-44bb-bf7c-f464711b3501/assignment_deadline17042025.pdf
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/45403030/a1f372f6-8079-4cf7-963f-18051623e017/05-dm-AI_v2.pdf
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/45403030/51b3b08d-e533-4d15-8748-701b2efa4122/LabMediaPipe.py

---
Answer from Perplexity: pplx.ai/share