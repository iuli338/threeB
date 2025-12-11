# settings_module.py

import customtkinter as ctk

# --- Configuration ---
# Format: (Light Mode Color, Dark Mode Color)
TITLE_BLUE = ("#1f6aa5", "#4da6ff")      # Darker blue for light mode readability
ACCENT_COLOR = ("#dbdbdb", "#2B2B2B")    # Light gray card vs Dark gray card
TEXT_COLOR = ("#333333", "#E0E0E0")      # Dark text vs Light text
BTN_FG_COLOR = ("#cccccc", "#333333")    # Light btn vs Dark btn
BTN_HOVER_COLOR = ("#bbbbbb", "#444444")

# Dictionary for translations
TRANSLATIONS = {
    "English": {
        "title": "SETTINGS",
        "back": "← Back",
        "appearance": "Appearance Mode",
        "language": "System Language",
        "mascot": "Assistant Avatar",
        "opt_light": "Light",
        "opt_dark": "Dark",
        "opt_system": "System"
    },
    "Romanian": {
        "title": "SETĂRI",
        "back": "← Înapoi",
        "appearance": "Mod Aspect",
        "language": "Limbă Sistem",
        "mascot": "Avatar Asistent",
        "opt_light": "Luminos",
        "opt_dark": "Întunecat",
        "opt_system": "Sistem"
    },
    "Ukrainian": {
        "title": "НАЛАШТУВАННЯ",
        "back": "← Назад",
        "appearance": "Режим вигляду",
        "language": "Мова системи",
        "mascot": "Аватар помічника",
        "opt_light": "Світлий",
        "opt_dark": "Темний",
        "opt_system": "Система"
    }
}

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Grid layout: Row 0 = Header, Row 1 = Content
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Store widget references to update text dynamically
        self.labels = {} 
        self.current_lang = "English" # Default language for this screen

        self.pack(fill="both", expand=True)
        self.setup_ui()
        
    def setup_ui(self):
        
        # --- 1. Header Section ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        
        # Back Button
        self.btn_back = ctk.CTkButton(
            header_frame, 
            text=TRANSLATIONS[self.current_lang]["back"], 
            command=self.controller.show_home,
            width=85, 
            height=35,
            fg_color=BTN_FG_COLOR,
            text_color=TEXT_COLOR,
            hover_color=BTN_HOVER_COLOR,
            font=("Arial", 18)
        )
        self.btn_back.pack(side="left")

        # Title
        self.label_title = ctk.CTkLabel(
            header_frame, 
            text=TRANSLATIONS[self.current_lang]["title"], 
            font=("Arial", 24, "bold"), 
            text_color=TITLE_BLUE
        )
        self.label_title.pack(side="left", padx=20)

        # --- 2. Main Settings Card ---
        self.content_card = ctk.CTkFrame(self, fg_color=ACCENT_COLOR, corner_radius=15)
        self.content_card.grid(row=1, column=0, sticky="nwe", padx=40, pady=10)
        
        self.content_card.grid_columnconfigure(0, weight=1) # Label column
        self.content_card.grid_columnconfigure(1, weight=0) # Control column

        # --- Setting Rows ---
        
        # Row 0: Appearance
        # We need to map current system state to dropdown values
        current_mode = ctk.get_appearance_mode()
        # Simple map to ensure Capitalized string matches dropdown
        mode_map = {"Light": "Light", "Dark": "Dark", "System": "System"}
        
        self.setup_setting_row(
            row=0, 
            key="appearance", # Key in TRANSLATIONS dict
            options=["Light", "Dark", "System"], 
            command_func=self.change_appearance_mode_event,
            default_val=mode_map.get(current_mode, "System")
        )

        # Row 1: Language
        self.setup_setting_row(
            row=1, 
            key="language",
            options=["Romanian", "English", "Ukrainian"], 
            command_func=self.change_language_event,
            default_val="English"
        )
        
        # Row 2: Mascot
        self.setup_setting_row(
            row=2, 
            key="mascot",
            options=["Default Bot", "Vibrant", "Monochrome", "8-bit"], 
            command_func=self.change_mascot_skin_event,
            default_val="Default Bot"
        )

    def setup_setting_row(self, row, key, options, command_func, default_val):
        """Helper to create a consistent row style"""
        
        # Label (Left)
        label = ctk.CTkLabel(
            self.content_card, 
            text=TRANSLATIONS[self.current_lang][key], 
            font=("Arial", 20),
            text_color=TEXT_COLOR
        )
        label.grid(row=row, column=0, padx=30, pady=25, sticky="w")
        
        # Store reference for language updates
        self.labels[key] = label
        
        # Option Menu (Right)
        option_menu = ctk.CTkOptionMenu(
            self.content_card,
            values=options,
            command=command_func,
            width=180,
            height=35,
            font=("Arial", 16),
            
            # --- Adaptive Styling (Tuple colors) ---
            fg_color=("gray75", "#444"),           # Light/Dark button body
            button_color=("gray65", "#555"),       # Light/Dark arrow area
            button_hover_color=("gray55", "#666"), # Hover
            text_color=TEXT_COLOR,                 # Adaptive text
            
            # --- Dropdown Styling ---
            dropdown_fg_color=("gray85", "#333"),  
            dropdown_hover_color=TITLE_BLUE,       
            dropdown_text_color=TEXT_COLOR,
            dropdown_font=("Arial", 15)
        )
        option_menu.set(default_val)
        option_menu.grid(row=row, column=1, padx=30, pady=25, sticky="e") 
        
        # Add a subtle separator line (unless it's the last item)
        if row < 2: 
            separator = ctk.CTkFrame(self.content_card, height=2, fg_color=("gray80", "#3a3a3a"))
            separator.grid(row=row, column=0, columnspan=2, sticky="ew", padx=20, pady=(60, 0)) 

    # --- Event Handlers ---

    def change_appearance_mode_event(self, new_appearance_mode: str):
        # Determine the internal mode string (ctk expects "Light", "Dark", or "System")
        # In this specific UI, the dropdown values match exactly, so we pass directly.
        ctk.set_appearance_mode(new_appearance_mode)

    def change_language_event(self, new_language: str):
        self.current_lang = new_language
        t = TRANSLATIONS[new_language]
        
        # Update Title and Back Button
        self.label_title.configure(text=t["title"])
        self.btn_back.configure(text=t["back"])
        
        # Update Row Labels using stored references
        for key, label_widget in self.labels.items():
            if key in t:
                label_widget.configure(text=t[key])

    def change_mascot_skin_event(self, new_skin: str):
        print(f"Mascot skin changed to: {new_skin}")
        
    def cleanup(self):
        pass