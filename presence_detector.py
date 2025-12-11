import cv2
import time
import sys
import traceback
import os

# --- CONFIGURARE HARDWARE ---
USE_RASPBERRY_PI = True  
FACE_AREA_THRESHOLD = 0.25 
TIME_TO_TRIGGER = 1.0
CASCADE_FILENAME = "haarcascade_frontalface_default.xml"

class PresenceDetector:
    def __init__(self, on_detect_callback=None, show_preview=True):
        """
        :param show_preview: Dacă True, deschide o fereastră externă cu feed-ul camerei.
        """
        self.on_detect_callback = on_detect_callback
        self.show_preview = show_preview  # Variabila de control
        self.running = False
        self.cascade_loaded = False
        
        # Verificare existență fișier
        if not os.path.exists(CASCADE_FILENAME):
            print(f"!!! EROARE CRITICĂ: Fișierul '{CASCADE_FILENAME}' lipsește!")
            return

        self.face_cascade = cv2.CascadeClassifier(CASCADE_FILENAME)
        if self.face_cascade.empty():
            print("!!! EROARE: Nu s-a putut încărca clasificatorul XML.")
        else:
            self.cascade_loaded = True

        self.start_look_time = None
        self.action_triggered = False
        self.camera = None
        self.raw_capture = None

    def _init_camera(self):
        print(f"Inițializare cameră (Preview={self.show_preview})...")
        if USE_RASPBERRY_PI:
            try:
                from picamera import PiCamera
                from picamera.array import PiRGBArray
                self.camera = PiCamera()
                self.camera.resolution = (320, 240)
                self.camera.framerate = 30
                self.raw_capture = PiRGBArray(self.camera, size=(320, 240))
                time.sleep(0.1)
                return True
            except ImportError:
                print("Eroare: Modulul 'picamera' nu este instalat.")
                return False
        else:
            self.camera = cv2.VideoCapture(1)
            if not self.camera.isOpened():
                print("Eroare: Nu se poate deschide camera web.")
                return False
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            return True

    def process_frame(self, frame):
        if frame is None or frame.size == 0:
            return

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if not self.cascade_loaded:
                return

            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            frame_height, frame_width = frame.shape[:2]
            total_area = frame_width * frame_height
            face_found_close = False

            # Procesare fețe
            for (x, y, w, h) in faces:
                # Dacă preview este activ, desenăm dreptunghiul
                if self.show_preview:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                face_area = w * h
                ratio = face_area / total_area
                
                # Afișăm procentul pe ecran dacă preview este activ
                if self.show_preview:
                    cv2.putText(frame, f"Ratio: {ratio:.2f}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                if ratio >= FACE_AREA_THRESHOLD:
                    face_found_close = True
                    # Luăm doar prima față relevantă
                    break

            # Logică Trigger
            if face_found_close:
                if self.start_look_time is None:
                    self.start_look_time = time.time()
                
                if (time.time() - self.start_look_time) >= TIME_TO_TRIGGER:
                    if not self.action_triggered:
                        if self.on_detect_callback:
                            print(">> PREZENȚĂ CONFIRMATĂ! Activare callback.")
                            self.on_detect_callback()
                        self.action_triggered = True
                        
                    # Feedback vizual pentru trigger
                    if self.show_preview:
                        cv2.circle(frame, (30, 30), 20, (0, 0, 255), -1) 
            else:
                self.start_look_time = None
                self.action_triggered = False

            # Afișare fereastră preview
            if self.show_preview:
                cv2.imshow("Camera Preview (Debug)", frame)
                # cv2.waitKey(1) este esențial pentru ca fereastra să se randeze
                cv2.waitKey(1)

        except Exception as e:
            print(f"Eroare în process_frame: {e}")
            traceback.print_exc()

    def start(self):
        if not self.cascade_loaded or not self._init_camera():
            return

        self.running = True
        print("Detector running...")

        try:
            if USE_RASPBERRY_PI:
                from picamera.array import PiRGBArray
                for frame_pi in self.camera.capture_continuous(self.raw_capture, format="bgr", use_video_port=True):
                    if not self.running: break
                    self.process_frame(frame_pi.array)
                    self.raw_capture.truncate(0)
            else:
                while self.running:
                    ret, frame = self.camera.read()
                    if ret:
                        self.process_frame(frame)
                    else:
                        time.sleep(0.1)
        except Exception as e:
            print(f"Eroare loop: {e}")
        finally:
            self._cleanup()

    def stop(self):
        self.running = False

    def _cleanup(self):
        print("Oprire detector...")
        if self.show_preview:
            cv2.destroyAllWindows()
            
        if USE_RASPBERRY_PI and self.camera:
            try: self.camera.close()
            except: pass
        elif not USE_RASPBERRY_PI and self.camera:
            self.camera.release()