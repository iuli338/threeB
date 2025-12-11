import customtkinter as ctk

class TouchKeyboard(ctk.CTkFrame):
    def __init__(self, master, entry_widget, on_submit, on_close, **kwargs):
        super().__init__(master, fg_color="#101010", corner_radius=0, **kwargs)
        self.entry = entry_widget
        self.on_submit = on_submit
        self.on_close = on_close
        
        # Layout tastatură
        self.keys = [
            ['1','2','3','4','5','6','7','8','9','0',"✕"], 
            ['q','w','e','r','t','y','u','i','o','p'], 
            ['a','s','d','f','g','h','j','k','l'], 
            ['z','x','c','v','b','n','m','⌫'], 
            ['SPAȚIU', 'TRIMITE']
        ]
        self.setup_keys()

    def setup_keys(self):
        keys_container = ctk.CTkFrame(self, fg_color="transparent")
        keys_container.pack(expand=True, fill="both", padx=5, pady=5)
        
        for row in self.keys:
            row_frame = ctk.CTkFrame(keys_container, fg_color="transparent")
            row_frame.pack(pady=2, expand=True)
            for key in row:
                # Dimensiuni și culori standard
                w, h = 55, 40
                fg = "#333"
                cmd = lambda k=key: self.press_key(k)
                
                # Taste speciale
                if key == '⌫': 
                    w, fg = 70, "#8B0000"
                elif key == 'SPAȚIU': 
                    w = 300
                elif key == 'TRIMITE': 
                    w, fg, cmd = 100, "#1b5e20", self.press_submit
                elif key == "✕": 
                    w, cmd = 50, self.press_close
                
                ctk.CTkButton(
                    row_frame, 
                    text=key.upper(), 
                    width=w, 
                    height=h, 
                    corner_radius=8, 
                    fg_color=fg, 
                    text_color="white", 
                    font=("Arial", 14, "bold"), 
                    command=cmd
                ).pack(side="left", padx=2)

    def press_key(self, k):
        if k == '⌫': 
            self.entry.delete(len(self.entry.get())-1, "end")
        elif k == 'SPAȚIU': 
            self.entry.insert("end", " ")
        else: 
            self.entry.insert("end", k)

    def press_submit(self): 
        # Aceasta va apela send_message din ChatView
        self.on_submit()

    def press_close(self): 
        self.on_close() 
        self.place_forget()

    def show(self): 
        self.place(relx=0.5, rely=1.0, anchor="s", relwidth=1.0, relheight=0.5)
        self.tkraise()