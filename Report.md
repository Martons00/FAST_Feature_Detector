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

# Implementazione di un Sistema di Monitoraggio del Conducente Utilizzando MediaPipe

In questo report descrivo l'implementazione di un sistema di monitoraggio del conducente basato su tecniche di visione artificiale, realizzato utilizzando Python e la libreria MediaPipe. L'obiettivo principale è stato sviluppare un sistema in grado di rilevare la sonnolenza e le distrazioni del conducente analizzando in tempo reale le immagini catturate da una telecamera.

## Metodologia e Strumenti

Ho implementato il sistema utilizzando Python 3 con le seguenti librerie principali:
- MediaPipe per il rilevamento dei punti di riferimento facciali
- OpenCV per l'elaborazione delle immagini e la visualizzazione
- NumPy per le operazioni matematiche
- TelegramBot API per l'invio di notifiche remote

MediaPipe fornisce una rete neurale pre-addestrata che identifica 468 punti di riferimento sul volto, permettendo un'analisi dettagliata degli occhi, della bocca e dell'orientamento generale del viso. Ho sfruttato queste capacità per implementare le funzionalità richieste dall'assignment.

## Calcolo dell'Eye Aspect Ratio (EAR)

Per determinare lo stato di apertura degli occhi, ho implementato il calcolo dell'Eye Aspect Ratio (EAR), che misura il rapporto tra l'altezza e la larghezza dell'occhio. La formula utilizzata è:

```
EAR = (|Y₂-Y₆| + |Y₃-Y₅|) / (2·|X₁-X₄|)
```

Nel mio codice, ho implementato questa formula nella funzione `calculateClosedEyeRatio`:

```python
def calculateClosedEyeRatio(eye):
    A = np.sqrt(abs(eye[1][0] - eye[5][0])**2 + abs(eye[1][1] - eye[5][1])**2)
    B = np.sqrt(abs(eye[2][0] - eye[4][0])**2 + abs(eye[2][1] - eye[4][1])**2)
    C = np.sqrt(abs(eye[0][0] - eye[3][0])**2 + abs(eye[0][1] - eye[3][1])**2)
    ear = (A + B) / (2.0 * C)
    return ear
```

Calcolo l'EAR per entrambi gli occhi e poi ne faccio la media per ottenere un valore più robusto. Inoltre, ho normalizzato il valore su una scala percentuale per facilitare l'interpretazione e il confronto con le soglie:

```python
ear = (ear_sx + ear_dx) / 2.0
ear = min(ear, 0.34)
ear = (ear / 0.34) * 100
```

## Implementazione del PERCLOS

Il PERCLOS (PERcentage of eye CLOSure) è una metrica standard per valutare la sonnolenza, misurando la percentuale di tempo in cui gli occhi sono chiusi in un determinato intervallo. Ho implementato il calcolo del PERCLOS secondo la formula:

```
PERCLOS = (t₃-t₂) / (t₄-t₁)
```

dove:
- t₁: momento in cui gli occhi passano da completamente aperti a 80% aperti
- t₂: momento in cui gli occhi passano da 80% a 20% aperti
- t₃: momento in cui gli occhi passano da 20% chiusi a 20% aperti
- t₄: momento in cui gli occhi passano da 20% a 80% aperti

Nel codice, ho implementato questa logica nella funzione `calculateDeltaTime`:

```python
def calculateDeltaTime(earsWindow):
    t2, t3, t4 = 0, 0, 0
    t2_1, t2_2, t3_1, t3_2, t4_1, t4_2 = 0, 0, 0, 0, 0, 0
    
    for i in range(len(earsWindow)):
        # Calcolo di t3 (da 20% chiuso a 20% aperto)
        if earsWindow[i]  20:
            t3_1 = i
        if earsWindow[i] >= 20 and earsWindow[i-1]  180:
    roll = roll - 360
```

Ho applicato lo stesso approccio per determinare l'orientamento degli occhi, ottenendo così una rappresentazione completa dell'orientamento della testa e della direzione dello sguardo.

## Rilevamento delle Distrazioni del Conducente

Per rilevare le distrazioni del conducente, ho combinato l'informazione sull'orientamento della testa e degli occhi. Se questa combinazione devia più di 30° rispetto alla posizione di riposo (0,0,0), considero il conducente distratto:

```python
def check_driver_distraction(pitch_left_eye, yaw_left_eye, pitch_right_eye, yaw_right_eye, pitch, yaw, roll, image, img_w):
    avg_pitch_eyes = (pitch_left_eye + pitch_right_eye) / 2
    avg_yaw_eyes = (yaw_left_eye + yaw_right_eye) / 2
    combined_pitch = pitch + avg_pitch_eyes
    combined_yaw = yaw + avg_yaw_eyes
    
    is_distracted = abs(combined_pitch) > 30 or abs(combined_yaw) > 30 or abs(roll) > 30
    
    # Gestione dello stato di distrazione e invio di alert
    # ...
```

Per aumentare la robustezza del sistema, ho implementato un sistema temporale che invia un allarme solo se la distrazione persiste per più di 5 secondi.

## Visualizzazione e Interfaccia Utente

Per facilitare il monitoraggio in tempo reale, ho implementato diverse visualizzazioni:

1. Un grafico dell'EAR nel tempo che mostra le soglie del 20% e 80%
2. Indicatori visivi dell'orientamento della testa e dello sguardo
3. Visualizzazione numerica dei valori di pitch, yaw, roll e EAR
4. Messaggi di allarme in caso di sonnolenza o distrazione

```python
def plotStats(image, ears, statusIn10s, img_w, img_h):
    # Disegna il grafico EAR nel tempo
    # ...
    
    # Disegna le soglie
    threshold_80_y = graph_y_start + graph_height - int(80 * graph_height / 100)
    threshold_20_y = graph_y_start + graph_height - int(20 * graph_height / 100)
    cv2.line(image, (graph_x_start, threshold_80_y),
            (graph_x_start + graph_width, threshold_80_y),
            (0, 255, 0), 1)
    cv2.line(image, (graph_x_start, threshold_20_y),
            (graph_x_start + graph_width, threshold_20_y),
            (0, 0, 255), 1)
```

## Conclusioni

L'implementazione realizzata soddisfa tutti i requisiti dell'assignment, fornendo un sistema di monitoraggio del conducente funzionale e reattivo. Il sistema è in grado di rilevare la sonnolenza attraverso l'analisi di EAR e PERCLOS, e le distrazioni mediante il calcolo dell'orientamento della testa e dello sguardo. L'integrazione con Telegram consente inoltre di inviare notifiche remote in caso di situazioni potenzialmente pericolose.

Il sistema può essere ulteriormente migliorato implementando tecniche di filtraggio per ridurre i falsi positivi e algoritmi di apprendimento automatico per adattarsi alle caratteristiche specifiche di diversi conducenti.

# Sistema di Monitoraggio del Conducente: Implementazione e Analisi

In questo report descrivo l'implementazione di un sistema di monitoraggio del conducente (Driver Monitoring System - DMS) sviluppato nell'ambito del mio progetto accademico. Il sistema utilizza tecniche di computer vision per rilevare i principali indicatori di sonnolenza e distrazione alla guida, con l'obiettivo di migliorare la sicurezza stradale attraverso il monitoraggio dello stato attentivo del conducente.

## Introduzione

I sistemi di monitoraggio del conducente rappresentano un'area di ricerca in rapida crescita nell'ambito della sicurezza dei veicoli. L'obiettivo principale di questi sistemi è prevenire incidenti stradali dovuti alla distrazione o alla sonnolenza del conducente attraverso l'analisi in tempo reale dei parametri comportamentali[1]. Il mio lavoro si è concentrato sull'implementazione di un sistema di monitoraggio non invasivo che utilizza una singola telecamera per tracciare i movimenti degli occhi, della bocca e della testa del conducente, analizzando questi dati per identificare potenziali situazioni di rischio.

A differenza dei sistemi tradizionali che utilizzano sensori biometrici, il mio approccio si basa unicamente sull'elaborazione di immagini acquisite da una telecamera frontale, in conformità con i requisiti del regolamento delegato (UE) 2023/2590[1]. Ho implementato algoritmi per il calcolo di metriche chiave come l'Eye Aspect Ratio (EAR), il PERCLOS (PERcentage of eye CLOSure) e la stima dell'orientamento della testa per rilevare vari stati del conducente.

## Calcolo dell'Eye Aspect Ratio (EAR)

Per il rilevamento della sonnolenza, ho implementato un algoritmo basato sull'Eye Aspect Ratio (EAR), una metrica che quantifica l'apertura degli occhi. L'implementazione si basa sull'estrazione di punti di riferimento facciali (facial landmarks) utilizzando la libreria Mediapipe, che fornisce 468 punti di riferimento rispetto ai 68 offerti da OpenCV, garantendo così una maggiore precisione[7].

Per calcolare l'EAR, ho identificato 12 punti di riferimento specifici per gli occhi:
- Per l'occhio sinistro:[362][385][387][263][373][380]
- Per l'occhio destro:[133][143][144][158][160]

L'EAR è stato calcolato utilizzando la seguente formula:

```
EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
```

dove p1-p6 rappresentano i punti di riferimento degli occhi e ||p_i-p_j|| indica la distanza euclidea tra i punti p_i e p_j[2].

Ho stabilito un valore di soglia di 0,25 per l'EAR; valori inferiori a questa soglia indicano che gli occhi sono chiusi[7]. Questa metodologia mi ha permesso di rilevare efficacemente gli stati di chiusura degli occhi, distinguendo tra normali battiti di ciglia e chiusure prolungate dovute alla sonnolenza.

## Implementazione del PERCLOS

Il PERCLOS è considerato uno standard nell'industria per la misurazione della sonnolenza ed è stato validato come una delle metriche più affidabili per il rilevamento della vigilanza del conducente[8]. Per implementare questa metrica, ho calcolato la percentuale di tempo in cui gli occhi del conducente rimangono chiusi in un intervallo definito.

Il mio algoritmo di calcolo del PERCLOS segue questi passaggi:

1. Acquisizione di frame video continui attraverso la telecamera
2. Conversione di ciascun frame in scala di grigi per ottimizzare l'elaborazione
3. Rilevamento e tracciamento del volto in ogni frame
4. Estrazione dei punti di riferimento degli occhi utilizzando Mediapipe
5. Calcolo dell'EAR per ciascun frame
6. Conteggio dei frame in cui l'EAR è inferiore alla soglia (0,25)
7. Calcolo del PERCLOS come rapporto tra il numero di frame con occhi chiusi e il numero totale di frame in un intervallo di tempo definito (tipicamente 60 secondi)

La formula utilizzata è:
```
PERCLOS = (Numero di frame con EAR < soglia / Numero totale di frame nell'intervallo) * 100
```

Ho stabilito un valore di soglia del 20% per il PERCLOS; valori superiori a questa soglia indicano uno stato di sonnolenza del conducente[3]. Questo approccio mi ha permesso di superare le limitazioni del semplice rilevamento della chiusura degli occhi, fornendo una misura più robusta e continua dello stato di vigilanza del conducente.

## Rilevamento della Distrazione e Orientamento della Testa

Per rilevare la distrazione del conducente, ho implementato un algoritmo di stima della posizione della testa basato sull'analisi dei punti di riferimento facciali. Questa metodologia consente di identificare quando lo sguardo del conducente non è rivolto alla strada, indicando potenziali distrazioni.

Il rilevamento dell'orientamento della testa si basa sui seguenti passaggi:

1. Estrazione dei punti di riferimento del naso utilizzando Mediapipe
2. Definizione di valori di riferimento per gli assi x, y e z in base alla posizione iniziale calibrata
3. Calcolo delle rotazioni della testa rispetto a questi valori di riferimento
4. Classificazione dell'orientamento della testa in cinque direzioni principali: sinistra, destra, su, giù e avanti

Per ogni frame, il sistema calcola gli angoli di rotazione (imbardata, beccheggio e rollio) della testa e li confronta con i valori di soglia predefiniti per determinare l'orientamento. Una deviazione significativa dalla posizione frontale viene classificata come potenziale distrazione[7].

Questa implementazione è conforme ai requisiti normativi che richiedono che i sistemi di rilevamento della distrazione siano in grado di identificare quando l'attenzione visiva del conducente si allontana dal compito di guida, attivandosi automaticamente quando la velocità del veicolo supera i 20 km/h[1].

## Rilevamento dello Sbadiglio

Per completare il sistema di monitoraggio, ho implementato anche un algoritmo per il rilevamento dello sbadiglio, un indicatore importante della sonnolenza. Il rilevamento si basa sul calcolo del Mouth Aspect Ratio (MAR), una metrica che quantifica l'apertura della bocca.

Per calcolare il MAR, ho utilizzato i seguenti punti di riferimento per la bocca:[291][181][17][269][405][7]

Ho stabilito un valore di soglia di 0,75 per il MAR; valori superiori a questa soglia indicano uno sbadiglio. Questo approccio mi ha permesso di rilevare efficacemente gli sbadigli, fornendo un indicatore aggiuntivo dello stato di sonnolenza del conducente.

## Conclusioni

Il sistema di monitoraggio del conducente implementato rappresenta un approccio completo per il rilevamento della sonnolenza e della distrazione alla guida. Attraverso l'uso combinato di metriche come EAR, PERCLOS, orientamento della testa e MAR, il sistema è in grado di fornire un monitoraggio affidabile dello stato del conducente, contribuendo potenzialmente alla riduzione degli incidenti stradali causati da fattori umani.

La metodologia adottata rispetta i requisiti di privacy e protezione dei dati, operando senza fare affidamento su dati biometrici personali degli occupanti del veicolo diversi dal conducente[1]. Inoltre, il sistema è progettato per funzionare in modo affidabile in diverse condizioni di illuminazione, garantendo prestazioni costanti sia di giorno che di notte.

Futuri sviluppi potrebbero includere l'integrazione di modelli di apprendimento automatico per migliorare ulteriormente l'accuratezza del sistema e l'implementazione di meccanismi di feedback adattivi che regolano le soglie in base alle caratteristiche individuali del conducente.
