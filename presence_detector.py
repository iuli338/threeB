import cv2
import time
import sys
import traceback
import os
import threading

# --- CONFIGURARE HARDWARE ---
USE_RASPBERRY_PI = False  # Setează True pentru Raspberry Pi (folosind Picamera2)
FACE_AREA_THRESHOLD = 0.50 
TIME_TO_TRIGGER = 1.0
CASCADE_FILENAME = "haarcascade_frontalface_default.xml"

class PresenceDetector:
    def __init__(self, on_detect_callback=None, show_preview=True):
        """
        :param on_detect_callback: Funcția apelată la detectarea prezenței.
        :param show_preview: Dacă True, afișează fereastra de debug.
        """
        self.on_detect_callback = on_detect_callback
        self.show_preview = show_preview
        self.running = False
        self.cascade_loaded = False
        
        # Verificare fișier XML
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
        
        # Variabila pentru raw_capture nu mai este necesară la Picamera2 în același mod,
        # dar o păstrăm null pentru compatibilitate logică.
        self.raw_capture = None

    def _init_camera(self):
        print(f"Inițializare cameră (Pi={USE_RASPBERRY_PI}, Preview={self.show_preview})...")
        
        if USE_RASPBERRY_PI:
            try:
                # --- IMPLEMENTARE PICAMERA2 ---
                from picamera2 import Picamera2
                
                self.camera = Picamera2()
                
                # Configurăm o rezoluție mică pentru performanță (320x240)
                # Formatul 'RGB888' este standard, vom converti la BGR pentru OpenCV
                config = self.camera.create_configuration(main={"size": (320, 240), "format": "RGB888"})
                self.camera.configure(config)
                self.camera.start() # Pornim motorul camerei
                
                print("Picamera2 inițializată cu succes.")
                return True
                
            except ImportError:
                print("Eroare: Biblioteca 'picamera2' nu este instalată (sudo apt install python3-picamera2).")
                return False
            except Exception as e:
                print(f"Eroare la inițializarea Picamera2: {e}")
                traceback.print_exc()
                return False
        else:
            # --- IMPLEMENTARE WINDOWS / USB WEBCAM ---
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("Eroare: Nu se poate deschide camera web (USB).")
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

            for (x, y, w, h) in faces:
                if self.show_preview:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                face_area = w * h
                ratio = face_area / total_area
                
                if self.show_preview:
                    cv2.putText(frame, f"Ratio: {ratio:.2f}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                if ratio >= FACE_AREA_THRESHOLD:
                    face_found_close = True
                    break

            # Logica de timp / trigger
            if face_found_close:
                if self.start_look_time is None:
                    self.start_look_time = time.time()
                
                if (time.time() - self.start_look_time) >= TIME_TO_TRIGGER:
                    if not self.action_triggered:
                        if self.on_detect_callback:
                            print(">> PREZENȚĂ CONFIRMATĂ! Activare callback.")
                            self.on_detect_callback()
                        self.action_triggered = True
                        
                    if self.show_preview:
                        cv2.circle(frame, (30, 30), 20, (0, 0, 255), -1) 
            else:
                self.start_look_time = None
                self.action_triggered = False

            if self.show_preview:
                cv2.imshow("Camera Preview (Debug)", frame)
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
                # --- LOOP PENTRU PICAMERA2 ---
                while self.running:
                    # Capturăm imaginea ca array NumPy
                    frame_rgb = self.camera.capture_array()
                    
                    # Picamera2 returnează RGB, OpenCV vrea BGR. Facem conversia.
                    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                    
                    self.process_frame(frame_bgr)
                    
                    # O mică pauză pentru a nu bloca CPU-ul complet, deși capture_array e sincron
                    time.sleep(0.01)
            else:
                # --- LOOP PENTRU WINDOWS ---
                while self.running:
                    ret, frame = self.camera.read()
                    if ret:
                        self.process_frame(frame)
                    else:
                        time.sleep(0.1)
                        
        except Exception as e:
            print(f"Eroare loop principal: {e}")
            traceback.print_exc()
        finally:
            self._cleanup()

    def stop(self):
        self.running = False

    def _cleanup(self):
        print("Oprire detector...")
        if self.show_preview:
            cv2.destroyAllWindows()
            
        if USE_RASPBERRY_PI and self.camera:
            try:
                self.camera.stop()
                # self.camera.close() # Picamera2 nu are neapărat nevoie de close explicit la final de script, dar stop e bun.
            except Exception as e:
                print(f"Eroare la oprirea camerei: {e}")
        elif not USE_RASPBERRY_PI and self.camera:
            self.camera.release()

if __name__ == "__main__":
    # Testare individuală
    print("Testare modul PresenceDetector...")
    det = PresenceDetector(show_preview=True)
    try:
        det.start()
    except KeyboardInterrupt:
        det.stop()