import customtkinter as ctk
import threading
import json
import os
import time
import webbrowser
import yagmail
from dotenv import load_dotenv
from PIL import Image
from assistant import UniversityAI
from tts_manager import TTSManager
from keyboard_module import TouchKeyboard
from datetime import datetime

# --- CONFIGURARE ENV ---
load_dotenv()
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# --- CONFIGURĂRI VIZUALE ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

TRANSLATIONS = {
    'ro': { 
        'title': 'THREEB', 'hint': 'Scrie un mesaj...', 
        'p1': 'Standard', 'p2': 'Profesor', 'p3': 'Bro', 
        'sys_change': 'Mod: ', 'sys_lang': '🇷🇴 Limbă: Română', 
        'welcome': 'Salut! Sunt THREEB. Cu ce te ajut?', 
        'thinking': '⏳ Procesez...', 
        'popup_report': '✅ RAPORT TRIMIS ADMINULUI!', 
        'btn_report': '⚠️ Raportează',
        'btn_report_sent': '✅ Trimis'
    },
    'en': { 
        'title': 'THREEB', 'hint': 'Type a message...', 
        'p1': 'Standard', 'p2': 'Professor', 'p3': 'Bro', 
        'sys_change': 'Mode: ', 'sys_lang': '🇬🇧 English', 
        'welcome': 'Hi! I am THREEB. How can I help?', 
        'thinking': '⏳ Thinking...', 
        'popup_report': '✅ REPORT SENT TO ADMIN!', 
        'btn_report': '⚠️ Report',
        'btn_report_sent': '✅ Sent'
    },
    'ua': { 
        'title': 'THREEB', 'hint': 'Напишіть повідомлення...', 
        'p1': 'Стандарт', 'p2': 'Професор', 'p3': 'Бро', 
        'sys_change': 'Режим: ', 'sys_lang': '🇺🇦 Мова: Українська', 
        'welcome': 'Привіт! Я THREEB. Чим можу допомогти?', 
        'thinking': '⏳ Думаю...', 
        'popup_report': '✅ ЗВІТ НАДІСЛАНО!', 
        'btn_report': '⚠️ Поскаржитись',
        'btn_report_sent': '✅ Надіслано'
    }
}

THEMES = {
    1: { "name": "Standard", "bg": "#0f172a", "header": "#1e293b", "chat_bg": "#0f172a", "input_bg": "#334155", "user_bubble": "#3b82f6", "ai_bubble": "#1e293b", "accent": "#60a5fa", "btn_hover": "#2563eb", "font": "Roboto Medium", "avatar": "AI" },
    2: { "name": "Profesor", "bg": "#022c22", "header": "#064e3b", "chat_bg": "#022c22", "input_bg": "#065f46", "user_bubble": "#10b981", "ai_bubble": "#064e3b", "accent": "#34d399", "btn_hover": "#059669", "font": "Times New Roman", "avatar": "P" },
    3: { "name": "Bro", "bg": "#2e1065", "header": "#4c1d95", "chat_bg": "#2e1065", "input_bg": "#5b21b6", "user_bubble": "#d946ef", "ai_bubble": "#4c1d95", "accent": "#e879f9", "btn_hover": "#c026d3", "font": "Consolas", "avatar": "B" }
}

# --- SCROLL FRAME ---
class TouchScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.last_y = 0
        # Binding pentru touch scroll
        self._parent_canvas.bind("<Button-1>", self.on_press)
        self._parent_canvas.bind("<B1-Motion>", self.on_drag)
        self.bind("<Button-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)

    def on_press(self, event):
        self.last_y = event.y_root

    def on_drag(self, event):
        delta = self.last_y - event.y_root
        self.last_y = event.y_root
        self._parent_canvas.yview_scroll(int(delta / 3), "units") 

    def bind_child_scroll(self, widget):
        widget.bind("<Button-1>", self.on_press)
        widget.bind("<B1-Motion>", self.on_drag)
        for child in widget.winfo_children():
            self.bind_child_scroll(child)

# --- CHAT BUBBLE ---
class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, text, sender, theme_id, current_lang, report_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.theme = THEMES[theme_id]
        self.text_content = text
        self.report_callback = report_callback
        self.current_lang = current_lang
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        
        initial = "TU" if sender == "User" else self.theme['avatar']
        col = "#64748b" if sender == "User" else self.theme['accent']
        self.avatar = ctk.CTkLabel(inner, text=initial, width=32, height=32, fg_color=col, text_color="black", corner_radius=16, font=("Arial",11,"bold"))

        bg = self.theme["user_bubble"] if sender == "User" else self.theme["ai_bubble"]
        self.bubble = ctk.CTkFrame(inner, fg_color=bg, corner_radius=16)
        
        self.lbl = ctk.CTkLabel(self.bubble, text=text, text_color="white", font=(self.theme["font"],15), wraplength=320, justify="left")
        self.lbl.pack(padx=12, pady=(8, 2))

        if sender == "AI":
            inner.pack(side="left", anchor="w")
            self.avatar.pack(side="left", padx=(0,8), anchor="n")
            self.bubble.pack(side="left")
            
            # --- INTEGRARE BUTON RAPORTARE ---
            if report_callback:
                btn_txt = TRANSLATIONS[self.current_lang]['btn_report']
                self.btn_report = ctk.CTkButton(
                    self.bubble, 
                    text=btn_txt, 
                    width=80, 
                    height=24, 
                    fg_color="#330000", 
                    hover_color="#550000", 
                    text_color="#ff6b6b", 
                    font=("Arial", 11, "bold"), 
                    corner_radius=12,
                    command=self.on_report_click
                )
                self.btn_report.pack(side="bottom", anchor="e", padx=10, pady=(5, 8))
        else:
            inner.pack(side="right", anchor="e")
            self.avatar.pack(side="right", padx=(8,0), anchor="n")
            self.bubble.pack(side="right")

    def update_text(self, new_text):
        self.text_content = new_text
        self.lbl.configure(text=new_text)

    def on_report_click(self):
        # 1. Schimbam interfata butonului
        sent_txt = TRANSLATIONS[self.current_lang]['btn_report_sent']
        self.btn_report.configure(text=sent_txt, fg_color="#1b5e20", text_color="white", state="disabled")
        
        # 2. Apelam callback-ul catre ChatView
        if self.report_callback: 
            self.report_callback(self.text_content)

# --- SPECIALIZATION CARD (ONE CLICK) ---
class SpecializationCard(ctk.CTkFrame):
    def __init__(self, master, spec_id, **kwargs):
        super().__init__(master, fg_color="#1e293b", corner_radius=8, border_width=1, border_color="#475569", cursor="hand2", **kwargs)
        
        self.spec_data = self.load_spec_data(spec_id)
        if not self.spec_data: return 
        
        self.target_url = self.spec_data.get("url", "https://aciee.ugal.ro")
        self.last_click_time = 0 

        self.grid_columnconfigure(1, weight=1)
        
        icon_path = os.path.join("icons", self.spec_data.get("icon", "default.png"))
        try:
            pil_image = Image.open(icon_path)
            img_obj = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(110, 110))
            self.icon_lbl = ctk.CTkLabel(self, text="", image=img_obj, cursor="hand2")
        except:
            self.icon_lbl = ctk.CTkLabel(self, text=self.spec_data.get("acronym", "?"), width=110, height=110, fg_color="#475569", corner_radius=8, cursor="hand2")
            
        self.icon_lbl.grid(row=0, column=0, rowspan=3, padx=15, pady=15, sticky="n")
        
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="nw", padx=(0, 10), pady=(15, 0))
        
        lbl_name = ctk.CTkLabel(content_frame, text=self.spec_data["name"].upper(), font=("Roboto", 16, "bold"), text_color="white", anchor="w", wraplength=500, cursor="hand2")
        lbl_name.pack(anchor="w", fill="x")
        
        lbl_tags = ctk.CTkLabel(content_frame, text=self.spec_data["tags"], font=("Arial", 11, "bold"), text_color="#60a5fa", anchor="w", cursor="hand2")
        lbl_tags.pack(anchor="w", fill="x")
        
        lbl_desc = ctk.CTkLabel(self, text=self.spec_data["description"], font=("Arial", 14), text_color="#cbd5e1", wraplength=450, justify="left", anchor="w", cursor="hand2")
        lbl_desc.grid(row=1, column=1, sticky="nw", padx=(0, 15), pady=(5, 15))

        self.bind_click_recursively(self)

    def load_spec_data(self, sid):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, 'specializations.json')
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f).get(str(sid))
        except: return None

    def bind_click_recursively(self, widget):
        widget.bind("<Button-1>", self.open_url)
        for child in widget.winfo_children():
            try: child.configure(cursor="hand2") 
            except: pass
            self.bind_click_recursively(child)

    def open_url(self, event=None):
        current_time = time.time()
        if current_time - self.last_click_time < 1.5:
            return
        self.last_click_time = current_time
        webbrowser.open(self.target_url)

# --- VIEW PRINCIPAL ---
class ChatView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        try: self.ai = UniversityAI()
        except: self.ai = None
        self.tts = TTSManager()
        
        self.current_mode = 1
        self.current_lang = 'ro'
        self.voice_enabled = True
        self.keyboard_visible = False
        self.is_thinking = False
        self.pending_bubble = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.lbl_icon = ctk.CTkLabel(self.header_frame, text="✦", font=("Arial",24), text_color="#60a5fa")
        self.lbl_icon.grid(row=0, column=0, padx=20, pady=10)
        self.lbl_title = ctk.CTkLabel(self.header_frame, text="THREEB", font=("Roboto",18,"bold"))
        self.lbl_title.grid(row=0, column=1, sticky="w")

        self.controls = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.controls.grid(row=0, column=2, padx=15)
        self.btn_ro = self.mk_btn("RO", 'ro')
        self.btn_en = self.mk_btn("EN", 'en')
        self.btn_ua = self.mk_btn("UA", 'ua')
        
        self.btn_voice = ctk.CTkButton(self.controls, text="🔊", width=35, height=35, corner_radius=18, fg_color="#334155", hover_color="#475569", command=self.toggle_voice)
        self.btn_voice.pack(side="left", padx=10)
        ctk.CTkButton(self.controls, text="✕", width=35, height=35, corner_radius=18, fg_color="#ef4444", hover_color="#dc2626", command=self.go_home).pack(side="left")

        # Persona Bar
        self.persona_bar = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.persona_bar.grid(row=0, column=0, sticky="s", pady=(55,0))
        self.btn_p1 = self.mk_pers("Standard", 1)
        self.btn_p2 = self.mk_pers("Profesor", 2)
        self.btn_p3 = self.mk_pers("Bro", 3)

        # Chat Scroll
        self.chat_scroll = TouchScrollableFrame(self, corner_radius=0)
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Footer Area
        self.bottom_area = ctk.CTkFrame(self, height=140, corner_radius=0, fg_color="transparent")
        self.bottom_area.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.sugg_frame = ctk.CTkFrame(self.bottom_area, height=40, fg_color="transparent")
        self.sugg_frame.pack(fill="x", pady=(0, 10), padx=20)
        
        self.input_capsule = ctk.CTkFrame(self.bottom_area, height=60, corner_radius=30)
        self.input_capsule.pack(fill="x", padx=20, pady=5)
        
        self.entry_msg = ctk.CTkEntry(self.input_capsule, placeholder_text="...", height=50, corner_radius=25, border_width=0, font=("Roboto",16), fg_color="transparent")
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(15, 5), pady=5)
        self.entry_msg.bind("<Return>", lambda e: self.send_message())
        self.entry_msg.bind("<Button-1>", self.open_keyboard)
        self.entry_msg.bind("<FocusIn>", self.open_keyboard)
        
        self.btn_send = ctk.CTkButton(self.input_capsule, text="➤", width=50, height=50, corner_radius=25, font=("Arial",20), command=self.send_message)
        self.btn_send.pack(side="right", padx=5, pady=5)

        self.keyboard = TouchKeyboard(self, self.entry_msg, self.send_message, self.close_keyboard)

        # Startup
        self.apply_theme(1)
        self.change_language('ro')
        welcome = TRANSLATIONS['ro']['welcome']
        self.add_message(welcome, "AI")
        self.after(800, lambda: self.tts.speak(welcome) if self.voice_enabled else None)

    def mk_btn(self, txt, code):
        b = ctk.CTkButton(self.controls, text=txt, width=40, height=30, corner_radius=15, fg_color="transparent", border_width=1, border_color="#475569", font=("Arial",11,"bold"), command=lambda: self.change_language(code))
        b.pack(side="left", padx=2)
        return b
    def mk_pers(self, txt, idx):
        b = ctk.CTkButton(self.persona_bar, text=txt, height=32, corner_radius=16, fg_color="#334155", font=("Arial",12), command=lambda: self.change_personality(idx))
        b.pack(side="left", padx=5)
        return b

    # --- FUNCTII RAPORTARE ---
    def show_popup_report(self):
        """Afiseaza un popup visual care confirma trimiterea"""
        overlay = ctk.CTkFrame(self, fg_color="transparent")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        box = ctk.CTkFrame(overlay, fg_color="#1a1a1a", border_color="#333", border_width=2, corner_radius=20)
        box.place(relx=0.5, rely=0.5, anchor="center")
        
        msg = TRANSLATIONS[self.current_lang]['popup_report']
        lbl = ctk.CTkLabel(box, text=msg, font=("Arial", 20, "bold"), text_color="#4BB543")
        lbl.pack(padx=40, pady=30)
        
        # Distrugem popup-ul dupa 2 secunde
        self.after(2000, overlay.destroy)

    def handle_report(self, text_content):
        """Functia apelata cand userul apasa 'Raporteaza'"""
        print('pop')
        # 1. Afisam Pop-up-ul imediat
        self.show_popup_report()
        
        # 2. Trimitem mailul pe un thread separat pentru a nu bloca GUI
        threading.Thread(target=self._send_email_yagmail, args=(text_content,), daemon=True).start()

    def _send_email_yagmail(self, content):
        """Logica de trimitere efectiva prin Yagmail"""
        if not SENDER_EMAIL or not SENDER_PASSWORD or not ADMIN_EMAIL:
            print("❌ EROARE: Credentiale lipsa in .env (ADMIN_EMAIL, EMAIL_USER, EMAIL_PASS)")
            return
            
        try:
            yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subject = f"REPORT: Message Reported at {timestamp}"
            
            body = [
                "<h3>⚠️ Raport Mesaj Utilizator</h3>",
                "<p>Un utilizator a raportat urmatorul mesaj generat de AI:</p>",
                "<hr>",
                f"<blockquote style='background: #f0f0f0; padding: 10px;'>{content}</blockquote>",
                "<hr>",
                f"<p><small>Trimis automat de THREEB App la {timestamp}</small></p>"
            ]
            
            yag.send(to=ADMIN_EMAIL, subject=subject, contents=body)
            print(f"✅ Report email sent successfully to {ADMIN_EMAIL}")
            
        except Exception as e:
            print(f"❌ Failed to send report email: {e}")

    def go_home(self):
        if hasattr(self.tts, 'stop'): self.tts.stop()
        if hasattr(self.controller, 'show_home'): self.controller.show_home()
        else: self.controller.destroy()

    def open_keyboard(self, e=None):
        if self.is_thinking: return
        if not self.keyboard_visible:
            self.keyboard.show(); self.keyboard_visible=True
            self.sugg_frame.pack_forget(); self.bottom_area.grid_configure(pady=(0, 250))
            
    def close_keyboard(self):
        self.keyboard_visible=False
        self.bottom_area.grid_configure(pady=(0, 10))
        self.sugg_frame.pack(fill="x", pady=(0, 10), padx=20, before=self.input_capsule)

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        self.btn_voice.configure(text="🔊" if self.voice_enabled else "🔇", text_color="green" if self.voice_enabled else "gray")
        self.tts.unpause() if self.voice_enabled else self.tts.pause()

    def change_language(self, code):
        if self.is_thinking: return
        self.current_lang = code
        if self.ai: self.ai.set_language(code)
        self.tts.set_language(code)
        t = TRANSLATIONS[code]
        self.lbl_title.configure(text=t['title'])
        self.entry_msg.configure(placeholder_text=t['hint'])
        self.btn_p1.configure(text=t['p1']); self.btn_p2.configure(text=t['p2']); self.btn_p3.configure(text=t['p3'])
        
        for b, c in [(self.btn_ro,'ro'),(self.btn_en,'en'),(self.btn_ua,'ua')]:
            b.configure(fg_color=THEMES[self.current_mode]["accent"] if c==code else "transparent", text_color="white")
            
        self.refresh_suggestions()
        self.show_toast(t['sys_lang'])

    def change_personality(self, idx):
        if self.current_mode==idx or self.is_thinking: return
        self.current_mode = idx
        if self.ai: self.ai.set_personality(idx)
        if idx==1: self.tts.set_gender('female')
        else: self.tts.set_gender('male')
        self.apply_theme(idx)
        self.show_toast(TRANSLATIONS[self.current_lang]['sys_change'] + TRANSLATIONS[self.current_lang][f'p{idx}'])

    def apply_theme(self, idx):
        t = THEMES[idx]
        self.configure(fg_color=t["bg"])
        self.header_frame.configure(fg_color=t["header"])
        self.lbl_title.configure(text_color=t["accent"])
        self.lbl_icon.configure(text_color=t["accent"])
        self.chat_scroll.configure(fg_color=t["bg"])
        self.entry_msg.configure(fg_color=t["input_bg"], text_color="white", font=(t["font"], 16))
        self.btn_send.configure(fg_color=t["accent"], hover_color=t["btn_hover"])
        bs = [self.btn_p1, self.btn_p2, self.btn_p3]
        for i, b in enumerate(bs, 1):
            b.configure(fg_color=t["accent"] if i==idx else "#334155", text_color="black" if i==idx and i!=3 else "white")

    def show_toast(self, txt):
        f = ctk.CTkFrame(self.chat_scroll, fg_color="#333", corner_radius=15)
        l = ctk.CTkLabel(f, text=txt, text_color="white", font=("Arial",12))
        l.pack(padx=15, pady=5); f.pack(pady=10)
        self.chat_scroll.bind_child_scroll(f); self.chat_scroll.bind_child_scroll(l)
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
        self.after(2500, f.destroy)

    def refresh_suggestions(self):
        for w in self.sugg_frame.winfo_children(): w.destroy()
        qs = self.ai.get_random_shortcuts() if self.ai else ["Error"]
        for q in qs:
            ctk.CTkButton(self.sugg_frame, text=q, fg_color="#333", hover_color="#444", height=30, corner_radius=15, font=(None,12), command=lambda x=q: self.sub_sug(x)).pack(side="left", padx=5, expand=True, fill="x")

    def sub_sug(self, txt):
        if not self.is_thinking:
            self.entry_msg.delete(0, "end"); self.entry_msg.insert(0, txt); self.send_message()

    def send_message(self):
        txt = self.entry_msg.get()
        if not txt: return
        self.tts.stop()
        self.close_keyboard()
        
        self.entry_msg.delete(0, "end")
        self.is_thinking = True
        
        self.btn_send.configure(state="disabled")
        self.entry_msg.configure(state="disabled", placeholder_text="...")
        
        self.add_message(txt, "User")
        
        thk = "⏳ " + TRANSLATIONS[self.current_lang].get('thinking', '...')
        self.pending_bubble = self.add_message(thk, "AI")
        
        threading.Thread(target=self.proc_ai, args=(txt,), daemon=True).start()

    def proc_ai(self, txt):
        resp_data = self.ai.ask_gemini(txt) if self.ai else {"msg": "Error AI", "ref_ids": []}
        if not self.winfo_exists(): return
        self.after(0, lambda: self.fin_ai(resp_data))

    def fin_ai(self, resp_data):
        text_resp = resp_data.get("msg", "...")
        ref_ids = resp_data.get("ref_ids", [])
        
        if self.pending_bubble:
            self.pending_bubble.update_text(text_resp)
            self.pending_bubble = None
        else:
            self.add_message(text_resp, "AI")
            
        if ref_ids:
            for sid in ref_ids:
                self.add_specialization_card(sid)

        self.chat_scroll._parent_canvas.yview_moveto(1.0)
        
        self.is_thinking = False
        self.btn_send.configure(state="normal")
        self.entry_msg.configure(state="normal", placeholder_text=TRANSLATIONS[self.current_lang]['hint'])
        
        if self.voice_enabled: self.tts.speak(text_resp)
        self.after(100, self.refresh_suggestions)

    def add_message(self, txt, snd):
        if not self.winfo_exists(): return None
        # AICI SE FACE LEGATURA CU FUNCTIA DE RAPORTARE
        cb = self.handle_report if snd=="AI" else None
        
        b = ChatBubble(self.chat_scroll, text=txt, sender=snd, theme_id=self.current_mode, current_lang=self.current_lang, report_callback=cb)
        if snd=="AI": b.pack(pady=5, padx=10, anchor="w")
        else: b.pack(pady=5, padx=10, anchor="e")
        self.chat_scroll.bind_child_scroll(b)
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
        return b

    def add_specialization_card(self, sid):
        card = SpecializationCard(self.chat_scroll, sid)
        card.pack(pady=10, padx=5, fill="x")
        self.chat_scroll.bind_child_scroll(card)
        self.chat_scroll._parent_canvas.yview_moveto(1.0)