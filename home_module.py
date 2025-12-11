# home_module.py

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os
import time

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
BG_COLOR = "#2b2b2b"
TITLE_BLUE = "#4da6ff"
BTN_WIDTH = 230
BTN_HEIGHT = 350

def create_dummy_images_if_missing():
    if not os.path.exists("images"):
        os.makedirs("images")
    dummies = [
        ("images/quiz_bg.jpg", (20, 30, 60)),
        ("images/info_bg.jpg", (80, 70, 60)),
        ("images/chat_bg.jpg", (60, 20, 100))
    ]
    for path, color in dummies:
        if not os.path.exists(path):
            img = Image.new('RGB', (BTN_WIDTH, BTN_HEIGHT), color)
            draw = ImageDraw.Draw(img)
            draw.rectangle([5, 5, BTN_WIDTH-5, BTN_HEIGHT-5], outline=color, width=3)
            img.save(path)

create_dummy_images_if_missing()

class HomeView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.last_interaction = time.time()
        self.inactivity_limit = 20  # Seconds
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=20)

        self.setup_header()
        self.setup_buttons()
        # NEW: Setup the settings button
        self.setup_settings_button()

        self.check_inactivity()
        
        # Bind events for inactivity reset
        self.controller.bind_all("<Motion>", self.reset_timer)
        self.controller.bind_all("<Button-1>", self.reset_timer)
        self.controller.bind_all("<Key>", self.reset_timer)

    def setup_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(pady=(0, 20))
        title_label = ctk.CTkLabel(
            header_frame, text="THREEB ⚙", font=("Arial", 28, "bold"), text_color=TITLE_BLUE
        )
        title_label.pack()

    # NEW METHOD: Settings Button setup
    def setup_settings_button(self):
        settings_button = ctk.CTkButton(
            self,
            text="Settings",
            command=self.show_settings, # Calls the new navigation method
            width=80,
            height=25
        )
        # Position in the top-right corner
        settings_button.place(relx=1.0, rely=0.0, x=-20, y=20, anchor=tk.NE)

    # NEW METHOD: Show Settings View
    def show_settings(self):
        self.reset_timer(None)
        self.controller.show_settings() # Switch the full view via controller

    def setup_buttons(self):
        grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        grid_frame.pack()
        self.create_image_card(grid_frame, 0, "images/quiz_bg.jpg", "QUIZ", "GET YOUR\nPERFECT FIELD")
        self.create_image_card(grid_frame, 1, "images/info_bg.jpg", "INFO", "EXPLORE WHAT WE\nCAN OFFER")
        self.create_image_card(grid_frame, 2, "images/chat_bg.jpg", "CHAT", "GET INTELLIGENT\nRECOMMENDATION")

    def create_image_card(self, parent, col, img_path, title, subtitle):
        canvas = tk.Canvas(parent, width=BTN_WIDTH, height=BTN_HEIGHT, bg=BG_COLOR, highlightthickness=0)
        canvas.grid(row=0, column=col, padx=15)

        try:
            pil_img = Image.open(img_path)
            pil_img = self.round_corners(pil_img, radius=30)
            tk_img = ImageTk.PhotoImage(pil_img)
            canvas.image = tk_img 
            canvas.create_image(BTN_WIDTH//2, BTN_HEIGHT//2, image=tk_img)
        except Exception:
            canvas.create_rectangle(0,0, BTN_WIDTH, BTN_HEIGHT, fill="#333333")

        canvas.create_text(BTN_WIDTH//2, BTN_HEIGHT//2 - 20, text=title, font=("Arial", 36, "bold"), fill="white", tags="content")
        canvas.create_text(BTN_WIDTH//2, BTN_HEIGHT//2 + 40, text=subtitle, font=("Arial", 11, "bold"), fill="white", justify="center", tags="content")

        def on_enter(e):
            canvas.config(cursor="hand2")
            if not canvas.find_withtag("hover_border"):
                canvas.create_rectangle(2,2, BTN_WIDTH-2, BTN_HEIGHT-2, outline="white", width=3, tags="hover_border")

        def on_leave(e):
            canvas.config(cursor="")
            canvas.delete("hover_border")

        def on_click(e):
            print(f"Clicked on {title}")
            self.reset_timer(None)
            
            # --- NAVIGATION LOGIC ---
            if title == "CHAT":
                self.controller.show_chat()
            elif title == "QUIZ":
                print("Quiz coming soon...")
            elif title == "INFO":
                print("Info coming soon...")

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<Button-1>", on_click)

    def round_corners(self, im, radius):
        im = im.resize((BTN_WIDTH, BTN_HEIGHT), Image.LANCZOS)
        circle = Image.new('L', (radius * 2, radius * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
        alpha = Image.new('L', im.size, 255)
        w, h = im.size
        alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
        im.putalpha(alpha)
        return im

    def reset_timer(self, event):
        self.last_interaction = time.time()

    def check_inactivity(self):
        if not self.winfo_exists(): return
        
        elapsed = time.time() - self.last_interaction
        if elapsed > self.inactivity_limit:
            print("Inactivity. Returning to animation.")
            self.controller.show_animation()
            return
        self.after(1000, self.check_inactivity)
            
    def cleanup(self):
        self.controller.unbind_all("<Motion>")
        self.controller.unbind_all("<Button-1>")
        self.controller.unbind_all("<Key>")