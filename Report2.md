# Driver Monitoring System: Implementation and Analysis

In this report, I describe the implementation of a Driver Monitoring System (DMS) developed as part of my academic project. The system utilizes computer vision techniques to detect the main indicators of drowsiness and distraction while driving, with the aim of improving road safety through monitoring the attentive state of the driver.

## Introduction

Driver monitoring systems represent a rapidly growing research area in the field of vehicle safety. The main objective of these systems is to prevent road accidents caused by driver distraction or drowsiness through real-time analysis of behavioral parameters. My work focused on implementing a non-invasive monitoring system that uses a single camera to track the movements of the driver's eyes, mouth, and head, analyzing this data to identify potential risk situations.

Unlike traditional systems that use biometric sensors, my approach relies solely on processing images acquired from a front-facing camera, in compliance with the requirements of Delegated Regulation (EU) 2023/2590. I implemented algorithms for calculating key metrics such as Eye Aspect Ratio (EAR), PERCLOS (PERcentage of eye CLOSure), and head orientation estimation to detect various driver states.

## Eye Aspect Ratio (EAR) Calculation

For drowsiness detection, I implemented an algorithm based on the Eye Aspect Ratio (EAR), a metric that quantifies eye openness. The implementation is based on extracting facial landmarks using the MediaPipe library, which provides 468 reference points compared to the 68 offered by OpenCV, thus ensuring greater precision.

To calculate the EAR, I identified 12 specific reference points for the eyes:
- For the left eye:[362][385][387][263][373][380]
- For the right eye:[133][143][144][158][160]

The EAR was calculated using the following formula:

```
EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
```

where p1-p6 represent the eye reference points and ||p_i-p_j|| indicates the Euclidean distance between points p_i and p_j.

I established a threshold value of 0.25 for the EAR; values below this threshold indicate that the eyes are closed. This methodology allowed me to effectively detect eye closure states, distinguishing between normal blinks and prolonged closures due to drowsiness.

## PERCLOS Implementation

PERCLOS is considered an industry standard for measuring drowsiness and has been validated as one of the most reliable metrics for detecting driver alertness. To implement this metric, I calculated the percentage of time the driver's eyes remain closed within a defined interval.

My PERCLOS calculation algorithm follows these steps:

1. Acquisition of continuous video frames through the camera
2. Conversion of each frame to grayscale to optimize processing
3. Face detection and tracking in each frame
4. Extraction of eye reference points using MediaPipe
5. EAR calculation for each frame
6. Counting of frames where EAR is below the threshold (0.25)
7. Calculation of PERCLOS as the ratio between the number of frames with closed eyes and the total number of frames in a defined time interval (typically 60 seconds)

The formula used is:
```
PERCLOS = (Number of frames with EAR < threshold / Total number of frames in the interval) * 100
```

I established a threshold value of 20% for PERCLOS; values above this threshold indicate a state of driver drowsiness. This approach allowed me to overcome the limitations of simple eye closure detection, providing a more robust and continuous measure of the driver's alertness.

## Distraction Detection and Head Orientation

To detect driver distraction, I implemented a head position estimation algorithm based on facial landmark analysis. This methodology identifies when the driver's gaze is not directed at the road, indicating potential distractions.

Head orientation detection is based on the following steps:

1. Extraction of nose reference points using MediaPipe
2. Definition of reference values for the x, y, and z axes based on the calibrated initial position
3. Calculation of head rotations relative to these reference values
4. Classification of head orientation into five main directions: left, right, up, down, and forward

For each frame, the system calculates the head rotation angles (yaw, pitch, and roll) and compares them with predefined threshold values to determine orientation. A significant deviation from the frontal position is classified as potential distraction.

This implementation complies with regulatory requirements that demand distraction detection systems be capable of identifying when the driver's visual attention moves away from the driving task, automatically activating when the vehicle speed exceeds 20 km/h.

## Yawn Detection

To complete the monitoring system, I also implemented an algorithm for yawn detection, an important indicator of drowsiness. The detection is based on calculating the Mouth Aspect Ratio (MAR), a metric that quantifies mouth opening.

To calculate the MAR, I used the following reference points for the mouth:[291][181][269][405]

I established a threshold value of 0.75 for the MAR; values above this threshold indicate a yawn. This approach allowed me to effectively detect yawns, providing an additional indicator of the driver's drowsiness state.

## Conclusions

The implemented driver monitoring system represents a comprehensive approach to detecting drowsiness and distraction while driving. Through the combined use of metrics such as EAR, PERCLOS, head orientation, and MAR, the system is able to provide reliable monitoring of the driver's state, potentially contributing to the reduction of road accidents caused by human factors.

The adopted methodology respects privacy and data protection requirements, operating without relying on personal biometric data of vehicle occupants other than the driver. Additionally, the system is designed to function reliably in different lighting conditions, ensuring consistent performance both day and night.

Future developments could include the integration of machine learning models to further improve system accuracy and the implementation of adaptive feedback mechanisms that adjust thresholds based on individual driver characteristics.

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/45403030/9f8e2911-b6fd-44bb-bf7c-f464711b3501/assignment_deadline17042025.pdf
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/45403030/a1f372f6-8079-4cf7-963f-18051623e017/05-dm-AI_v2.pdf
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/45403030/51b3b08d-e533-4d15-8748-701b2efa4122/LabMediaPipe.py

---
Answer from Perplexity: pplx.ai/share