import customtkinter as ctk
import threading
import time
from assistant import UniversityAI
from tts_manager import TTSManager

# --- CONFIGURĂRI VIZUALE GLOBALE ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- TRADUCERI ---
TRANSLATIONS = {
    'ro': { 'title': 'THREEB', 'hint': 'Apasă pentru a scrie...', 'p1': 'Standard', 'p2': 'Profesor', 'p3': 'Bro', 'sys_change': 'Mod activat: ', 'sys_lang': '🇷🇴 Limbă: Română', 'welcome': 'Salut! Sunt THREEB. Cu ce te ajut?' },
    'en': { 'title': 'THREEB', 'hint': 'Tap to type...', 'p1': 'Standard', 'p2': 'Professor', 'p3': 'Bro', 'sys_change': 'Mode active: ', 'sys_lang': '🇬🇧 Language: English', 'welcome': 'Hi! I am THREEB. How can I help?' },
    'ru': { 'title': 'THREEB', 'hint': 'Нажмите, чтобы писать...', 'p1': 'Стандарт', 'p2': 'Профессор', 'p3': 'Бро', 'sys_change': 'Режим: ', 'sys_lang': '🇷🇺 Язык: Русский', 'welcome': 'Привет! Я THREEB. Чем помочь?' }
}

# --- TEME (Design Vizual) ---
THEMES = {
    1: { # STANDARD (Neutral Blue)
        "name": "Standard", "bg": "#0f172a", "header": "#1e293b", 
        "chat_bg": "#0f172a", "input_bg": "#334155",
        "user_bubble": "#3b82f6", "ai_bubble": "#1e293b", 
        "accent": "#60a5fa", "font": "Roboto Medium", "avatar": "AI"
    },
    2: { # PROFESOR (Elegant Green)
        "name": "Profesor", "bg": "#022c22", "header": "#064e3b", 
        "chat_bg": "#022c22", "input_bg": "#065f46",
        "user_bubble": "#10b981", "ai_bubble": "#064e3b", 
        "accent": "#34d399", "font": "Times New Roman", "avatar": "P"
    },
    3: { # STUDENT/BRO (Cyber Purple)
        "name": "Bro", "bg": "#2e1065", "header": "#4c1d95", 
        "chat_bg": "#2e1065", "input_bg": "#5b21b6",
        "user_bubble": "#d946ef", "ai_bubble": "#4c1d95", 
        "accent": "#e879f9", "font": "Consolas", "avatar": "B"
    }
}

# --- CLASĂ TASTATURĂ VIRTUALĂ ---
class TouchKeyboard(ctk.CTkFrame):
    def __init__(self, master, entry_widget, on_submit, on_close, **kwargs):
        super().__init__(master, fg_color="#101010", corner_radius=0, **kwargs)
        self.entry = entry_widget
        self.on_submit = on_submit
        self.on_close = on_close
        
        # Layout taste (QWERTY + Speciale)
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
        keys_container.pack(expand=True, fill="both", padx=5, pady=(5, 5))

        for row_keys in self.keys:
            row_frame = ctk.CTkFrame(keys_container, fg_color="transparent")
            row_frame.pack(pady=2, expand=True)
            
            for key in row_keys:
                width = 55 
                height = 45
                fg_color = "#333"
                hover_color = "#444"
                text_color = "white"
                cmd = lambda k=key: self.press_key(k)
                
                if key == '⌫':
                    width = 70
                    fg_color = "#8B0000" # Roșu închis
                    hover_color = "#B22222"
                elif key == 'SPAȚIU':
                    width = 300
                elif key == 'TRIMITE':
                    width = 100
                    fg_color = "#1b5e20" # Verde
                    hover_color = "#2e7d32"
                    cmd = self.press_submit
                elif key == "✕":
                    width = 50
                    fg_color = "#333"
                    text_color = "#ff5555"
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
                    font=("Arial", 14, "bold"),
                    command=cmd
                )
                btn.pack(side="left", padx=2)

    def press_key(self, key):
        if key == '⌫':
            current_text = self.entry.get()
            self.entry.delete(len(current_text)-1, "end")
        elif key == 'SPAȚIU':
            self.entry.insert("end", " ")
        else:
            self.entry.insert("end", key)

    def press_submit(self):
        self.on_submit() # Apelează funcția de trimitere din ChatView
        # Tastatura rămâne deschisă sau închisă? De obicei se închide la send.
        # self.press_close() 

    def press_close(self):
        self.on_close() # Notifică ChatView să rearanjeze UI-ul
        self.place_forget()

    def show(self):
        # Apare jos de tot
        self.place(relx=0.5, rely=1.0, anchor="s", relwidth=1.0, relheight=0.45)
        self.tkraise()

# --- SCROLL FRAME (Smart Touch) ---
class TouchScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.last_y = 0
        
        self._parent_canvas.bind("<Button-1>", self.on_press)
        self._parent_canvas.bind("<B1-Motion>", self.on_drag)
        self.bind("<Button-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)

    def on_press(self, event):
        self.last_y = event.y_root

    def on_drag(self, event):
        bbox = self._parent_canvas.bbox("all") 
        if not bbox: return
        content_height = bbox[3] - bbox[1]
        
        if content_height <= self.winfo_height(): return 

        delta = self.last_y - event.y_root
        self.last_y = event.y_root
        self._parent_canvas.yview_scroll(-int(delta), "units")

    def bind_child_scroll(self, widget):
        widget.bind("<Button-1>", self.on_press)
        widget.bind("<B1-Motion>", self.on_drag)
        for child in widget.winfo_children():
            self.bind_child_scroll(child)

# --- BULE CHAT (Design Modern cu Avatare) ---
class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, text, sender, theme_id, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme = THEMES[theme_id]
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        
        # Avatar
        initial = "TU" if sender == "User" else self.theme['avatar']
        color_av = "#64748b" if sender == "User" else self.theme['accent']
        
        self.avatar = ctk.CTkLabel(
            inner, text=initial, width=32, height=32,
            fg_color=color_av, text_color="black", corner_radius=16,
            font=("Arial", 11, "bold")
        )

        bg = self.theme["user_bubble"] if sender == "User" else self.theme["ai_bubble"]
        
        self.bubble = ctk.CTkFrame(inner, fg_color=bg, corner_radius=16)
        self.lbl = ctk.CTkLabel(
            self.bubble, text=text, text_color="white",
            font=(self.theme["font"], 15), wraplength=400, justify="left"
        )
        self.lbl.pack(padx=12, pady=8)

        if sender == "AI":
            inner.pack(side="left", anchor="w")
            self.avatar.pack(side="left", padx=(0, 8))
            self.bubble.pack(side="left")
        else:
            inner.pack(side="right", anchor="e")
            self.avatar.pack(side="right", padx=(8, 0))
            self.bubble.pack(side="right")

    def update_text(self, new_text):
        self.lbl.configure(text=new_text)

# --- CLASA PRINCIPALĂ (VIEW) ---
class ChatView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        # Backend Logic
        try:
            self.ai = UniversityAI()
        except:
            self.ai = None
        self.tts = TTSManager()
        
        self.current_mode = 1
        self.current_lang = 'ro'
        self.voice_enabled = True
        self.keyboard_visible = False
        self.is_thinking = False
        self.suggestion_buttons = []
        self.pending_bubble = None

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # === 1. TOP BAR (Transparent & Clean) ===
        self.top_bar = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.grid_columnconfigure(1, weight=1)

        # Logo
        ctk.CTkLabel(self.top_bar, text="✦", font=("Arial", 24), text_color="#60a5fa").grid(row=0, column=0, padx=(20, 10), pady=10)
        self.lbl_title = ctk.CTkLabel(self.top_bar, text="THREEB", font=("Roboto", 18, "bold"))
        self.lbl_title.grid(row=0, column=1, sticky="w")

        # Controale Dreapta
        self.controls = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.controls.grid(row=0, column=2, padx=15)

        # Lang Buttons
        self.btn_ro = self.create_pill("RO", "ro")
        self.btn_en = self.create_pill("EN", "en")
        self.btn_ru = self.create_pill("RU", "ru")
        
        # Mute Btn
        self.btn_voice = ctk.CTkButton(
            self.controls, text="🔊", width=35, height=35, corner_radius=18,
            fg_color="#334155", hover_color="#475569", command=self.toggle_voice
        )
        self.btn_voice.pack(side="left", padx=10)
        
        # Close (Back to Home)
        ctk.CTkButton(
            self.controls, text="✕", width=35, height=35, corner_radius=18,
            fg_color="#ef4444", hover_color="#dc2626", command=self.go_home
        ).pack(side="left")

        # === 2. PERSONA SELECTOR (Sub Header) ===
        self.persona_bar = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.persona_bar.grid(row=0, column=0, sticky="s", pady=(55, 0))
        
        self.btn_p1 = self.create_persona_btn("Standard", 1)
        self.btn_p2 = self.create_persona_btn("Profesor", 2)
        self.btn_p3 = self.create_persona_btn("Bro", 3)

        # === 3. CHAT AREA ===
        self.chat_scroll = TouchScrollableFrame(self, corner_radius=0)
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # === 4. BOTTOM AREA (Capsule Input) ===
        self.bottom_area = ctk.CTkFrame(self, height=140, corner_radius=0, fg_color="transparent")
        self.bottom_area.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Sugestii
        self.sugg_frame = ctk.CTkFrame(self.bottom_area, height=40, fg_color="transparent")
        self.sugg_frame.pack(fill="x", pady=(0, 10), padx=20)
        
        # Input Capsule
        self.input_capsule = ctk.CTkFrame(self.bottom_area, height=60, corner_radius=30)
        self.input_capsule.pack(fill="x", padx=20, pady=5)
        
        self.entry_msg = ctk.CTkEntry(
            self.input_capsule, placeholder_text="...", height=50, 
            corner_radius=25, border_width=0, font=("Roboto", 16), fg_color="transparent"
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(15, 5), pady=5)
        
        # Bindings pentru tastatură
        self.entry_msg.bind("<Button-1>", self.open_keyboard)
        self.entry_msg.bind("<FocusIn>", self.open_keyboard)
        self.entry_msg.bind("<Return>", lambda e: self.send_message())

        self.btn_send = ctk.CTkButton(
            self.input_capsule, text="➤", width=50, height=50, 
            corner_radius=25, font=("Arial", 20), command=self.send_message
        )
        self.btn_send.pack(side="right", padx=5, pady=5)

        # --- INIȚIALIZARE TASTATURĂ VIRTUALĂ ---
        self.keyboard = TouchKeyboard(self, self.entry_msg, self.send_message, self.close_keyboard)

        # Start Logic
        self.apply_theme(1)
        self.change_language('ro')
        
        # Mesaj de întâmpinare
        welcome_text = TRANSLATIONS['ro']['welcome']
        self.add_message(welcome_text, "AI")
        self.after(800, lambda: self.tts.speak(welcome_text) if self.voice_enabled else None)

    # --- LOGICA NAVIGARE ---
    def go_home(self):
        self.cleanup()
        self.controller.show_home()

    def cleanup(self):
        """Curățenie înainte de a schimba ecranul"""
        if hasattr(self.tts, 'stop'):
            self.tts.stop()

    # --- HELPERS UI ---
    def create_pill(self, text, code):
        btn = ctk.CTkButton(
            self.controls, text=text, width=40, height=30, corner_radius=15, 
            fg_color="transparent", border_width=1, border_color="#475569",
            font=("Arial", 11, "bold"), command=lambda: self.change_language(code)
        )
        btn.pack(side="left", padx=2)
        return btn

    def create_persona_btn(self, text, idx):
        btn = ctk.CTkButton(
            self.persona_bar, text=text, height=32, corner_radius=16, 
            fg_color="#334155", font=("Arial", 12), 
            command=lambda: self.change_personality(idx)
        )
        btn.pack(side="left", padx=5)
        return btn

    # --- LOGICA TASTATURĂ ---
    def open_keyboard(self, event=None):
        if not self.keyboard_visible:
            self.keyboard.show()
            self.keyboard_visible = True
            # Împingem UI-ul în sus ca să se vadă inputul
            # Ascundem sugestiile temporar pentru spațiu
            self.sugg_frame.pack_forget()
            self.bottom_area.grid_configure(pady=(0, 250)) # Ridicăm footer-ul

    def close_keyboard(self):
        self.keyboard_visible = False
        # Revenim la normal
        self.bottom_area.grid_configure(pady=(0, 10))
        self.sugg_frame.pack(fill="x", pady=(0, 10), padx=20, before=self.input_capsule)

    # --- LOGICA APLICAȚIEI ---
    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        if self.voice_enabled:
            self.btn_voice.configure(text="🔊", fg_color="#334155")
            self.tts.unpause()
        else:
            self.btn_voice.configure(text="🔇", fg_color="#ef4444")
            self.tts.pause()

    def change_language(self, code):
        if self.is_thinking: return 
        self.current_lang = code
        if self.ai: self.ai.set_language(code)
        self.tts.set_language(code)
        
        t = TRANSLATIONS[code]
        self.lbl_title.configure(text=t['title'])
        self.entry_msg.configure(placeholder_text=t['hint'])
        self.btn_p1.configure(text=t['p1'])
        self.btn_p2.configure(text=t['p2'])
        self.btn_p3.configure(text=t['p3'])
        
        for btn, c in [(self.btn_ro, 'ro'), (self.btn_en, 'en'), (self.btn_ru, 'ru')]:
            btn.configure(fg_color=THEMES[self.current_mode]["accent"] if c == code else "transparent", text_color="white")
        
        self.refresh_suggestions()
        self.status_notification(t['sys_lang'])

    def change_personality(self, idx):
        if self.is_thinking: return
        self.current_mode = idx
        if self.ai: self.ai.set_personality(idx)
        self.apply_theme(idx)
        
        msg = TRANSLATIONS[self.current_lang]['sys_change'] + TRANSLATIONS[self.current_lang][f'p{idx}']
        self.status_notification(msg)

    def apply_theme(self, idx):
        t = THEMES[idx]
        self.configure(fg_color=t["bg"])
        self.top_bar.configure(fg_color=t["bg"])
        self.lbl_title.configure(text_color=t["accent"])
        self.chat_scroll.configure(fg_color=t["bg"])
        self.input_capsule.configure(fg_color=t["input_bg"])
        self.entry_msg.configure(text_color="white", font=(t["font"], 16))
        self.btn_send.configure(fg_color=t["accent"], hover_color="white", text_color="black")
        
        btns = [self.btn_p1, self.btn_p2, self.btn_p3]
        for i, btn in enumerate(btns, 1):
            if i == idx: btn.configure(fg_color=t["accent"], text_color="black")
            else: btn.configure(fg_color="#334155", text_color="white")

    def status_notification(self, text):
        container = ctk.CTkFrame(self.chat_scroll, fg_color="#333", corner_radius=15)
        lbl = ctk.CTkLabel(container, text=text, text_color="white", font=("Arial", 12))
        lbl.pack(padx=15, pady=5)
        container.pack(pady=10)
        self.chat_scroll.bind_child_scroll(container)
        self.chat_scroll.bind_child_scroll(lbl)
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
        self.after(2500, container.destroy)

    def refresh_suggestions(self):
        for w in self.sugg_frame.winfo_children(): w.destroy()
        qs = self.ai.get_random_shortcuts() if self.ai else []
        t = THEMES[self.current_mode]
        for q in qs:
            btn = ctk.CTkButton(
                self.sugg_frame, text=q, fg_color=t["input_bg"], hover_color="#475569", 
                height=35, corner_radius=17, font=(t["font"], 12),
                command=lambda x=q: self.submit_suggestion(x)
            )
            btn.pack(side="left", padx=5, expand=True, fill="x")

    def toggle_interaction(self, enable):
        state = "normal" if enable else "disabled"
        self.is_thinking = not enable
        self.btn_send.configure(state=state)
        # self.entry_msg.configure(state=state) # Entry-ul îl lăsăm activ să poată scrie următoarea
        for w in self.sugg_frame.winfo_children(): w.configure(state=state)

    def submit_suggestion(self, text):
        if self.is_thinking: return
        self.entry_msg.delete(0, "end")
        self.entry_msg.insert(0, text)
        self.send_message()

    def send_message(self):
        text = self.entry_msg.get()
        if not text: return

        # 1. KILL TTS (Stop Instant)
        self.tts.stop()
        
        self.keyboard.press_close() # Închide tastatura
        self.entry_msg.delete(0, "end")
        self.add_message(text, "User")
        
        self.toggle_interaction(False)
        
        # Mesaj placeholder
        self.pending_bubble = self.add_message("...", "AI")
        
        threading.Thread(target=self.process_ai, args=(text,), daemon=True).start()

    def process_ai(self, text):
        response = self.ai.ask_gemini(text) if self.ai else "Eroare AI"
        
        # Update UI pe thread principal
        self.after(0, lambda: self.finalize_response(response))

    def finalize_response(self, response):
        if self.pending_bubble:
            self.pending_bubble.update_text(response)
            self.pending_bubble = None
            self.chat_scroll._parent_canvas.yview_moveto(1.0)
        
        self.toggle_interaction(True)
        
        if self.voice_enabled:
            self.tts.speak(response)
        
        self.after(100, self.refresh_suggestions)

    def add_message(self, text, sender):
        bubble = ChatBubble(self.chat_scroll, text=text, sender=sender, theme_id=self.current_mode)
        if sender == "AI": bubble.pack(pady=5, padx=15, anchor="w")
        else: bubble.pack(pady=5, padx=15, anchor="e")
        self.chat_scroll.bind_child_scroll(bubble)
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
        return bubble