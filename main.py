import flet as ft
from assistant import UniversityAI
from tts_manager import TTSManager # <--- IMPORT NOU
import time
import threading

def main(page: ft.Page):
    # --- 1. CONFIGURARE ---
    page.title = "THREEB"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10 
    page.spacing = 5
    page.window.maximized = True

    page.fonts = {
        "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf"
    }

    try:
        ai = UniversityAI()
    except:
        ai = None

    # Inițializare TTS
    tts = TTSManager()
    voice_enabled = True # Pornit implicit

    # --- TEMATICI ---
    themes = {
        1: { # ANA (Standard)
            "name": "Ana (Studentă)",
            "page_bg": "#121212",
            "input_bg": "#262626",
            "ai_bubble": ft.Colors.BLUE_900,
            "accent": ft.Colors.BLUE_400,
            "font_family": "Roboto",
            "icon": ft.Icons.FACE_3, # Fata
            "header_icon": ft.Icons.RECORD_VOICE_OVER,
            "btn_active": ft.Colors.BLUE_700
        },
        2: { # PROFESOR IONESCU
            "name": "Prof. Ionescu",
            "page_bg": "#1B3A28",
            "input_bg": "#2E5A43",
            "ai_bubble": "#3E2723",
            "accent": ft.Colors.AMBER_400,
            "font_family": "Serif",
            "icon": ft.Icons.FACE, # Barbat ochelari/generic
            "header_icon": ft.Icons.HISTORY_EDU,
            "btn_active": ft.Colors.AMBER_800
        },
        3: { # ALEX (Student)
            "name": "Alex (Bro)",
            "page_bg": "#1A0B2E",
            "input_bg": "#2D1B4E",
            "ai_bubble": "#4A148C",
            "accent": ft.Colors.PINK_400,
            "font_family": "Monospace",
            "icon": ft.Icons.HEADSET_MIC, # Gamer
            "header_icon": ft.Icons.GAMEPAD,
            "btn_active": ft.Colors.PINK_600
        }
    }

    current_mode = 1 
    page.bgcolor = themes[1]["page_bg"]

    # --- 2. HEADER ---
    header_icon_control = ft.Icon(themes[1]["header_icon"], size=28, color=themes[1]["accent"])
    title_text = ft.Text("THREEB", size=22, weight="bold", font_family=themes[1]["font_family"])

    # Funcție toggle voce
    def toggle_voice(e):
        nonlocal voice_enabled
        voice_enabled = not voice_enabled
        btn_voice.icon = ft.Icons.VOLUME_UP if voice_enabled else ft.Icons.VOLUME_OFF
        btn_voice.icon_color = ft.Colors.GREEN if voice_enabled else ft.Colors.RED
        if not voice_enabled:
            tts.stop() # Oprim daca vorbeste
        page.update()

    btn_voice = ft.IconButton(ft.Icons.VOLUME_UP, on_click=toggle_voice, icon_color="green")

    header = ft.Row(
        [
            ft.Row([header_icon_control, title_text], spacing=10),
            ft.Row([
                btn_voice, # Butonul de voce
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: page.window.destroy(), icon_color="red", icon_size=24)
            ])
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        height=40
    )

    # --- 3. FUNCȚII TEMATICĂ ---
    def change_personality(e, index):
        nonlocal current_mode
        current_mode = index
        if ai: ai.set_personality(index)
        
        t = themes[index]
        page.bgcolor = t["page_bg"]
        txt_input.bgcolor = t["input_bg"]
        txt_input.text_style = ft.TextStyle(font_family=t["font_family"], color=ft.Colors.WHITE, size=16)
        
        header_icon_control.name = t["header_icon"]
        header_icon_control.color = t["accent"]
        title_text.font_family = t["font_family"]
        
        for btn, idx in [(btn_p1, 1), (btn_p2, 2), (btn_p3, 3)]:
            btn.style.bgcolor = ft.Colors.GREY_800 if idx != index else t["btn_active"]
            btn.content.font_family = t["font_family"]

        btn_send.icon_color = t["accent"]
        add_message(f"✨ Ai ales: {t['name']}", "System")
        
        # Salut Audio la schimbare
        if voice_enabled:
            intro_msg = f"Salut! Eu sunt {t['name'].split(' ')[0]}."
            tts.speak(intro_msg)

        page.update()

    def get_btn_style():
        return ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE, padding=5)

    btn_p1 = ft.ElevatedButton(content=ft.Text("Ana", size=13), on_click=lambda e: change_personality(e, 1), style=get_btn_style(), height=35, expand=True)
    btn_p1.style.bgcolor = themes[1]["btn_active"] 
    btn_p2 = ft.ElevatedButton(content=ft.Text("Prof. Ionescu", size=13), on_click=lambda e: change_personality(e, 2), style=get_btn_style(), height=35, expand=True)
    btn_p3 = ft.ElevatedButton(content=ft.Text("Alex", size=13), on_click=lambda e: change_personality(e, 3), style=get_btn_style(), height=35, expand=True)

    personality_row = ft.Row([btn_p1, btn_p2, btn_p3], spacing=5)

    # --- 4. CHAT & INPUT ---
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    txt_input = ft.TextField(
        hint_text="Întreabă ceva...", text_size=16, expand=True, border_radius=20, filled=True,
        bgcolor=themes[1]["input_bg"], content_padding=15, text_style=ft.TextStyle(font_family="Roboto"),
        on_submit=lambda e: send_message(None), height=50
    )

    suggestions_row = ft.Row(spacing=5, alignment=ft.MainAxisAlignment.CENTER)

    # --- LOGICA ---
    def add_message(text, sender):
        t = themes[current_mode]
        
        if sender == "AI":
            align = ft.MainAxisAlignment.START
            bg_col = t["ai_bubble"] 
            icon_type = t["icon"]
            text_col = ft.Colors.WHITE
            font_use = t["font_family"]
            border_radius = ft.border_radius.only(top_left=0, top_right=15, bottom_left=15, bottom_right=15)
        elif sender == "System":
            align = ft.MainAxisAlignment.CENTER
            bg_col = ft.Colors.with_opacity(0.3, "#000000")
            icon_type = ft.Icons.AUTO_AWESOME
            text_col = t["accent"]
            font_use = t["font_family"]
            border_radius = ft.border_radius.all(8)
        else: # User
            align = ft.MainAxisAlignment.END
            bg_col = ft.Colors.GREY_800
            icon_type = ft.Icons.PERSON
            text_col = ft.Colors.WHITE
            font_use = t["font_family"]
            border_radius = ft.border_radius.only(top_left=15, top_right=0, bottom_left=15, bottom_right=15)

        adaptive_width = None
        is_long = len(text) > 40
        if is_long: adaptive_width = 500

        content_row = ft.Row([
            ft.Icon(icon_type, size=16, color=t["accent"] if sender == "AI" else ft.Colors.GREY_400),
            ft.Text(text, size=15, color=text_col, selectable=True, font_family=font_use, expand=is_long, weight="bold" if sender=="System" else "normal")
        ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=8)

        bubble = ft.Row(
            [ft.Container(content=content_row, bgcolor=bg_col, padding=10, border_radius=border_radius, width=adaptive_width)],
            alignment=align, opacity=1, animate_opacity=500
        )
        chat_list.controls.append(bubble)
        page.update()

        if sender == "System":
            def fade_out_task():
                time.sleep(2)
                bubble.opacity = 0
                page.update()
                time.sleep(0.6)
                chat_list.controls.remove(bubble)
                page.update()
            threading.Thread(target=fade_out_task, daemon=True).start()

    def refresh_suggestions():
        suggestions_row.controls.clear()
        t = themes[current_mode]
        questions = ai.get_random_shortcuts() if ai else ["Verifică API", "Eroare"]
        for q in questions:
            btn = ft.ElevatedButton(
                content=ft.Text(q, font_family=t["font_family"], size=12),
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
        
        # --- AICI SE INTAMPLA MAGIA VOCALA ---
        if voice_enabled:
            tts.speak(response)
        # -------------------------------------
        
        refresh_suggestions()

    btn_send = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color=themes[1]["accent"], icon_size=30, on_click=send_message)

    add_message("Bună! Eu sunt Ana. Cu ce te ajut?", "AI")
    if voice_enabled: tts.speak("Bună! Eu sunt Ana. Cu ce te ajut?")
    
    try: refresh_suggestions()
    except: pass

    page.add(
        header, personality_row, ft.Divider(height=1, color=ft.Colors.GREY_900),
        chat_list, ft.Divider(height=1, color=ft.Colors.GREY_900),
        suggestions_row, ft.Row([txt_input, btn_send], alignment=ft.MainAxisAlignment.CENTER, spacing=5)
    )

ft.app(target=main)