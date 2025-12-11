# settings_module.py

import customtkinter as ctk

# --- Configuration (using constants from home_module for consistency) ---
TITLE_BLUE = "#4da6ff" 

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Use grid for the main frame to manage vertical space precisely
        self.grid_rowconfigure(0, weight=1)  # Content Frame row
        self.grid_rowconfigure(1, weight=0)  # Back Button row (fixed height)
        self.grid_columnconfigure(0, weight=1) # Center content horizontally
        self.pack(fill="both", expand=True)

        self.setup_ui()
        
    def setup_ui(self):
        
        # --- 1. Content Frame for settings widgets (Top section) ---
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Place content_frame in the top row (row 0)
        content_frame.grid(row=0, column=0, pady=(40, 10), padx=50, sticky="nwe")
        
        # Configure the grid within the content frame for centering and spacing:
        # Give both columns equal weight so they expand equally, centering the entire element set.
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # You may need to adjust the width of the main window or the padx/pady 
        # to ensure the content doesn't collide with the frame edges.

        # --- Appearance Mode (Skin) Setting (Row 0) ---
        self.setup_setting_row(
            content_frame, 
            0, 
            "Appearance Mode (Skin):", 
            ["Light", "Dark", "System"], 
            self.change_appearance_mode_event
        )

        # --- Language Setting (Placeholder) (Row 1) ---
        self.setup_setting_row(
            content_frame, 
            1, 
            "Language:", 
            ["Romanian (Default)", "English", "Ucrainian"], 
            self.change_language_event
        )
        
        # --- Mascot Skin Setting (Placeholder) (Row 2) ---
        self.setup_setting_row(
            content_frame, 
            2, 
            "Mascot Skin:", 
            ["Default Bot", "Vibrant", "Monochrome", "8-bit"], # Example skins
            self.change_mascot_skin_event
        )

        # --- 2. Back Button (Bottom section) ---
        back_button = ctk.CTkButton(
            self,
            text="< Back to Home",
            command=self.controller.show_home,
            width=250, 
            height=50, 
            font=("Arial", 28, "bold") 
        )
        # Place back_button in the bottom row (row 1) and center it
        back_button.grid(row=1, column=0, pady=(10, 20))


    def setup_setting_row(self, parent_frame, row, label_text, options, command_func):
        # Label - Font size 28
        label = ctk.CTkLabel(parent_frame, text=label_text, font=("Arial", 28))
        # Anchored to the East of its column (column 0)
        label.grid(row=row, column=0, padx=20, pady=20, sticky="e") 
        
        # Option Menu - Font size 28
        option_menu = ctk.CTkOptionMenu(
            parent_frame,
            values=options,
            command=command_func,
            width=200,
            height=40,
            font=("Arial", 28) 
        )
        
        # Set current value for appearance mode
        if "Appearance Mode" in label_text:
            current_mode = ctk.get_appearance_mode().capitalize()
            option_menu.set(current_mode)
        else:
            option_menu.set(options[0]) # Default for other settings
            
        # Anchored to the West of its column (column 1)
        option_menu.grid(row=row, column=1, padx=20, pady=20, sticky="w") 

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_language_event(self, new_language: str):
        print(f"Language changed to: {new_language}. (Full translation logic not implemented)")
        
    # NEW METHOD: Mascot Skin Event Handler
    def change_mascot_skin_event(self, new_skin: str):
        print(f"Mascot skin changed to: {new_skin}. (Visual change not implemented)")
        
    def cleanup(self):
        pass