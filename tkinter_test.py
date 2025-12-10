import customtkinter as ctk

# --- Configurare Inițială ---
# Modul de aspect: "System" (respectă setarea OS-ului), "Dark", sau "Light"
ctk.set_appearance_mode("System")  
# Tema de culoare: "blue" (standard), "green", "dark-blue"
ctk.set_default_color_theme("dark-blue")  

class HelloWorldApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurare fereastră principală
        self.title("Hello World - CustomTkinter")
        self.geometry("500x350")
        
        # Centrare fereastră pe ecran (opțional, dar arată bine)
        # (Aici e doar geometria, centrarea reală depinde de OS, dar dimensiunea e fixă)
        
        # Creăm un Grid Layout pentru a centra totul frumos
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Crearea unui "Card" (Frame) central ---
        # Frame-ul va conține toate elementele și le va grupa vizual
        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Configurăm grid-ul din interiorul frame-ului
        self.main_frame.grid_columnconfigure(0, weight=1)

        # --- Titlu (Label) ---
        self.label_title = ctk.CTkLabel(
            self.main_frame, 
            text="Hello, World! 👋", 
            font=("Roboto Medium", 24)
        )
        self.label_title.grid(row=0, column=0, padx=20, pady=(40, 10))

        # --- Subtitlu (Label) ---
        self.label_subtitle = ctk.CTkLabel(
            self.main_frame, 
            text="Bine ai venit în CustomTkinter", 
            font=("Roboto", 14),
            text_color="gray70" # Culoare mai ștearsă pentru subtitlu
        )
        self.label_subtitle.grid(row=1, column=0, padx=20, pady=(0, 30))

        # --- Buton Interactiv ---
        self.btn_action = ctk.CTkButton(
            self.main_frame, 
            text="Schimbă Modul (Dark/Light)", 
            command=self.change_mode,
            height=40,
            corner_radius=10,
            font=("Roboto Bold", 14)
        )
        self.btn_action.grid(row=2, column=0, padx=20, pady=20)

    def change_mode(self):
        """Funcție care schimbă tema aplicației când apeși butonul"""
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Light":
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

if __name__ == "__main__":
    app = HelloWorldApp()
    app.mainloop()