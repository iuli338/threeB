import customtkinter as ctk
from PIL import Image
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import yagmail
import threading
import json
import sys
import os
from datetime import datetime

# --- CONFIGURARE ---
SENDER_EMAIL = "marzacristian42@gmail.com"
SENDER_PASSWORD = "ofye fkyu picr nzfc"
LOG_FILE = "quiz_logs.json"

TEXTS = {}

def load_texts():
    global TEXTS
    try:
        with open("texts.json", "r", encoding="utf-8") as f:
            TEXTS = json.load(f)
    except Exception as e:
        print(f"Error loading texts: {e}")
        TEXTS = {} # Fallback gol

# --- INTREBARI (CU LIMBA UCRAINEANĂ) ---
INTREBARI_DATA = [
    # CTI
    {"ro": "Îți place să rezolvi probleme logice complexe doar scriind cod?", "en": "Do you enjoy solving complex logical problems just by writing code?", "ua": "Вам подобається вирішувати складні логічні задачі за допомогою коду?", "wx": 1.0, "wy": 1.0},
    {"ro": "Ești pasionat de cum funcționează un site web, o bază de date sau un AI?", "en": "Are you passionate about how a website, database, or AI works?", "ua": "Ви захоплюєтеся тим, як працюють веб-сайти, бази даних або ШІ?", "wx": 1.0, "wy": 1.0},
    {"ro": "Preferi să lucrezi exclusiv pe calculator, fără să atingi fire sau piese?", "en": "Do you prefer working exclusively on a computer without touching wires or parts?", "ua": "Ви віддаєте перевагу роботі виключно за комп'ютером, не торкаючись дротів?", "wx": 1.0, "wy": 1.0},
    # AIA
    {"ro": "Vrei să programezi roboți fizici care se mișcă și interacționează cu lumea?", "en": "Do you want to program physical robots that move and interact with the world?", "ua": "Ви хочете програмувати фізичних роботів, які рухаються та взаємодіють зі світом?", "wx": -0.8, "wy": 1.0},
    {"ro": "Te interesează cum se automatizează o casă (Smart Home) sau o fabrică?", "en": "Are you interested in how to automate a house (Smart Home) or a factory?", "ua": "Вам цікаво, як автоматизувати будинок (Smart Home) або завод?", "wx": -0.5, "wy": 0.8},
    {"ro": "Îți place ideea de a combina programarea cu senzorii și motoarele?", "en": "Do you like the idea of combining programming with sensors and motors?", "ua": "Вам подобається ідея поєднання програмування з датчиками та моторами?", "wx": -0.5, "wy": 1.0},
    # ELECTRICĂ
    {"ro": "Ești curios cum se produce energia electrică (eoliană, solară, nucleară)?", "en": "Are you curious about how electricity is generated (wind, solar, nuclear)?", "ua": "Вам цікаво, як виробляється електроенергія (вітрова, сонячна, ядерна)?", "wx": -1.0, "wy": -1.0},
    {"ro": "Te fascinează motoarele electrice mari și infrastructura de înaltă tensiune?", "en": "Do large electric motors and high-voltage infrastructure fascinate you?", "ua": "Вас захоплюють великі електродвигуни та високовольтна інфраструктура?", "wx": -1.0, "wy": -1.0},
    {"ro": "Vrei să proiectezi instalații electrice pentru clădiri sau orașe?", "en": "Do you want to design electrical installations for buildings or cities?", "ua": "Ви хочете проектувати електричні установки для будівель або міст?", "wx": -1.0, "wy": -0.8},
    # ELECTRONICĂ
    {"ro": "Îți place să lipești piese mărunte pe plăci de circuite (cipuri, tranzistori)?", "en": "Do you like soldering small parts onto circuit boards (chips, transistors)?", "ua": "Вам подобається паяти дрібні деталі на платах (чіпи, транзистори)?", "wx": 1.0, "wy": -1.0},
    {"ro": "Ești curios cum funcționează semnalul 5G, Wi-Fi și antenele?", "en": "Are you curious about how 5G signals, Wi-Fi, and antennas work?", "ua": "Вам цікаво, як працюють сигнали 5G, Wi-Fi та антени?", "wx": 1.0, "wy": -0.8},
    {"ro": "Te pasionează prelucrarea semnalelor audio/video și microprocesoarele?", "en": "Are you passionate about audio/video signal processing and microprocessors?", "ua": "Ви захоплюєтеся обробкою аудіо/відео сигналів та мікропроцесорами?", "wx": 1.0, "wy": -0.8}
]

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
        elif x >= 0 and y < 0: return t["spec_etti"], t["desc_etti"]
        else: return t["spec_el"], t["desc_el"]

    @staticmethod
    def genereaza_grafic(x, y):
        plt.figure(figsize=(8, 8), dpi=90)
        plt.fill_between([0, 10], 0, 10, color='#E3F2FD', alpha=0.6)
        plt.fill_between([-10, 0], 0, 10, color='#F3E5F5', alpha=0.6)
        plt.fill_between([0, 10], -10, 0, color='#E0F2F1', alpha=0.6)
        plt.fill_between([-10, 0], -10, 0, color='#FFF3E0', alpha=0.6)
        
        plt.axhline(0, color='#546E7A', linewidth=1, linestyle='--')
        plt.axvline(0, color='#546E7A', linewidth=1, linestyle='--')
        plt.xlim(-11, 11); plt.ylim(-11, 11)
        
        font_style = {'weight': 'bold', 'size': 10, 'family': 'sans-serif'}
        plt.text(9, 9, "CTI\n(Soft & Data)", ha='right', va='top', color='#1565C0', **font_style)
        plt.text(-9, 9, "AIA\n(Robo & Sys)", ha='left', va='top', color='#6A1B9A', **font_style)
        plt.text(9, -9, "ETTI\n(Signal & Chips)", ha='right', va='bottom', color='#00695C', **font_style)
        plt.text(-9, -9, "ELECTRIC\n(Power & Grid)", ha='left', va='bottom', color='#EF6C00', **font_style)

        plt.scatter(x, y, s=300, c='#D32F2F', marker='X', edgecolors='white', linewidth=2, zorder=10)
        
        filename = "temp_chart.png"
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        return filename

    @staticmethod
    def genereaza_grafic_colectiv():
        points_x = []
        points_y = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for entry in data:
                        points_x.append(entry["coordonate"]["x"])
                        points_y.append(entry["coordonate"]["y"])
            except Exception: pass

        plt.figure(figsize=(8, 5.5), dpi=100)
        plt.fill_between([0, 10], 0, 10, color='#E3F2FD', alpha=0.6)
        plt.fill_between([-10, 0], 0, 10, color='#F3E5F5', alpha=0.6)
        plt.fill_between([0, 10], -10, 0, color='#E0F2F1', alpha=0.6)
        plt.fill_between([-10, 0], -10, 0, color='#FFF3E0', alpha=0.6)
        plt.axhline(0, color='#546E7A', linewidth=1, linestyle='--')
        plt.axvline(0, color='#546E7A', linewidth=1, linestyle='--')
        plt.xlim(-11, 11); plt.ylim(-11, 11)
        
        if points_x:
            plt.scatter(points_x, points_y, s=100, c='#1f6aa5', marker='o', alpha=0.6, edgecolors='white', linewidth=1, zorder=10)
        
        filename = "collective_stats.png"
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        return filename

    @staticmethod
    def salveaza_log_json(email, spec, x, y):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "email": email,
            "rezultat": spec,
            "coordonate": {"x": round(x, 2), "y": round(y, 2)}
        }
        data = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []
        data.append(entry)
        try:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Log Error: {e}")

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

# --- QUIZ VIEW CLASS (MODUL INTEGRAT) ---
class QuizView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.lang = "en" 
        self.backend = QuizBackend()
        self.user_answers = [] 
        self.current_question_index = 0
        self.current_var = ctk.IntVar(value=0)

        load_texts() 
        self.show_language_screen()

    def clean_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_language_screen(self):
        self.clean_frame()
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Engineering Compass", font=("Roboto", 32, "bold")).pack(pady=(0, 10))
        ctk.CTkLabel(frame, text="Select Language", font=("Arial", 14), text_color="gray").pack(pady=(0, 20))

        btn_style = {"width": 250, "height": 45, "font": ("Arial", 16, "bold"), "corner_radius": 22}
        
        ctk.CTkButton(frame, text="🇬🇧 ENGLISH", fg_color="#1f6aa5", command=lambda: self.set_lang("en"), **btn_style).pack(pady=8)
        ctk.CTkButton(frame, text="🇷🇴 ROMÂNĂ", fg_color="#e67e22", command=lambda: self.set_lang("ro"), **btn_style).pack(pady=8)
        # SCHIMBAT DIN RUSĂ ÎN UCRAINEANĂ
        ctk.CTkButton(frame, text="🇺🇦 УКРАЇНСЬКА", fg_color="#F1C40F", text_color="black", command=lambda: self.set_lang("ua"), **btn_style).pack(pady=8)

        # BUTON BACK TO HOME
        ctk.CTkButton(frame, text="⬅ HOME / MENIU", fg_color="transparent", border_width=1, border_color="white",
                      width=200, height=35, command=self.controller.show_home).pack(pady=(30, 0))

    def set_lang(self, lang_code):
        self.lang = lang_code
        self.start_quiz()

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

        card = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15, border_width=1, border_color="#3a3a3a")
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.9)

        prog_txt = t["progress"].format(self.current_question_index + 1, len(INTREBARI_DATA))
        ctk.CTkLabel(card, text=prog_txt, font=("Roboto Medium", 20), text_color="#1f6aa5").pack(pady=(30, 10))

        progress_val = (self.current_question_index + 1) / len(INTREBARI_DATA)
        pb = ctk.CTkProgressBar(card, width=300, height=6, corner_radius=3, progress_color="#1f6aa5")
        pb.pack(pady=(0, 15))
        pb.set(progress_val)

        q_text = INTREBARI_DATA[self.current_question_index][self.lang]
        ctk.CTkLabel(card, text=q_text, font=("Roboto Medium", 20), wraplength=600, justify="center").pack(pady=(20, 10))

        options_frame = ctk.CTkFrame(card, fg_color="transparent")
        options_frame.pack(pady=(30, 15))

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
        self.backend.salveaza_log_json(email, spec, x, y)
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

    def show_thank_you_screen(self, spec):
        self.clean_frame()
        t = TEXTS[self.lang]
        
        ctk.CTkLabel(self, text="✔", font=("Arial", 80), text_color="#00c853").pack(pady=(20, 10))
        ctk.CTkLabel(self, text=t["success_title"], font=("Roboto", 30, "bold")).pack()
        ctk.CTkLabel(self, text=spec, font=("Roboto", 18), text_color="#64b5f6").pack(pady=5)
        ctk.CTkLabel(self, text=t["check_email"], font=("Arial", 14), text_color="gray").pack(pady=10)

        # Buton Statistici
        ctk.CTkButton(self, text="📊 GLOBAL STATS", font=("Arial", 12, "bold"), height=35, width=200, corner_radius=18,
                      fg_color="#1f6aa5", hover_color="#144a75", command=self.show_statistics_screen).pack(pady=5)

        # Buton Noua Sesiune
        ctk.CTkButton(self, text=t["restart"], font=("Roboto Medium", 12), height=45, width=200, corner_radius=22,
                      fg_color="#333333", hover_color="#000000", command=self.show_language_screen).pack(pady=5)

        # --- BUTONUL NOU DE HOME ---
        ctk.CTkButton(self, text=t["back_home"], font=("Roboto Medium", 12), height=40, width=200, corner_radius=20,
                      fg_color="transparent", border_width=1, border_color="#555555", text_color="gray",
                      hover_color="#333333",
                      command=self.controller.show_home).pack(pady=10)

    def show_statistics_screen(self):
        self.clean_frame()
        img_path = self.backend.genereaza_grafic_colectiv()
        try:
            my_image = ctk.CTkImage(light_image=Image.open(img_path), dark_image=Image.open(img_path), size=(500, 340))
            ctk.CTkLabel(self, image=my_image, text="").pack(pady=10)
        except Exception as e:
            ctk.CTkLabel(self, text=f"Error: {e}").pack()

        ctk.CTkButton(self, text="BACK", font=("Arial", 12, "bold"), height=40, width=150, corner_radius=20,
                      fg_color="#333333", command=lambda: self.show_thank_you_screen("")).pack(pady=10)