import customtkinter as ctk
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import yagmail
import threading
import json
import sys

# --- CONFIGURARE ---
SENDER_EMAIL = "marzacristian42@gmail.com"
SENDER_PASSWORD = "ofye fkyu picr nzfc"

# Variabila globală pentru texte
TEXTS = {}

# --- ÎNCĂRCARE JSON ---
def load_texts():
    global TEXTS
    try:
        with open("texts.json", "r", encoding="utf-8") as f:
            TEXTS = json.load(f)
    except FileNotFoundError:
        print("❌ EROARE: Fișierul 'texts.json' lipsește!")
        sys.exit()
    except json.JSONDecodeError:
        print("❌ EROARE: Format JSON invalid.")
        sys.exit()

# --- BAZA DE DATE ÎNTREBĂRI ---
INTREBARI_DATA = [
    {"ro": "Îți place să rezolvi probleme logice complexe scriind cod?", "en": "Do you enjoy solving complex logical problems by writing code?", "ru": "Вам нравится решать сложные логические задачи с помощью кода?", "wx": 1.0, "wy": 1.0},
    {"ro": "Ești pasionat de Inteligența Artificială și baze de date?", "en": "Are you passionate about Artificial Intelligence and databases?", "ru": "Вы увлекаетесь искусственным интеллектом и базами данных?", "wx": 1.0, "wy": 1.0},
    {"ro": "Preferi să dezvolți aplicații software decât să construiești aparate fizice?", "en": "Do you prefer developing software apps over building physical devices?", "ru": "Вы предпочитаете разрабатывать ПО, а не строить физические устройства?", "wx": 1.0, "wy": 1.0},
    {"ro": "Te fascinează ideea de a programa roboți care se mișcă autonom?", "en": "Does the idea of programming autonomous robots fascinate you?", "ru": "Вас увлекает идея программирования автономных роботов?", "wx": -0.8, "wy": 1.0},
    {"ro": "Îți place să înțelegi cum senzorii controlează o linie de producție?", "en": "Do you like understanding how sensors control a production line?", "ru": "Вам нравится разбираться, как датчики управляют производственной линией?", "wx": -0.5, "wy": 0.8},
    {"ro": "Matematica sistemelor și teoria controlului ți se par interesante?", "en": "Do systems mathematics and control theory seem interesting to you?", "ru": "Вам интересна математика систем и теория управления?", "wx": -0.5, "wy": 1.0},
    {"ro": "Îți place să construiești circuite și să lipești componente electronice?", "en": "Do you like building circuits and soldering electronic components?", "ru": "Вам нравится собирать схемы и паять электронные компоненты?", "wx": 1.0, "wy": -1.0},
    {"ro": "Ești curios cum funcționează rețelele de înaltă tensiune și generatoarele?", "en": "Are you curious about how high voltage grids and generators work?", "ru": "Вам интересно, как работают высоковольтные сети и генераторы?", "wx": 1.0, "wy": -1.0},
    {"ro": "Preferi hardware-ul și microcipurile în locul programării pure?", "en": "Do you prefer hardware and microchips over pure programming?", "ru": "Вы предпочитаете аппаратное обеспечение и микрочипы чистому программированию?", "wx": 1.0, "wy": -0.8},
    {"ro": "Ești pasionat de motoare, angrenajele și sisteme de transmisie?", "en": "Are you passionate about engines, gears, and transmission systems?", "ru": "Вы увлекаетесь двигателями, шестернями и системами передач?", "wx": -1.0, "wy": -1.0},
    {"ro": "Îți place să proiectezi piese 3D și să analizezi rezistența materialelor?", "en": "Do you like designing 3D parts and analyzing material strength?", "ru": "Вам нравится проектировать 3D-детали и анализировать прочность материалов?", "wx": -1.0, "wy": -1.0},
    {"ro": "Te interesează aerodinamica și mecanica fluidelor?", "en": "Are you interested in aerodynamics and fluid mechanics?", "ru": "Вам интересна аэродинамика и механика жидкостей?", "wx": -1.0, "wy": -1.0}
]

# --- BACKEND ---
class QuizBackend:
    @staticmethod
    def calculeaza_coordonate(raspunsuri):
        x_score = 0
        y_score = 0
        for i, val in enumerate(raspunsuri):
            weight = val - 3 
            q_data = INTREBARI_DATA[i]
            x_score += weight * q_data["wx"]
            y_score += weight * q_data["wy"]
        x_final = max(-10, min(10, x_score * 0.8))
        y_final = max(-10, min(10, y_score * 0.8))
        return x_final, y_final

    @staticmethod
    def obtine_rezultat_text(x, y, lang):
        t = TEXTS[lang]
        if x >= 0 and y >= 0: return t["spec_cti"], t["desc_cti"]
        elif x < 0 and y >= 0: return t["spec_aia"], t["desc_aia"]
        elif x >= 0 and y < 0: return t["spec_el"], t["desc_el"]
        else: return t["spec_mec"], t["desc_mec"]

    @staticmethod
    def genereaza_grafic(x, y):
        plt.figure(figsize=(8, 8), dpi=90) # DPI puțin mai mic pentru viteză pe Pi
        plt.fill_between([0, 10], 0, 10, color='#E3F2FD', alpha=0.6)
        plt.fill_between([-10, 0], 0, 10, color='#F3E5F5', alpha=0.6)
        plt.fill_between([0, 10], -10, 0, color='#FFF8E1', alpha=0.6)
        plt.fill_between([-10, 0], -10, 0, color='#FFEBEE', alpha=0.6)
        
        plt.axhline(0, color='#546E7A', linewidth=1, linestyle='--')
        plt.axvline(0, color='#546E7A', linewidth=1, linestyle='--')
        plt.xlim(-11, 11); plt.ylim(-11, 11)
        
        font_style = {'weight': 'bold', 'size': 11, 'family': 'sans-serif'}
        plt.text(9, 9, "SOFTWARE", ha='right', va='top', color='#1565C0', **font_style)
        plt.text(-9, 9, "ROBOTICS", ha='left', va='top', color='#6A1B9A', **font_style)
        plt.text(9, -9, "HARDWARE", ha='right', va='bottom', color='#EF6C00', **font_style)
        plt.text(-9, -9, "MECHANICS", ha='left', va='bottom', color='#C62828', **font_style)

        plt.scatter(x, y, s=300, c='#00C853', marker='X', edgecolors='white', linewidth=2, zorder=10)
        
        filename = "temp_chart.png"
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        return filename

    @staticmethod
    def trimite_mail(email, lang, x, y, spec, desc, path):
        t = TEXTS[lang]
        sub = t["email_sub"]
        msg = t["email_body"].format(spec, desc, x, y)
        try:
            yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
            yag.send(to=email, subject=sub, contents=msg, attachments=[path])
            return True, ""
        except Exception as e:
            return False, str(e)

# --- GUI ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Engineering Compass")
        
        # --- REZOLUȚIE FIXĂ PENTRU ECRAN 7 INCH ---
        self.geometry("800x480")
        
        ctk.set_appearance_mode("Dark") 
        ctk.set_default_color_theme("dark-blue")

        self.lang = "en" 
        self.backend = QuizBackend()
        self.user_answers = [] 
        self.current_question_index = 0
        self.current_var = ctk.IntVar(value=0)

        load_texts() # Încărcăm textele din JSON
        self.show_language_screen()

    def clean_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    # --- 1. LANGUAGE SCREEN ---
    def show_language_screen(self):
        self.clean_frame()
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Fonturi mai mici pentru 480p
        ctk.CTkLabel(frame, text="Engineering Compass", font=("Roboto", 32, "bold")).pack(pady=(0, 10))
        ctk.CTkLabel(frame, text="Select Language / Alege Limba", font=("Arial", 14), text_color="gray").pack(pady=(0, 20))

        btn_style = {"width": 250, "height": 45, "font": ("Arial", 16, "bold"), "corner_radius": 22}
        
        ctk.CTkButton(frame, text="🇬🇧 ENGLISH", fg_color="#1f6aa5", command=lambda: self.set_lang("en"), **btn_style).pack(pady=8)
        ctk.CTkButton(frame, text="🇷🇴 ROMÂNĂ", fg_color="#e67e22", command=lambda: self.set_lang("ro"), **btn_style).pack(pady=8)
        ctk.CTkButton(frame, text="🇷🇺 РУССКИЙ", fg_color="#c0392b", command=lambda: self.set_lang("ru"), **btn_style).pack(pady=8)

    def set_lang(self, lang_code):
        self.lang = lang_code
        self.start_quiz()

    # --- 2. QUESTION SCREEN ---
    def start_quiz(self):
        self.current_question_index = 0
        self.user_answers = []
        self.show_question_page()

    def show_question_page(self):
        self.clean_frame()
        self.current_var = ctk.IntVar(value=0)
        t = TEXTS[self.lang] 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Cardul este mai lat (85%) și mai înalt (90%) pentru a profita de ecranul mic
        card = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15, border_width=1, border_color="#3a3a3a")
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.9)

        # Header Progres
        prog_txt = t["progress"].format(self.current_question_index + 1, len(INTREBARI_DATA))
        ctk.CTkLabel(card, text=prog_txt, font=("Roboto Medium", 12), text_color="#1f6aa5").pack(pady=(15, 2))

        progress_val = (self.current_question_index + 1) / len(INTREBARI_DATA)
        pb = ctk.CTkProgressBar(card, width=300, height=6, corner_radius=3, progress_color="#1f6aa5")
        pb.pack(pady=(0, 15))
        pb.set(progress_val)

        # --- TEXT WRAPPING ---
        # Aici este magia: wraplength=600 face ca textul să treacă pe rândul următor
        q_text = INTREBARI_DATA[self.current_question_index][self.lang]
        ctk.CTkLabel(card, text=q_text, 
                     font=("Roboto Medium", 20), # Font redus
                     wraplength=600,             # Forțează trecerea pe rândul 2
                     justify="center").pack(pady=10)

        # Opțiuni
        options_frame = ctk.CTkFrame(card, fg_color="transparent")
        options_frame.pack(pady=15)

        # Labels DA/NU mai mici
        ctk.CTkLabel(options_frame, text=t["no"], font=("Arial", 12, "bold"), text_color="#e57373").pack(side="left", padx=10)

        for val in range(1, 6):
            btn = ctk.CTkRadioButton(options_frame, text=str(val), variable=self.current_var, value=val,
                                     width=24, height=24, border_width_checked=8, border_width_unchecked=2,
                                     font=("Arial", 14, "bold"), fg_color="#1f6aa5", hover_color="#144a75")
            btn.pack(side="left", padx=10)

        ctk.CTkLabel(options_frame, text=t["yes"], font=("Arial", 12, "bold"), text_color="#81c784").pack(side="left", padx=10)

        self.error_label = ctk.CTkLabel(card, text="", text_color="#ff5252", font=("Arial", 12))
        self.error_label.pack(pady=(5, 2))

        ctk.CTkButton(card, text=t["next"], font=("Roboto Medium", 14), height=40, width=180, corner_radius=20,
                      fg_color="#1f6aa5", hover_color="#144a75", command=self.next_step).pack(pady=10)

    def next_step(self):
        val = self.current_var.get()
        if val == 0:
            self.error_label.configure(text=TEXTS[self.lang]["error_sel"])
            return
        self.user_answers.append(val)
        self.current_question_index += 1
        
        if self.current_question_index < len(INTREBARI_DATA):
            self.show_question_page()
        else:
            self.show_email_page()

    # --- 3. EMAIL SCREEN ---
    def show_email_page(self):
        self.clean_frame()
        t = TEXTS[self.lang]

        card = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15, border_width=1, border_color="#3a3a3a")
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)

        ctk.CTkLabel(card, text=t["done_title"], font=("Roboto", 26, "bold")).pack(pady=(30, 10))
        ctk.CTkLabel(card, text=t["ask_email"], font=("Roboto", 16), text_color="gray").pack(pady=(0, 20))

        self.email_entry = ctk.CTkEntry(card, placeholder_text=t["placeholder_email"], width=300, height=45, font=("Arial", 16), corner_radius=10)
        self.email_entry.pack(pady=10)

        self.loading_bar = ctk.CTkProgressBar(card, width=300, mode="indeterminate", progress_color="#00c853")
        self.status_label = ctk.CTkLabel(card, text="", text_color="#ff5252")
        self.status_label.pack(pady=5)

        self.submit_btn = ctk.CTkButton(card, text=t["submit_btn"], font=("Roboto Medium", 14), height=50, width=220, corner_radius=25,
                                        fg_color="#00c853", hover_color="#009624", command=self.on_finalize)
        self.submit_btn.pack(pady=20)

    def on_finalize(self):
        email = self.email_entry.get().strip()
        if "@" not in email:
            self.status_label.configure(text=TEXTS[self.lang]["error_email"])
            return

        self.submit_btn.configure(state="disabled", text=TEXTS[self.lang]["processing"])
        self.loading_bar.pack(pady=10)
        self.loading_bar.start()

        threading.Thread(target=self.process_backend, args=(self.user_answers, email), daemon=True).start()

    def process_backend(self, raspunsuri, email):
        x, y = self.backend.calculeaza_coordonate(raspunsuri)
        spec, desc = self.backend.obtine_rezultat_text(x, y, self.lang)
        path = self.backend.genereaza_grafic(x, y)
        success, err = self.backend.trimite_mail(email, self.lang, x, y, spec, desc, path)
        self.after(0, lambda: self.finish_process(success, spec, err))

    def finish_process(self, success, spec, err):
        self.loading_bar.stop()
        if success:
            self.show_thank_you_screen(spec)
        else:
            self.submit_btn.configure(state="normal", text="RETRY")
            self.loading_bar.pack_forget()
            self.status_label.configure(text=f"Error: {err}")

    # --- 4. THANK YOU SCREEN ---
    def show_thank_you_screen(self, spec):
        self.clean_frame()
        t = TEXTS[self.lang]
        
        # Checkmark mai mic pentru ecran 480p
        ctk.CTkLabel(self, text="✔", font=("Arial", 80), text_color="#00c853").pack(pady=(40, 10))
        ctk.CTkLabel(self, text=t["success_title"], font=("Roboto", 30, "bold")).pack()
        ctk.CTkLabel(self, text=spec, font=("Roboto", 20), text_color="#64b5f6").pack(pady=15)
        ctk.CTkLabel(self, text=t["check_email"], font=("Arial", 14), text_color="gray").pack(pady=20)

        ctk.CTkButton(self, text=t["restart"], font=("Roboto Medium", 12), height=45, width=200, corner_radius=22,
                      fg_color="#333333", hover_color="#000000", command=self.show_language_screen).pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()