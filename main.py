import flet as ft
from assistant import UniversityAI
from tts_manager import TTSManager
import time
import threading

# --- DICȚIONAR TRADUCERI UI ---
TRANSLATIONS = {
    'ro': {
        'title': 'THREEB',
        'hint': 'Întreabă ceva...',
        'p1': 'Ana (Studentă)', 'p2': 'Prof. Ionescu', 'p3': 'Alex (Bro)',
        'sys_change': '✨ Mediu schimbat: ',
        'sys_lang': 'Limbă setată: Română',
        'welcome': 'Salut! Eu sunt Ana. Cu ce te ajut?'
    },
    'en': {
        'title': 'THREEB',
        'hint': 'Ask something...',
        'p1': 'Ana (Student)', 'p2': 'Prof. Jones', 'p3': 'Alex (Bro)',
        'sys_change': '✨ Theme changed: ',
        'sys_lang': 'Language set: English',
        'welcome': 'Hi! I am Ana. How can I help?'
    },
    'ru': {
        'title': 'THREEB',
        'hint': 'Спроси что-нибудь...',
        'p1': 'Ана (Студент)', 'p2': 'Проф. Иванов', 'p3': 'Алекс (Бро)',
        'sys_change': '✨ Тема изменена: ',
        'sys_lang': 'Язык: Русский',
        'welcome': 'Привет! Я Ана. Чем помочь?'
    }
}

def main(page: ft.Page):
    # --- CONFIGURARE ---
    page.title = "THREEB"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10 
    page.spacing = 5
    page.window.maximized = True
    # page.window.full_screen = True 

    page.fonts = {"Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf"}

    try:
        ai = UniversityAI()
    except:
        ai = None

    tts = TTSManager()
    
    # Stare aplicație
    app_state = {
        "voice_playing": True, # True = Play, False = Paused/Muted
        "lang": "ro",
        "mode": 1
    }

    # --- TEMATICI ---
    themes = {
        1: { "name": "Standard", "page_bg": "#121212", "input_bg": "#262626", "ai_bubble": ft.Colors.BLUE_900, "accent": ft.Colors.BLUE_400, "font": "Roboto", "icon": ft.Icons.FACE_3, "header_icon": ft.Icons.RECORD_VOICE_OVER, "btn": ft.Colors.BLUE_700 },
        2: { "name": "Profesor", "page_bg": "#1B3A28", "input_bg": "#2E5A43", "ai_bubble": "#3E2723", "accent": ft.Colors.AMBER_400, "font": "Serif", "icon": ft.Icons.FACE, "header_icon": ft.Icons.HISTORY_EDU, "btn": ft.Colors.AMBER_800 },
        3: { "name": "Student", "page_bg": "#1A0B2E", "input_bg": "#2D1B4E", "ai_bubble": "#4A148C", "accent": ft.Colors.PINK_400, "font": "Monospace", "icon": ft.Icons.HEADSET_MIC, "header_icon": ft.Icons.GAMEPAD, "btn": ft.Colors.PINK_600 }
    }

    page.bgcolor = themes[1]["page_bg"]

    # --- HEADER & CONTROLS ---
    
    header_icon = ft.Icon(themes[1]["header_icon"], size=28, color=themes[1]["accent"])
    title_text = ft.Text("THREEB", size=22, weight="bold")

    # 1. LOGICA PAUZĂ / PLAY
    def toggle_voice_pause(e):
        app_state["voice_playing"] = not app_state["voice_playing"]
        
        if app_state["voice_playing"]:
            # Dăm UNPAUSE (continuă)
            btn_voice.icon = ft.Icons.PAUSE_CIRCLE_FILLED
            btn_voice.icon_color = ft.Colors.GREEN
            tts.unpause()
        else:
            # Dăm PAUSE (îngheață)
            btn_voice.icon = ft.Icons.PLAY_CIRCLE_FILLED
            btn_voice.icon_color = ft.Colors.RED
            tts.pause()
            
        page.update()

    btn_voice = ft.IconButton(ft.Icons.PAUSE_CIRCLE_FILLED, on_click=toggle_voice_pause, icon_color="green", tooltip="Pause/Resume Voice")

    # 2. LOGICA SCHIMBARE LIMBĂ
    def change_language(e, lang_code):
        app_state["lang"] = lang_code
        
        # Setăm limba în backend și TTS
        if ai: ai.set_language(lang_code)
        tts.set_language(lang_code)
        tts.stop() # Oprim audio vechi
        
        # Updatăm UI Texte
        t_dict = TRANSLATIONS[lang_code]
        title_text.value = t_dict['title']
        txt_input.hint_text = t_dict['hint']
        
        btn_p1.content.value = t_dict['p1']
        btn_p2.content.value = t_dict['p2']
        btn_p3.content.value = t_dict['p3']
        
        # Stil butoane limbă
        btn_ro.style.bgcolor = ft.Colors.BLUE_900 if lang_code == 'ro' else ft.Colors.TRANSPARENT
        btn_en.style.bgcolor = ft.Colors.BLUE_900 if lang_code == 'en' else ft.Colors.TRANSPARENT
        btn_ru.style.bgcolor = ft.Colors.BLUE_900 if lang_code == 'ru' else ft.Colors.TRANSPARENT

        add_message(t_dict['sys_lang'], "System")
        refresh_suggestions()
        page.update()

    # Butoane Limbă
    def lang_btn_style():
        return ft.ButtonStyle(padding=5, shape=ft.RoundedRectangleBorder(radius=5))

    btn_ro = ft.TextButton("RO", on_click=lambda e: change_language(e, 'ro'), style=lang_btn_style())
    btn_en = ft.TextButton("EN", on_click=lambda e: change_language(e, 'en'), style=lang_btn_style())
    btn_ru = ft.TextButton("RU", on_click=lambda e: change_language(e, 'ru'), style=lang_btn_style())
    
    btn_ro.style.bgcolor = ft.Colors.BLUE_900

    # Asamblare Header
    header = ft.Row(
        [
            ft.Row([header_icon, title_text], spacing=10),
            ft.Row([
                btn_ro, btn_en, btn_ru,
                ft.Container(width=10),
                btn_voice,
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: page.window.destroy(), icon_color="red", icon_size=24)
            ])
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, height=40
    )

    # --- MAIN UI LOGIC ---

    def change_personality(e, index):
        app_state["mode"] = index
        if ai: ai.set_personality(index)
        
        # --- LOGICA SCHIMBARE VOCE (GEN) ---
        # 1 = Ana (Female), 2 = Profesor (Male), 3 = Alex (Male)
        if index == 1:
            tts.set_gender('female')
        else:
            tts.set_gender('male')
        # -----------------------------------

        t = themes[index]
        page.bgcolor = t["page_bg"]
        txt_input.bgcolor = t["input_bg"]
        txt_input.text_style = ft.TextStyle(font_family=t["font"], color=ft.Colors.WHITE, size=16)
        
        header_icon.name = t["header_icon"]
        header_icon.color = t["accent"]
        title_text.font_family = t["font"]
        
        for btn, idx in [(btn_p1, 1), (btn_p2, 2), (btn_p3, 3)]:
            btn.style.bgcolor = ft.Colors.GREY_800 if idx != index else t["btn"]
            btn.content.font_family = t["font"]

        btn_send.icon_color = t["accent"]
        
        msg = TRANSLATIONS[app_state["lang"]]['sys_change'] + t["name"]
        add_message(msg, "System")
        page.update()

    def get_btn_style():
        return ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE, padding=5)

    btn_p1 = ft.ElevatedButton(content=ft.Text(TRANSLATIONS['ro']['p1'], size=13), on_click=lambda e: change_personality(e, 1), style=get_btn_style(), height=35, expand=True)
    btn_p1.style.bgcolor = themes[1]["btn"] 
    btn_p2 = ft.ElevatedButton(content=ft.Text(TRANSLATIONS['ro']['p2'], size=13), on_click=lambda e: change_personality(e, 2), style=get_btn_style(), height=35, expand=True)
    btn_p3 = ft.ElevatedButton(content=ft.Text(TRANSLATIONS['ro']['p3'], size=13), on_click=lambda e: change_personality(e, 3), style=get_btn_style(), height=35, expand=True)

    personality_row = ft.Row([btn_p1, btn_p2, btn_p3], spacing=5)

    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    txt_input = ft.TextField(
        hint_text=TRANSLATIONS['ro']['hint'], text_size=16, expand=True, border_radius=20, filled=True,
        bgcolor=themes[1]["input_bg"], content_padding=15, text_style=ft.TextStyle(font_family="Roboto"),
        on_submit=lambda e: send_message(None), height=50
    )

    suggestions_row = ft.Row(spacing=5, alignment=ft.MainAxisAlignment.CENTER)

    def add_message(text, sender):
        t = themes[app_state["mode"]]
        if sender == "AI":
            align, bg_col, icon_type, text_col, rad = ft.MainAxisAlignment.START, t["ai_bubble"], t["icon"], ft.Colors.WHITE, ft.border_radius.only(0,15,15,15)
        elif sender == "System":
            align, bg_col, icon_type, text_col, rad = ft.MainAxisAlignment.CENTER, ft.Colors.with_opacity(0.3, "#000000"), ft.Icons.AUTO_AWESOME, t["accent"], ft.border_radius.all(8)
        else:
            align, bg_col, icon_type, text_col, rad = ft.MainAxisAlignment.END, ft.Colors.GREY_800, ft.Icons.PERSON, ft.Colors.WHITE, ft.border_radius.only(15,0,15,15)

        width = 500 if len(text) > 40 else None
        
        content = ft.Row([
            ft.Icon(icon_type, size=16, color=t["accent"] if sender == "AI" else ft.Colors.GREY_400),
            ft.Text(text, size=15, color=text_col, selectable=True, font_family=t["font"], expand=bool(width), weight="bold" if sender=="System" else "normal")
        ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=8)

        bubble = ft.Row([ft.Container(content=content, bgcolor=bg_col, padding=10, border_radius=rad, width=width)], alignment=align, opacity=1, animate_opacity=500)
        chat_list.controls.append(bubble)
        page.update()

        if sender == "System":
            def fade():
                time.sleep(2)
                bubble.opacity = 0
                page.update()
                time.sleep(0.6)
                chat_list.controls.remove(bubble)
                page.update()
            threading.Thread(target=fade, daemon=True).start()

    def refresh_suggestions():
        suggestions_row.controls.clear()
        t = themes[app_state["mode"]]
        questions = ai.get_random_shortcuts() if ai else ["Error"]
        for q in questions:
            btn = ft.ElevatedButton(
                content=ft.Text(q, font_family=t["font"], size=12),
                on_click=lambda e, question=q: click_suggestion(question),
                bgcolor=ft.Colors.GREY_800, color=ft.Colors.BLUE_100, height=40,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=5),
                expand=True
            )
            suggestions_row.controls.append(btn)
        page.update()

    def click_suggestion(text):
        txt_input.value = text
        send_message(None)

    def send_message(e):
        user_msg = txt_input.value
        if not user_msg: return
        add_message(user_msg, "User")
        txt_input.value = ""
        txt_input.focus()
        page.update()
        
        response = ai.ask_gemini(user_msg) if ai else "Eroare AI"
        add_message(response, "AI")
        
        if app_state["voice_playing"]:
            tts.speak(response)
            
        refresh_suggestions()

    btn_send = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color=themes[1]["accent"], icon_size=30, on_click=send_message)

    add_message(TRANSLATIONS['ro']['welcome'], "AI")
    if app_state["voice_playing"]: tts.speak(TRANSLATIONS['ro']['welcome'])
    try: refresh_suggestions()
    except: pass

    page.add(
        header, personality_row, ft.Divider(height=1, color=ft.Colors.GREY_900),
        chat_list, ft.Divider(height=1, color=ft.Colors.GREY_900),
        suggestions_row, ft.Row([txt_input, btn_send], alignment=ft.MainAxisAlignment.CENTER, spacing=5)
    )

ft.app(target=main)