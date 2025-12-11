# settings_module.py

import customtkinter as ctk

# --- Configuration (using constants from home_module for consistency) ---
TITLE_BLUE = "#4da6ff" 

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.setup_ui()
        
    def setup_ui(self):
        # Header Frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(40, 60))
        
        title_label = ctk.CTkLabel(
            header_frame, text="APPLICATION SETTINGS ⚙", font=("Arial", 28, "bold"), text_color=TITLE_BLUE
        )
        title_label.pack()

        # Content Frame for settings widgets
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(pady=20, padx=50)

        # --- Appearance Mode (Skin) Setting ---
        self.setup_setting_row(
            content_frame, 
            0, 
            "Appearance Mode (Skin):", 
            ["Light", "Dark", "System"], 
            self.change_appearance_mode_event
        )

        # --- Language Setting (Placeholder) ---
        self.setup_setting_row(
            content_frame, 
            1, 
            "Language:", 
            ["English (Default)", "Spanish", "French"], 
            self.change_language_event
        )
        
        # --- NEW: Mascot Skin Setting (Placeholder) ---
        self.setup_setting_row(
            content_frame, 
            2, 
            "Mascot Skin:", 
            ["Default Bot", "Vibrant", "Monochrome", "8-bit"], # Example skins
            self.change_mascot_skin_event
        )

        # --- Back Button ---
        back_button = ctk.CTkButton(
            self,
            text="< Back to Home",
            command=self.controller.show_home,
            width=200,
            height=40,
            font=("Arial", 16, "bold")
        )
        back_button.pack(pady=(80, 20))

    def setup_setting_row(self, parent_frame, row, label_text, options, command_func):
        # Label
        label = ctk.CTkLabel(parent_frame, text=label_text, font=("Arial", 16))
        label.grid(row=row, column=0, padx=20, pady=15, sticky="w")
        
        # Option Menu
        option_menu = ctk.CTkOptionMenu(
            parent_frame,
            values=options,
            command=command_func,
            width=150
        )
        
        # Set current value for appearance mode
        if "Appearance Mode" in label_text:
            current_mode = ctk.get_appearance_mode().capitalize()
            option_menu.set(current_mode)
        else:
            option_menu.set(options[0]) # Default for other settings
            
        option_menu.grid(row=row, column=1, padx=20, pady=15, sticky="e")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_language_event(self, new_language: str):
        print(f"Language changed to: {new_language}. (Full translation logic not implemented)")
        
    # NEW METHOD: Mascot Skin Event Handler
    def change_mascot_skin_event(self, new_skin: str):
        # This function would contain the logic to update the mascot's appearance 
        # in a real application.
        print(f"Mascot skin changed to: {new_skin}. (Visual change not implemented)")
        
    def cleanup(self):
        # No cleanup needed for a simple CTkFrame view
        pass