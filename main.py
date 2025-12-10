import customtkinter as ctk
import cv2
import time
from PIL import Image, ImageTk
import os

class RaspberryPiFaceTracker(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configurări Fereastră ---
        self.title("RPi Tracker - Haar Cascade")
        self.geometry("800x480")
        ctk.set_appearance_mode("Dark")
        # Setăm fundalul negru, conform imaginii tale
        self.configure(fg_color="#000000") 

        # --- Configurări Detecție (Haar Cascade) ---
        # Încărcăm clasificatorul pre-antrenat din OpenCV
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("EROARE CRITICĂ: Nu s-a putut încărca fișierul XML Haar Cascade.")
            print("Verifică instalarea opencv-python.")
            exit()

        # --- Configurare Cameră (Rezoluție mică pentru RPi) ---
        self.cap = cv2.VideoCapture(1)
        # 320x240 este suficient pentru Haar și rulează rapid pe Pi
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        # --- Configurare UI ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Canvas principal (fundal negru)
        self.canvas = ctk.CTkCanvas(self, bg="#000000", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.status_label = ctk.CTkLabel(self, text="Initializare...", font=("Roboto", 14), text_color="#555555")
        self.status_label.grid(row=1, column=0, pady=(5, 10))

        # --- Încărcare Imagine Pupila (Din fișierul tău) ---
        # Salvăm imaginea ta ca 'pupil.png' în același folder cu scriptul
        image_path = "pupil.png" 
        if not os.path.exists(image_path):
            # Dacă nu găsește imaginea, creăm una temporară (un cerc albastru)
            # Asta e doar pentru test, ideal e să ai imaginea ta salvată.
            print("Imaginea 'pupil.png' nu a fost găsită. Se folosește un placeholder.")
            img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.ellipse((0, 0, 50, 50), fill="#3399ff")
            img.save(image_path)

        # Încărcăm imaginea și o convertim pentru Tkinter
        pil_img = Image.open(image_path).resize((50, 50), Image.LANCZOS)
        self.pupil_img_tk = ImageTk.PhotoImage(pil_img)
        self.pupil_radius = 25 # Jumătate din 50x50

        # --- Desenare Interfață Statică ---
        self.draw_face_elements()

        # --- Variabile de Urmărire și Animație ---
        self.target_pupil_x = 0
        self.target_pupil_y = 0
        self.current_pupil_x = 0
        self.current_pupil_y = 0
        # Pe Pi, o valoare mai mare poate ajuta la fluiditate dacă FPS-ul e mic
        self.smoothing_factor = 0.15 

        # Pornim bucla
        self.update_loop()

    def draw_face_elements(self):
        """Desenează contururile ochilor și plasează pupilele inițial."""
        self.update()
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        if cw < 100: cw = 800
        if ch < 100: ch = 600
        
        center_x, center_y = cw // 2, ch // 2

        # Configurare poziție ochi
        self.eye_offset_x = 90
        self.eye_pos_y = center_y - 30
        eye_radius = 60 # Raza cercurilor mari albastre
        
        # Culoarea albastră din imaginea ta
        blue_color = "#3399ff" 

        # Centrul Ochiului Stâng
        self.eye_l_center = (center_x - self.eye_offset_x, self.eye_pos_y)
        # Desenăm conturul albastru (ochiul mare)
        self.canvas.create_oval(
            self.eye_l_center[0] - eye_radius, self.eye_l_center[1] - eye_radius,
            self.eye_l_center[0] + eye_radius, self.eye_l_center[1] + eye_radius,
            outline=blue_color, width=8
        )

        # Centrul Ochiului Drept
        self.eye_r_center = (center_x + self.eye_offset_x, self.eye_pos_y)
        # Desenăm conturul albastru
        self.canvas.create_oval(
            self.eye_r_center[0] - eye_radius, self.eye_r_center[1] - eye_radius,
            self.eye_r_center[0] + eye_radius, self.eye_r_center[1] + eye_radius,
            outline=blue_color, width=8
        )

        # --- Plasăm imaginile pupilelor în centru ---
        # create_image folosește centrul imaginii ca punct de ancorare
        self.pupil_l_id = self.canvas.create_image(
            self.eye_l_center[0], self.eye_l_center[1],
            image=self.pupil_img_tk, anchor="center"
        )
        self.pupil_r_id = self.canvas.create_image(
            self.eye_r_center[0], self.eye_r_center[1],
            image=self.pupil_img_tk, anchor="center"
        )

        # Limite de mișcare (câți pixeli se pot deplasa pupilele)
        self.max_eye_movement_x = 30
        self.max_eye_movement_y = 20

    def update_loop(self):
        # 1. Citire Cameră și Procesare (Haar Cascade)
        ret, frame = self.cap.read()
        
        face_center_x_norm = 0.5
        face_center_y_norm = 0.5
        person_count = 0
        detected = False

        if ret:
            # Oglindire
            frame = cv2.flip(frame, 1)
            
            # Haar funcționează pe imagini Grayscale (alb-negru)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # --- DETECȚIA PROPRIU-ZISĂ ---
            # scaleFactor=1.2, minNeighbors=4: Parametri buni pentru viteză pe Pi
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.2, 
                minNeighbors=4, 
                minSize=(30, 30)
            )

            if len(faces) > 0:
                detected = True
                person_count = len(faces)
                
                # Luăm prima față detectată (cea mai mare de obicei)
                (x, y, w, h) = faces[0]
                
                # Dimensiunile cadrului video (320x240)
                frame_h, frame_w = frame.shape[:2]
                
                # Calculăm centrul feței și îl normalizăm (0.0 - 1.0)
                face_center_x = x + w / 2
                face_center_y = y + h / 2
                
                face_center_x_norm = face_center_x / frame_w
                face_center_y_norm = face_center_y / frame_h

        # 2. Logică UI și Calcul Țintă
        if detected:
            self.status_label.configure(text=f"Stare: Urmaresc ({person_count} persoane)", text_color="#3399ff")
            
            # Calculăm noua poziție țintă (offset față de centru)
            # (valoare_norm - 0.5) variază de la -0.5 la +0.5
            # Înmulțim cu 2 * max_movement pentru a obține range-ul complet de pixeli (-max la +max)
            self.target_pupil_x = (face_center_x_norm - 0.5) * 2 * self.max_eye_movement_x
            self.target_pupil_y = (face_center_y_norm - 0.5) * 2 * self.max_eye_movement_y
            
        else:
            self.status_label.configure(text="Stare: Asteptare...", text_color="#555555")
            # Revenire la centru
            self.target_pupil_x = 0
            self.target_pupil_y = 0

        # 3. Animație Fluidă (Lerp)
        self.current_pupil_x += (self.target_pupil_x - self.current_pupil_x) * self.smoothing_factor
        self.current_pupil_y += (self.target_pupil_y - self.current_pupil_y) * self.smoothing_factor

        # 4. Mutare Imagini Pupile
        # Calculăm noile coordonate absolute pentru centrul imaginii
        new_pl_x = self.eye_l_center[0] + self.current_pupil_x
        new_pl_y = self.eye_l_center[1] + self.current_pupil_y
        
        new_pr_x = self.eye_r_center[0] + self.current_pupil_x
        new_pr_y = self.eye_r_center[1] + self.current_pupil_y

        # Folosim canvas.coords pentru a muta imaginile
        self.canvas.coords(self.pupil_l_id, new_pl_x, new_pl_y)
        self.canvas.coords(self.pupil_r_id, new_pr_x, new_pr_y)

        # Reapelare buclă (~30 FPS țintă)
        self.after(33, self.update_loop)

    def close_app(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    # Asigură-te că ai salvat imaginea ta ca 'pupil.png' înainte de a rula
    app = RaspberryPiFaceTracker()
    app.protocol("WM_DELETE_WINDOW", app.close_app)
    app.mainloop()