# Driver Drowsiness and Distraction Monitoring System Based on MediaPipe

The analyzed code implements an advanced real-time monitoring system to detect drowsiness and distraction in drivers, using computer vision and MediaPipe. The system captures and analyzes the driver’s eye and head movements, calculating key metrics to determine the level of attention and fatigue, and sends alerts when it detects dangerous behavior.

## Methods for Calculating EAR and PERCLOS

### Eye Aspect Ratio (EAR)
The system calculates the Eye Aspect Ratio, a key indicator of eye closure, through a series of geometric operations on the detected facial landmarks:

```python
def calculateClosedEyeRatio(eye):
    A = np.sqrt(abs(eye[1][0] - eye[5][0])**2 + abs(eye[1][1] - eye[5][1])**2)
    B = np.sqrt(abs(eye[2][0] - eye[4][0])**2 + abs(eye[2][1] - eye[4][1])**2)
    C = np.sqrt(abs(eye[0][0] - eye[3][0])**2 + abs(eye[0][1] - eye[3][1])**2)
    # Calculate the EAR
    ear = (A + B) / (2.0 * C)
    return ear
```

The EAR calculation is based on three fundamental measurements:
- Distance A between the upper lateral points of the eye (points 1 and 5)
- Distance B between the lower lateral points of the eye (points 2 and 4)
- Distance C between the extreme points of the eye (points 0 and 3)

The final ratio is calculated as the average of the vertical distances divided by the horizontal distance: `(A + B) / (2.0 * C)`. This value is calculated separately for both eyes and then averaged to obtain an overall EAR:

```python
def calculateEAR(image, left_eye_pos_2d, right_eye_pos_2d, ears):
    ear_sx = calculateClosedEyeRatio(left_eye_pos_2d)
    ear_dx = calculateClosedEyeRatio(right_eye_pos_2d)
    ear = (ear_sx + ear_dx) / 2.0
    ear = min(ear, 0.34)
    ear = (ear / 0.34) * 100
    ears.append(ear)
```

The system then normalizes the EAR, limiting it to a maximum of 0.34 and converting it to a percentage for more intuitive interpretation.

### PERCLOS (PERcentage of eye CLOSure)
PERCLOS is a fundamental metric for assessing driver fatigue, based on the percentage of time the eyes are closed. The system calculates it through the `calculateDeltaTime` function:

```python
def calculateDeltaTime(earsWindow):
    t2, t3, t4 = 0, 0, 0
    t2_1, t2_2, t3_1, t3_2, t4_1, t4_2 = 0, 0, 0, 0, 0, 0
    # Calculation of time intervals
    # ...
    if t4 != 0:
        return (t3-t2)/(t4)
    else:
        return 0
```

The system measures three critical time intervals:
- t2: period when the eyes are partially closed (EAR ≤ 80% and > 20%)
- t3: period when the eyes are completely closed (EAR ≤ 20%)
- t4: the full interval from the start of closure to complete reopening (EAR ≥ 80%)

The final formula `(t3-t2)/t4` represents the ratio between the time of complete eye closure and the total closure-opening cycle, thus providing a precise indicator of driver drowsiness.

## Detection of Gaze Direction and Head Position

### Head Gaze (Head Orientation)

The system uses advanced computer vision techniques to determine the 3D orientation of the head:

```python
def checkGaze(image, face_pos_2d, face_pos_3d, left_eye_pos_2d, left_eye_pos_3d, right_eye_pos_2d, right_eye_pos_3d):
    # Camera matrix and distortion parameters
    focal_length = 1 * img_w
    cam_matrix = np.array([[focal_length, 0, img_h / 2],
                           [0, focal_length, img_w / 2],
                           [0, 0, 1]])
    dist_matrix = np.zeros((4, 1), dtype=np.float64)
    # Solve PnP
    success, rot_vec, trans_vec = cv2.solvePnP(face_pos_3d, face_pos_2d, cam_matrix, dist_matrix)
    # Calculate Euler angles
    rmat, jac = cv2.Rodrigues(rot_vec)
    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
    # Convert to degrees
    pitch = angles[0] * 1800
    yaw = -angles[1] * 1800
    # ...
```

The code uses OpenCV’s `solvePnP` algorithm, which solves the Perspective-n-Point problem to calculate the rotation and translation vectors of the face. These vectors are then converted into Euler angles using `cv2.Rodrigues` and `cv2.RQDecomp3x3`.

The three fundamental angles calculated are:
- Pitch: vertical tilt of the head (looking up/down)
- Yaw: horizontal rotation of the head (looking right/left)
- Roll: lateral tilt of the head, calculated using the relative position of the eyes

### Eye Gaze (Gaze Direction)

In addition to head position, the system also tracks the gaze direction of each eye:

```python
success_left_eye, rot_vec_left_eye, trans_vec_left_eye = cv2.solvePnP(left_eye_pos_3d, left_eye_pos_2d, cam_matrix, dist_matrix)
success_right_eye, rot_vec_right_eye, trans_vec_right_eye = cv2.solvePnP(right_eye_pos_3d, right_eye_pos_2d, cam_matrix, dist_matrix)
# Calculate angles for each eye
angles_left_eye, mtxR_left_eye, mtxQ_left_eye, Qx_left_eye, Qy_left_eye, Qz_left_eye = cv2.RQDecomp3x3(rmat_left_eye)
angles_right_eye, mtxR_right_eye, mtxQ_right_eye, Qx_right_eye, Qy_right_eye, Qz_right_eye = cv2.RQDecomp3x3(rmat_right_eye)
pitch_left_eye = angles_left_eye[0] * 1800
yaw_left_eye = angles_left_eye[1] * 1800
pitch_right_eye = angles_right_eye[0] * 1800
yaw_right_eye = angles_right_eye[1] * 1800
```

The system applies the same approach used for the head to each eye separately, obtaining the pitch and yaw values for both eyes. This data allows the system to detect when the gaze is not aligned with the head orientation, a further indicator of distraction.

The visualization of gaze direction is implemented through the `plotDirections` function, which draws vector lines starting from the reference points of the nose and pupils:

```python
def plotDirections(image, nose_pos_2d, pitch, yaw, left_pupil_pos_2d, pitch_left_eye, yaw_left_eye, right_pupil_pos_2d, pitch_right_eye, yaw_right_eye, ear):
    p1 = (int(nose_pos_2d[0]), int(nose_pos_2d[1]))
    p2 = (int(nose_pos_2d[0] + yaw * 10), int(nose_pos_2d[1] - pitch * 10))
    cv2.line(image, p1, p2, (255, 0, 0), 3)
    if ear > 20:
        # Draw lines for the eyes only if they are sufficiently open
        # ...
```

## Drowsiness Monitoring Systems and Visualization

### Drowsiness Detection

The system implements a sophisticated temporal analysis to determine if the driver is drowsy:

```python
def checkAwake(ear, ears, start, statusIn10s, image, img_w, img_h):
    if ear  300:
        statusIn10s.pop(0)
    if st.mean(statusIn10s) > 0.8 and len(statusIn10s) > 300:
        cv2.putText(image, "DROWSY", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if telegram_alert:
            asyncio.run(send_alert("WARNING: The driver appears drowsy!"))
    else:
        cv2.putText(image, "AWAKE", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
```

This method analyzes the EAR in real time and accumulates a history of states (drowsy/awake) over the last 300 frames. If the average of drowsy states exceeds 80%, the system declares the driver "DROWSY" and can send an alert via Telegram.

### Distraction Detection

To identify driver distraction, the system combines head orientation and eye gaze data:

```python
def check_driver_distraction(pitch_left_eye, yaw_left_eye, pitch_right_eye, yaw_right_eye, pitch, yaw, roll, image, img_w):
    global distraction_start_time, alert_sent
    avg_pitch_eyes = (pitch_left_eye + pitch_right_eye) / 2
    avg_yaw_eyes = (yaw_left_eye + yaw_right_eye) / 2
    combined_pitch = pitch + avg_pitch_eyes
    combined_yaw = yaw + avg_yaw_eyes
    is_distracted = abs(combined_pitch) > 30 or abs(combined_yaw) > 30 or abs(roll) > 30
    if is_distracted:
        # Handle distraction state
        # ...
```

The system calculates combined values for pitch and yaw, considering both head orientation and eye gaze direction. If any of the angles exceed 30 degrees, the driver is considered distracted.

Additionally, the system tracks the duration of distraction, sending an alert if it persists for more than 5 seconds:

```python
if distraction_duration >= 5 and not alert_sent:
    global telegram_alert
    if telegram_alert:
        asyncio.run(send_alert("WARNING: The driver appears distracted for more than 5 seconds!"))
    alert_sent = True
```

### Visualization of Graphs and Statistics

The system presents detailed graphical visualizations to assist in monitoring:

```python
def plotStats(image, ears, statusIn10s, img_w, img_h):
    # Graph dimensions
    graph_width = int(img_w * 0.3)
    graph_height = int(img_h * 0.2)
    graph_x_start = int(img_w - graph_width - (img_h * 0.05))
    graph_y_start = int(img_h * 0.75)
    # Draw EAR graph
    # ...
    # Draw threshold lines
    threshold_80_y = graph_y_start + graph_height - int(80 * graph_height / 100)
    threshold_20_y = graph_y_start + graph_height - int(20 * graph_height / 100)
    # ...
    # Draw drowsiness status graph
    # ...
```

Two main graphs are created:
1. **EAR Graph**: shows the temporal trend of the Eye Aspect Ratio, with threshold lines at 20% and 80% indicating closed and fully open eyes, respectively.
2. **Drowsiness Status Graph**: visually represents the periods when the system detected the driver as drowsy.

These graphs are strategically positioned in the lower right corner of the image and include descriptive labels for easier interpretation.

## Conclusion

The system implements a multimodal approach for monitoring driver drowsiness and distraction, integrating:

1. Precise analysis of eye openness via EAR
2. Drowsiness assessment through PERCLOS
3. Detection of head orientation and gaze direction
4. Temporal monitoring of drowsiness and distraction states
5. Clear graphical visualizations of critical metrics
6. Alert system for potentially dangerous situations

This implementation represents a significant step forward in driver safety systems, offering non-invasive yet effective monitoring of driver attention, with important potential applications in preventing accidents caused by drowsiness and distraction.

