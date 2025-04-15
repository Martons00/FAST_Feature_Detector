# Implementation of a Driver Monitoring System Using MediaPipe

In this report, I describe the implementation of a driver monitoring system based on computer vision techniques, developed using Python and the MediaPipe library. The main objective was to develop a system capable of detecting driver drowsiness and distraction by analyzing camera images in real-time. The system captures and analyzes the driver's eye and head movements, calculating key metrics to determine the level of attention and fatigue, and sends alerts when it detects dangerous behavior.
For alerting the user, on-screen warnings were used along with messages sent via Telegram bot for added functionality.

## Introduction

After configuring the capture environment, positions of interest from facial landmarks are acquired, which are then used to compute various metrics for our system. This process occurs within a loop, performing analysis for each frame captured by the camera, at a rate of approximately 30 fps.

// screenshot of the if statements for position capture

## Methods for Calculating EAR and PERCLOS

### Eye Aspect Ratio (EAR)
For drowsiness detection, I implemented an algorithm based on the Eye Aspect Ratio (EAR), a metric that quantifies eye openness. To calculate the EAR, I identified 12 specific reference points for the eyes:

For the left eye:[362][385][387][263][373][380]
For the right eye:[133][143][144][158][160]

// screenshot of the formula and my capture photo

I calculate the EAR for both eyes and then average them to obtain a more robust value. Additionally, I normalized the value on a percentage scale to facilitate interpretation and comparison with a threshold of 0.35.
Using the EAR values, I constructed a curve showing all EAR values within a 10-second window. I also developed a curve indicating the state when EAR is below the 20% threshold (indicating closed eyes) by assigning a value of 1, and 0 when eyes are open. Using these states, if the average is > 0.8 over 10 seconds, the system sends an alarm message to the driver warning that they are drowsy.

Furthermore, as required, if the EAR > 80% for 10 seconds, the driver is alerted about their inattention.

// screenshot of the window

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

To accomplish this, I wrote a function that calculates the sum of t2, t3, and t4 within the reference window. I consider t1 to be approximately 0 since in a real environment, it is difficult to capture correctly due to noise.

// screenshot of how to recognize events to calculate deltas and PERCLOS value

If the PERCLOS value exceeds a threshold, the system warns the driver that they are falling asleep.

## Detection of Gaze Direction and Head Position

### Head Gaze (Head Orientation)
To detect driver distraction, I implemented a head position estimation algorithm based on facial landmark analysis. This methodology identifies when the driver's gaze is not directed at the road, indicating potential distractions.

Head orientation detection is based on the following steps:

Extraction of nose reference points using MediaPipe
Definition of reference values for the x, y, and z axes based on the calibrated initial position
Calculation of head rotations relative to these reference values
The code uses OpenCV's solvePnP algorithm, which solves the Perspective-n-Point problem to calculate the rotation and translation vectors of the face. These vectors are then converted into Euler angles using cv2.Rodrigues and cv2.RQDecomp3x3.

// relevant code

The three fundamental angles calculated are:

Pitch: vertical tilt of the head (looking up/down)
Yaw: horizontal rotation of the head (looking right/left)
Roll: lateral tilt of the head, calculated using the relative position of the eyes
Classification of head orientation into five main directions: left, right, up, down, and forward
For each frame, the system calculates the head rotation angles (yaw, pitch, and roll) and compares them with predefined threshold values to determine orientation. A significant deviation from the frontal position is classified as potential distraction.
The system applies the same approach used for the head to each eye separately, obtaining the pitch and yaw values for both eyes. This data allows the system to detect when the gaze is not aligned with the head orientation, a further indicator of distraction.

Using these values, I estimated the direction from the eyes and nose.

// screenshot of the lines

## Conclusion

The implemented system meets all the requirements of the assignment, providing a functional and responsive driver monitoring system. The system can detect drowsiness through EAR and PERCLOS analysis, and distractions through head and gaze orientation calculations. Integration with Telegram also allows sending remote notifications in case of potentially dangerous situations.

The system could be further improved by implementing filtering techniques to reduce false positives and machine learning algorithms to adapt to the specific characteristics of different drivers.

The implemented driver monitoring system represents a comprehensive approach to detecting drowsiness and distraction while driving. Through the combined use of metrics such as EAR, PERCLOS, head orientation, and MAR, the system is able to provide reliable monitoring of the driver's state, potentially contributing to the reduction of road accidents caused by human factors.

The adopted methodology respects privacy and data protection requirements, operating without relying on personal biometric data of vehicle occupants other than the driver. Additionally, the system is designed to function reliably in different lighting conditions, ensuring consistent performance both day and night.

Future developments could include the integration of machine learning models to further improve system accuracy and the implementation of adaptive feedback mechanisms that adjust thresholds based on individual driver characteristics.
