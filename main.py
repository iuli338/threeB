import cv2
import mediapipe as mp
import time

# Folosim Face Detection care este disponibil în versiunea ta
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(1)

# Setări rezoluție (opțional, pentru claritate)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Variabile FPS
prev_time = 0
curr_time = 0
font = cv2.FONT_HERSHEY_SIMPLEX

# Inițializăm Face Detection
# min_detection_confidence: 0.5 (50% siguranță)
# model_selection: 0 pentru distanțe mici (selfie), 1 pentru distanțe mai mari (cameră cameră)
with mp_face_detection.FaceDetection(
    model_selection=1, 
    min_detection_confidence=0.5) as face_detection:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignorare cadru gol.")
            continue

        # Optimizare
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Procesare
        results = face_detection.process(image_rgb)

        # Revenire la BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        person_count = 0
        h, w, _ = image.shape

        if results.detections:
            for detection in results.detections:
                person_count += 1
                
                # Extragem cutia (bounding box) pentru fiecare față detectată
                bboxC = detection.location_data.relative_bounding_box
                
                x_min = int(bboxC.xmin * w)
                y_min = int(bboxC.ymin * h)
                width = int(bboxC.width * w)
                height = int(bboxC.height * h)

                # Desenăm dreptunghiul (Box)
                # Dacă detectăm o față, presupunem că există o persoană
                cv2.rectangle(image, (x_min, y_min), (x_min + width, y_min + height), (0, 255, 0), 2)
                
                # Afișăm scorul
                score = detection.score[0]
                label_text = f"Persoana {person_count}"
                cv2.putText(image, label_text, (x_min, y_min - 10), font, 0.6, (0, 255, 0), 2)

        # ---------------------------------------------------------
        # Calcul FPS & Dashboard
        # ---------------------------------------------------------
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time

        # Panou informații
        cv2.rectangle(image, (0, 0), (350, 80), (0, 0, 0), -1)
        
        cv2.putText(image, f'FPS: {int(fps)}', (10, 30), font, 1, (255, 255, 255), 2)
        
        color_status = (0, 255, 0) if person_count > 0 else (0, 0, 255)
        cv2.putText(image, f'DETECTAT: {person_count} Persoane', (10, 65), font, 0.8, color_status, 2)

        cv2.imshow('Multi-Person Detection (Face)', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()