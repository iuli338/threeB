import flet as ft
from assistant import UniversityAI

def main(page: ft.Page):
    # --- 1. CONFIGURARE PAGINĂ ---
    page.title = "THREEB Assistant"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15
    page.window.maximized = True

    # Inițializare AI
    try:
        ai = UniversityAI()
    except:
        ai = None

    # --- 2. ELEMENTE UI ---
    
    # Header cu Titlu și Buton Exit
    header = ft.Row(
        [
            ft.Row([
                ft.Icon(ft.Icons.SMART_TOY_OUTLINED, size=35, color=ft.Colors.BLUE_400),
                ft.Text("THREEB", size=26, weight="bold"),
            ]),
            ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: page.window.destroy(), icon_color="red", icon_size=30)
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # --- ZONA BUTOANE PERSONALITATE ---
    # Definim funcția care se activează la click
    def change_personality(e, index):
        # 1. Schimbăm în backend
        if ai: ai.set_personality(index)
        
        # 2. Schimbăm culorile vizual
        btn_p1.style.bgcolor = ft.Colors.GREY_800 if index != 1 else ft.Colors.BLUE_600
        btn_p2.style.bgcolor = ft.Colors.GREY_800 if index != 2 else ft.Colors.GREEN_600
        btn_p3.style.bgcolor = ft.Colors.GREY_800 if index != 3 else ft.Colors.ORANGE_600
        
        # 3. Anunțăm în chat (Feedback vizual)
        names = {1: "Standard", 2: "Profesor", 3: "Student (Bro)"}
        add_message(f"Mod activat: {names[index]}", "System")
        
        page.update()

    # Creăm butoanele
    # Stil comun
    def get_style(active_color):
        return ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=ft.Colors.GREY_800, # Default grey
            color=ft.Colors.WHITE,
            animation_duration=300
        )

    btn_p1 = ft.ElevatedButton(
        "Standard", 
        on_click=lambda e: change_personality(e, 1),
        style=get_style(ft.Colors.BLUE_600),
        height=40, expand=True
    )
    # Îl setăm pe primul ca fiind activ (Albastru) din start
    btn_p1.style.bgcolor = ft.Colors.BLUE_600

    btn_p2 = ft.ElevatedButton(
        "Profesor", 
        on_click=lambda e: change_personality(e, 2),
        style=get_style(ft.Colors.GREEN_600),
        height=40, expand=True
    )

    btn_p3 = ft.ElevatedButton(
        "Student (Bro)", 
        on_click=lambda e: change_personality(e, 3),
        style=get_style(ft.Colors.ORANGE_600),
        height=40, expand=True
    )

    # Rândul cu butoane
    personality_row = ft.Row(
        [btn_p1, btn_p2, btn_p3],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    # --- RESTUL UI-ului ---

    chat_list = ft.ListView(expand=True, spacing=15, auto_scroll=True)

    txt_input = ft.TextField(
        hint_text="Întreabă ceva...",
        text_size=18, expand=True, border_radius=25, filled=True,
        bgcolor=ft.Colors.GREY_900,
        content_padding=20,
        on_submit=lambda e: send_message(None)
    )

    suggestions_row = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)

    # --- 3. LOGICA BULELOR ADAPTIVE ---

    def add_message(text, sender):
        # Configurare culori în funcție de cine trimite
        if sender == "AI":
            align = ft.MainAxisAlignment.START
            bg_col = ft.Colors.BLUE_900
            icon_type = ft.Icons.ASSISTANT
            border_radius = ft.border_radius.only(top_left=0, top_right=20, bottom_left=20, bottom_right=20)
        elif sender == "System": # Mesaj de sistem (schimbare mod)
            align = ft.MainAxisAlignment.CENTER
            bg_col = ft.Colors.GREY_900
            icon_type = ft.Icons.SETTINGS
            border_radius = ft.border_radius.all(10)
        else: # User
            align = ft.MainAxisAlignment.END
            bg_col = ft.Colors.GREY_800
            icon_type = ft.Icons.PERSON
            border_radius = ft.border_radius.only(top_left=20, top_right=0, bottom_left=20, bottom_right=20)

        # Logica de lățime adaptivă
        adaptive_width = None
        is_long = len(text) > 45
        if is_long: adaptive_width = 550

        content = ft.Row([
            ft.Icon(icon_type, size=16 if sender=="System" else 20, color=ft.Colors.GREY_400),
            ft.Text(text, size=14 if sender=="System" else 17, color=ft.Colors.WHITE, selectable=True, expand=is_long)
        ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=10)

        bubble = ft.Row(
            [ft.Container(content=content, bgcolor=bg_col, padding=10 if sender=="System" else 15, border_radius=border_radius, width=adaptive_width)],
            alignment=align
        )
        chat_list.controls.append(bubble)
        page.update()

    def refresh_suggestions():
        suggestions_row.controls.clear()
        if ai:
            questions = ai.get_random_shortcuts()
        else:
            questions = ["Verifică API", "Eroare", "Retry"]
            
        for q in questions:
            btn = ft.ElevatedButton(
                text=q,
                on_click=lambda e, question=q: click_suggestion(question),
                bgcolor=ft.Colors.GREY_800, color=ft.Colors.BLUE_100, height=50,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
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

        if ai:
            response = ai.ask_gemini(user_msg)
        else:
            response = "Eroare: AI neinițializat."
            
        add_message(response, "AI")
        refresh_suggestions()

    btn_send = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED, icon_color=ft.Colors.BLUE_400, icon_size=35,
        on_click=send_message
    )

    # --- 4. START ---
    add_message("Salut! Sunt THREEB. Întreabă-mă orice despre FACIEE!", "AI")
    refresh_suggestions()

    # Layout final
    page.add(
        header,
        ft.Container(height=5),
        personality_row, # Aici am pus butoanele noi
        ft.Divider(color=ft.Colors.GREY_800), 
        chat_list, 
        ft.Divider(color=ft.Colors.GREY_800),
        suggestions_row, 
        ft.Container(height=5),
        ft.Row([txt_input, btn_send], alignment=ft.MainAxisAlignment.CENTER)
    )

ft.app(target=main)