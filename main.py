import customtkinter as ctk
import threading
from assistant import UniversityAI
from tts_manager import TTSManager
import sys

# --- CONFIGURĂRI GLOBALE ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Definim Temele (Culori similare cu versiunea Flet)
THEMES = {
    1: { # ANA (Standard)
        "name": "Standard",
        "bg_color": "#121212",
        "chat_bg": "#1a1a1a",
        "input_bg": "#262626",
        "user_bubble": "#262626",
        "ai_bubble": "#0D47A1", # Blue 900
        "accent": "#42A5F5",    # Blue 400
        "font": "Roboto Medium",
        "btn_hover": "#1565C0"
    },
    2: { # PROFESOR
        "name": "Profesor",
        "bg_color": "#1B3A28",  # Dark Green
        "chat_bg": "#142c1f",
        "input_bg": "#2E5A43",
        "user_bubble": "#2E5A43",
        "ai_bubble": "#3E2723", # Brownish
        "accent": "#FFCA28",    # Amber
        "font": "Times New Roman", # Serif-like
        "btn_hover": "#F57F17"
    },
    3: { # STUDENT
        "name": "Student",
        "bg_color": "#1A0B2E",  # Deep Purple
        "chat_bg": "#120621",
        "input_bg": "#2D1B4E",
        "user_bubble": "#2D1B4E",
        "ai_bubble": "#4A148C", # Purple
        "accent": "#EC407A",    # Pink
        "font": "Consolas",     # Monospace
        "btn_hover": "#AD1457"
    }
}

class ChatBubble(ctk.CTkFrame):
    """Widget personalizat pentru bula de chat"""
    def __init__(self, master, text, sender, theme_id, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = THEMES[theme_id]
        
        # Configurare culori și aliniere
        if sender == "AI":
            bg_color = self.theme["ai_bubble"]
            text_color = "white"
            anchor = "w"  # West (Stânga)
            self.configure(fg_color=bg_color, corner_radius=15)
        else:
            bg_color = self.theme["user_bubble"]
            text_color = "white"
            anchor = "e"  # East (Dreapta)
            self.configure(fg_color=bg_color, corner_radius=15)

        # Label pentru Text (cu Wrapping)
        self.lbl_text = ctk.CTkLabel(
            self,
            text=text,
            text_color=text_color,
            font=(self.theme["font"], 14),
            wraplength=450,  # Lățime maximă înainte de a trece pe rând nou
            justify="left"
        )
        self.lbl_text.pack(padx=15, pady=10)

class ThreebApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Logică Backend ---
        try:
            self.ai = UniversityAI()
        except:
            self.ai = None
        self.tts = TTSManager()
        
        # Stare
        self.current_mode = 1
        self.voice_enabled = True

        # --- Configurare Fereastră ---
        self.title("THREEB Assistant")
        self.geometry("800x600")
        
        # Configurare Grid Principal (1 coloană, mai multe rânduri)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Chat-ul ocupă tot spațiul liber

        # ================= HEADER =================
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1) # Titlul la mijloc

        # Icon (Simulat text)
        self.lbl_icon = ctk.CTkLabel(self.header_frame, text="🤖", font=("Arial", 24))
        self.lbl_icon.grid(row=0, column=0, padx=15, pady=10)

        # Titlu
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="THREEB", font=("Roboto Medium", 20, "bold"))
        self.lbl_title.grid(row=0, column=1, sticky="w")

        # Buton Voce
        self.btn_voice = ctk.CTkButton(
            self.header_frame, text="🔊", width=40, command=self.toggle_voice,
            fg_color="transparent", hover_color="#333", font=("Arial", 20)
        )
        self.btn_voice.grid(row=0, column=2, padx=5)

        # Buton Close
        self.btn_close = ctk.CTkButton(
            self.header_frame, text="✕", width=40, command=self.destroy,
            fg_color="transparent", hover_color="#C62828", text_color="red", font=("Arial", 18, "bold")
        )
        self.btn_close.grid(row=0, column=3, padx=(5, 15))

        # ================= BUTOANE PERSONALITATE =================
        self.persona_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.persona_frame.grid(row=0, column=0, sticky="s", pady=(50, 5)) # Suprapus ușor peste header sau sub

        self.btn_p1 = self.create_persona_btn("Standard", 1)
        self.btn_p2 = self.create_persona_btn("Profesor", 2)
        self.btn_p3 = self.create_persona_btn("Student", 3)
        
        self.btn_p1.pack(side="left", padx=5)
        self.btn_p2.pack(side="left", padx=5)
        self.btn_p3.pack(side="left", padx=5)

        # ================= ZONA DE CHAT =================
        self.chat_scroll = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # ================= ZONA SUGESTII =================
        self.suggestions_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.suggestions_frame.grid(row=2, column=0, sticky="ew", pady=5)
        
        # ================= ZONA INPUT =================
        self.input_frame = ctk.CTkFrame(self, height=70, fg_color="transparent")
        self.input_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry_msg = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Întreabă ceva...",
            height=50,
            corner_radius=25,
            border_width=0,
            font=("Roboto Medium", 16)
        )
        self.entry_msg.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_msg.bind("<Return>", self.send_message_event)

        self.btn_send = ctk.CTkButton(
            self.input_frame,
            text="➤",
            width=50,
            height=50,
            corner_radius=25,
            font=("Arial", 20),
            command=self.send_message
        )
        self.btn_send.grid(row=0, column=1)

        # Inițializare UI
        self.apply_theme(1)
        self.refresh_suggestions()
        self.add_message("Salut! Alege o personalitate.", "AI")
        
        # Mesaj vocal introductiv (opțional)
        if self.voice_enabled:
             self.tts.speak("Salut! Eu sunt Threeb.")

    def create_persona_btn(self, text, mode_idx):
        return ctk.CTkButton(
            self.persona_frame,
            text=text,
            height=30,
            corner_radius=15,
            fg_color="#333",
            command=lambda: self.change_personality(mode_idx)
        )

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        if self.voice_enabled:
            self.btn_voice.configure(text="🔊", text_color="green")
            self.tts.unpause()
        else:
            self.btn_voice.configure(text="🔇", text_color="gray")
            self.tts.pause()

    def change_personality(self, mode_idx):
        self.current_mode = mode_idx
        if self.ai: self.ai.set_personality(mode_idx)
        
        # Schimbare Gen Voce
        if mode_idx == 1: self.tts.set_gender('female')
        else: self.tts.set_gender('male')

        self.apply_theme(mode_idx)
        
        t = THEMES[mode_idx]
        self.status_notification(f"✨ Mod schimbat: {t['name']}")

    def apply_theme(self, mode_idx):
        t = THEMES[mode_idx]
        
        # 1. Background General
        self.configure(fg_color=t["bg_color"])
        
        # 2. Header
        self.header_frame.configure(fg_color=t["chat_bg"])
        self.lbl_title.configure(font=(t["font"], 20, "bold"), text_color=t["accent"])
        self.lbl_icon.configure(text_color=t["accent"])
        
        # 3. Chat Area
        self.chat_scroll.configure(fg_color=t["bg_color"]) # Transparent efectiv
        
        # 4. Input Area
        self.entry_msg.configure(fg_color=t["input_bg"], text_color="white", font=(t["font"], 16))
        self.btn_send.configure(fg_color=t["accent"], hover_color=t["btn_hover"])
        
        # 5. Butoane Persona (Highlight cel activ)
        buttons = [self.btn_p1, self.btn_p2, self.btn_p3]
        for idx, btn in enumerate(buttons, 1):
            if idx == mode_idx:
                btn.configure(fg_color=t["accent"], text_color="black" if mode_idx != 3 else "white")
            else:
                btn.configure(fg_color="#333", text_color="white")

    def status_notification(self, text):
        """Afișează un label temporar (ca System Message)"""
        lbl = ctk.CTkLabel(self.chat_scroll, text=text, text_color="gray", font=("Arial", 12))
        lbl.pack(pady=5)
        # Dispare după 3 secunde (metoda .after este nativă Tkinter)
        self.after(3000, lbl.destroy)

    def refresh_suggestions(self):
        # Ștergem butoanele vechi
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()

        if self.ai:
            questions = self.ai.get_random_shortcuts()
        else:
            questions = ["Eroare API", "Verifică Key"]

        t = THEMES[self.current_mode]
        for q in questions:
            btn = ctk.CTkButton(
                self.suggestions_frame,
                text=q,
                fg_color="#333",
                hover_color="#444",
                height=30,
                corner_radius=15,
                font=(t["font"], 12),
                command=lambda question=q: self.submit_suggestion(question)
            )
            btn.pack(side="left", padx=5, expand=True, fill="x")

    def submit_suggestion(self, text):
        self.entry_msg.delete(0, "end")
        self.entry_msg.insert(0, text)
        self.send_message()

    def send_message_event(self, event):
        self.send_message()

    def send_message(self):
        text = self.entry_msg.get()
        if not text: return

        self.entry_msg.delete(0, "end")
        
        # 1. Adaugă mesaj user
        self.add_message(text, "User")
        
        # 2. Logică AI în Thread separat (ca să nu înghețe UI-ul)
        threading.Thread(target=self.process_ai_response, args=(text,), daemon=True).start()

    def process_ai_response(self, text):
        response = self.ai.ask_gemini(text) if self.ai else "Eroare AI"
        
        # 3. Update UI din thread (CTk e thread-safe în general pentru metode simple)
        self.add_message(response, "AI")
        
        # 4. Voce
        if self.voice_enabled:
            self.tts.speak(response)
        
        # 5. Refresh sugestii (trebuie apelat pe main thread ideal, dar merge și așa)
        self.after(100, self.refresh_suggestions)

    def add_message(self, text, sender):
        # Creăm bula
        bubble = ChatBubble(
            self.chat_scroll, 
            text=text, 
            sender=sender, 
            theme_id=self.current_mode
        )
        
        # Aliniere folosind pack options
        if sender == "AI":
            bubble.pack(pady=5, padx=10, anchor="w") # Stânga
        else:
            bubble.pack(pady=5, padx=10, anchor="e") # Dreapta
            
        # Scroll la fund
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

if __name__ == "__main__":
    app = ThreebApp()
    app.mainloop()