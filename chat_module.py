import customtkinter as ctk
import threading
import sys

# Try importing backend; if missing, use dummies to prevent crash
try:
    from assistant import UniversityAI
    from tts_manager import TTSManager
except ImportError:
    print("Warning: 'assistant.py' or 'tts_manager.py' missing. Using dummy classes.")
    class UniversityAI:
        def set_personality(self, x): pass
        def get_random_shortcuts(self): return ["Ce facultăți sunt?", "Taxe?", "Admitere?"]
        def ask_gemini(self, text): return f"Simulated response to: {text}"
    class TTSManager:
        def speak(self, text): pass
        def set_gender(self, x): pass
        def pause(self): pass
        def unpause(self): pass
        def stop(self): pass

# --- CONFIGURĂRI GLOBALE ---
THEMES = {
    1: { "name": "Standard", "bg_color": "#121212", "chat_bg": "#1a1a1a", "input_bg": "#262626", "user_bubble": "#262626", "ai_bubble": "#0D47A1", "accent": "#42A5F5", "font": "Roboto Medium", "btn_hover": "#1565C0" },
    2: { "name": "Profesor", "bg_color": "#1B3A28", "chat_bg": "#142c1f", "input_bg": "#2E5A43", "user_bubble": "#2E5A43", "ai_bubble": "#3E2723", "accent": "#FFCA28", "font": "Times New Roman", "btn_hover": "#F57F17" },
    3: { "name": "Student", "bg_color": "#1A0B2E", "chat_bg": "#120621", "input_bg": "#2D1B4E", "user_bubble": "#2D1B4E", "ai_bubble": "#4A148C", "accent": "#EC407A", "font": "Consolas", "btn_hover": "#AD1457" }
}

# --- CLASĂ TASTATURĂ VIRTUALĂ ---
class TouchKeyboard(ctk.CTkFrame):
    def __init__(self, master, entry_widget, on_submit, on_close, **kwargs):
        super().__init__(master, fg_color="#1f1f1f", corner_radius=0, **kwargs)
        self.entry = entry_widget
        self.on_submit = on_submit
        self.on_close = on_close
        
        # Layout taste
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', "✕"],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm', '⌫'],
            ['SPAȚIU', 'TRIMITE']
        ]
        
        self.setup_keys()

    def setup_keys(self):
        keys_container = ctk.CTkFrame(self, fg_color="transparent")
        keys_container.pack(expand=True, fill="both", padx=5, pady=(10, 20))

        for r, row_keys in enumerate(self.keys):
            row_frame = ctk.CTkFrame(keys_container, fg_color="transparent")
            row_frame.pack(pady=3, expand=True)
            
            for key in row_keys:
                width = 60 
                height = 40
                fg_color = "#333"
                hover_color = "#444"
                text_color = "white"
                cmd = lambda k=key: self.press_key(k)
                
                # Stiluri speciale
                if key == '⌫':
                    width = 80
                    fg_color = "#8B0000"
                    hover_color = "#B22222"
                elif key == 'SPAȚIU':
                    width = 400
                elif key == 'TRIMITE':
                    width = 120
                    fg_color = "#1b5e20"
                    hover_color = "#2e7d32"
                    cmd = self.press_submit
                elif key == "✕":
                    width = 40
                    height = 40
                    fg_color = "#333"
                    hover_color = "#8B0000"
                    cmd = self.press_close

                btn = ctk.CTkButton(
                    row_frame, 
                    text=key.upper(), 
                    width=width, 
                    height=height,
                    corner_radius=8, 
                    fg_color=fg_color, 
                    hover_color=hover_color,
                    text_color=text_color,
                    font=("Arial", 16, "bold"),
                    command=cmd
                )
                btn.pack(side="left", padx=3)

    def press_key(self, key):
        if key == '⌫':
            current_text = self.entry.get()
            self.entry.delete(len(current_text)-1, "end")
        elif key == 'SPAȚIU':
            self.entry.insert("end", " ")
        else:
            self.entry.insert("end", key)

    def press_submit(self):
        self.on_submit()
        self.press_close()

    def press_close(self):
        self.on_close() 
        self.place_forget()

    def show(self):
        self.place(relx=0.5, rely=1.0, anchor="s", relwidth=1.0, relheight=0.60)
        self.tkraise()


class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, text, sender, theme_id, **kwargs):
        super().__init__(master, **kwargs)
        self.theme = THEMES[theme_id]
        
        if sender == "AI":
            bg_color = self.theme["ai_bubble"]
            text_color = "white"
            anchor = "w"
            self.configure(fg_color=bg_color, corner_radius=15)
        else:
            bg_color = self.theme["user_bubble"]
            text_color = "white"
            anchor = "e"
            self.configure(fg_color=bg_color, corner_radius=15)

        self.lbl_text = ctk.CTkLabel(
            self, text=text, text_color=text_color,
            font=(self.theme["font"], 14), wraplength=450, justify="left"
        )
        self.lbl_text.pack(padx=15, pady=10)


class ChatView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.ai = UniversityAI()
        self.tts = TTSManager()
        
        self.current_mode = 1
        self.voice_enabled = True
        self.keyboard_visible = False
        
        # Lista pentru a ține evidența butoanelor de sugestie
        self.suggestion_buttons = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ================= HEADER =================
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.lbl_icon = ctk.CTkLabel(self.header_frame, text="🤖", font=("Arial", 24))
        self.lbl_icon.grid(row=0, column=0, padx=15, pady=10)

        self.lbl_title = ctk.CTkLabel(self.header_frame, text="THREEB", font=("Roboto Medium", 20, "bold"))
        self.lbl_title.grid(row=0, column=1, sticky="w")

        self.btn_voice = ctk.CTkButton(
            self.header_frame, text="🔊", width=40, command=self.toggle_voice,
            fg_color="transparent", hover_color="#333", font=("Arial", 20)
        )
        self.btn_voice.grid(row=0, column=2, padx=5)

        self.btn_close = ctk.CTkButton(
            self.header_frame, text="✕", width=40, 
            command=lambda: self.controller.show_home(),
            fg_color="transparent", hover_color="#C62828", text_color="red", font=("Arial", 18, "bold")
        )
        self.btn_close.grid(row=0, column=3, padx=(5, 15))

        # ================= BUTOANE PERSONALITATE =================
        self.persona_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.persona_frame.grid(row=0, column=0, sticky="s", pady=(50, 5))

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
            self.input_frame, placeholder_text="Apasă aici pentru tastatură...",
            height=50, corner_radius=25, border_width=0, font=("Roboto Medium", 16)
        )
        self.entry_msg.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_msg.bind("<Return>", self.send_message_event)
        
        self.entry_msg.bind("<Button-1>", self.open_keyboard)
        self.entry_msg.bind("<FocusIn>", self.open_keyboard)

        self.btn_send = ctk.CTkButton(
            self.input_frame, text="➤", width=50, height=50,
            corner_radius=25, font=("Arial", 20), command=self.send_message
        )
        self.btn_send.grid(row=0, column=1)

        # --- INIȚIALIZARE TASTATURĂ ---
        self.keyboard = TouchKeyboard(self, self.entry_msg, self.send_message, self.close_keyboard)

        # Inițializare UI
        self.apply_theme(1)
        self.refresh_suggestions()
        self.add_message("Salut! Alege o personalitate.", "AI")
        
        if self.voice_enabled:
             threading.Thread(target=lambda: self.tts.speak("Salut! Eu sunt Threeb."), daemon=True).start()

    def create_persona_btn(self, text, mode_idx):
        return ctk.CTkButton(
            self.persona_frame, text=text, height=30, corner_radius=15, fg_color="#333",
            command=lambda: self.change_personality(mode_idx)
        )
    
    def open_keyboard(self, event=None):
        if not self.keyboard_visible:
            self.keyboard.show()
            self.keyboard_visible = True
            
            # Ridicăm input-ul mai sus pentru a face loc tastaturii
            self.input_frame.grid_configure(pady=(0, 310)) 
            self.suggestions_frame.grid_remove()

    def close_keyboard(self):
        self.keyboard_visible = False
        self.input_frame.grid_configure(pady=(0, 20))
        self.suggestions_frame.grid()

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        if self.voice_enabled:
            self.btn_voice.configure(text="🔊", text_color="green")
            self.tts.unpause()
        else:
            self.btn_voice.configure(text="🔇", text_color="gray")
            self.tts.pause()

    def change_personality(self, mode_idx):
        if self.current_mode == mode_idx:
            return

        self.current_mode = mode_idx
        if self.ai: self.ai.set_personality(mode_idx)
        
        if mode_idx == 1: self.tts.set_gender('female')
        else: self.tts.set_gender('male')

        self.apply_theme(mode_idx)
        t = THEMES[mode_idx]
        self.status_notification(f"✨ Mod schimbat: {t['name']}")

    def apply_theme(self, mode_idx):
        t = THEMES[mode_idx]
        self.configure(fg_color=t["bg_color"])
        self.header_frame.configure(fg_color=t["chat_bg"])
        self.lbl_title.configure(font=(t["font"], 20, "bold"), text_color=t["accent"])
        self.lbl_icon.configure(text_color=t["accent"])
        self.chat_scroll.configure(fg_color=t["bg_color"])
        self.entry_msg.configure(fg_color=t["input_bg"], text_color="white", font=(t["font"], 16))
        self.btn_send.configure(fg_color=t["accent"], hover_color=t["btn_hover"])
        
        buttons = [self.btn_p1, self.btn_p2, self.btn_p3]
        for idx, btn in enumerate(buttons, 1):
            if idx == mode_idx:
                btn.configure(fg_color=t["accent"], text_color="black" if mode_idx != 3 else "white")
            else:
                btn.configure(fg_color="#333", text_color="white")

    def status_notification(self, text):
        lbl = ctk.CTkLabel(self.chat_scroll, text=text, text_color="gray", font=("Arial", 12))
        lbl.pack(pady=5)
        self.after(3000, lbl.destroy)

    def refresh_suggestions(self):
        # 1. Ștergem butoanele vechi și resetăm lista
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        self.suggestion_buttons = [] # Resetare listă

        if self.ai: questions = self.ai.get_random_shortcuts()
        else: questions = ["Eroare API"]

        t = THEMES[self.current_mode]
        for q in questions:
            btn = ctk.CTkButton(
                self.suggestions_frame, text=q, fg_color="#333", hover_color="#444",
                height=30, corner_radius=15, font=(t["font"], 12),
                command=lambda question=q: self.submit_suggestion(question)
            )
            btn.pack(side="left", padx=5, expand=True, fill="x")
            # 2. Adăugăm referința butonului în listă
            self.suggestion_buttons.append(btn)

    def disable_suggestions(self):
        """Dezactivează toate butoanele de sugestie curente"""
        for btn in self.suggestion_buttons:
            try:
                btn.configure(state="disabled")
            except Exception:
                pass

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
        
        # 3. Dezactivăm sugestiile imediat ce s-a trimis mesajul
        self.disable_suggestions()
        
        self.close_keyboard()
        self.keyboard.place_forget()
        
        self.add_message(text, "User")
        threading.Thread(target=self.process_ai_response, args=(text,), daemon=True).start()

    def process_ai_response(self, text):
        response = self.ai.ask_gemini(text) if self.ai else "Eroare AI"
        
        if not self.winfo_exists():
            return

        self.add_message(response, "AI")
        if self.voice_enabled:
            self.tts.speak(response)
        
        if self.winfo_exists():
            # Aceasta va șterge butoanele dezactivate și va crea altele noi (active)
            self.after(100, self.refresh_suggestions)

    def add_message(self, text, sender):
        if not self.winfo_exists(): return
        
        bubble = ChatBubble(self.chat_scroll, text=text, sender=sender, theme_id=self.current_mode)
        if sender == "AI": bubble.pack(pady=5, padx=10, anchor="w")
        else: bubble.pack(pady=5, padx=10, anchor="e")
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def cleanup(self):
        if hasattr(self.tts, 'stop'):
            self.tts.stop()