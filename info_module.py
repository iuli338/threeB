# info_module.py

import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

# --- Configuration ---
# Colors
TITLE_BLUE = "#4da6ff" 
ACCENT_COLOR = "#2B2B2B" # Darker, modern card background
TEXT_COLOR = "#E0E0E0"   # Off-white for better readability
BG_COLOR = "#1a1a1a"     # Main background

# Image configuration
IMAGE_PATHS = [
    "burse.jpg",
    "cantine.jpg",
    "erasmus.jpg"
]

# Adjusted size to fit 480p height constraints better (4:3 ratio)
IMAGE_SIZE = (300, 225) 

# Descriptions
INFO_SLIDES = [
    {
        "title": "Scholarship Success",
        "description": "Unlock your potential! UGAL offers merit scholarships for high achievers and social support. Check the faculty for deadlines and criteria to secure your funding.",
        "color": "#77AADD"
    },
    {
        "title": "Student Dorms",
        "description": "Modern, comfortable housing close to campus. It's the perfect place to meet people and focus on studies. Assignments are competitive, so keep those grades up!",
        "color": "#A958F4"
    },
    {
        "title": "Campus Cafeteria",
        "description": "Fuel your brain! The UGAL Cantină offers diverse, delicious, and highly subsidized meals. Forget cooking—enjoy quick, balanced, and cheap lunches right on campus.",
        "color": "#77FFF4"
    }
]

# --- Dummy Image Generator ---
def create_dummy_info_images():
    if not os.path.exists("images"):
        os.makedirs("images")
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font_title = ImageFont.load_default()

    for i, slide in enumerate(INFO_SLIDES):
        path_name = IMAGE_PATHS[i]
        full_path = os.path.join("images", path_name)
        
        if not os.path.exists(full_path):
            img = Image.new('RGB', IMAGE_SIZE, slide["color"])
            draw = ImageDraw.Draw(img)
            title_text = f"{slide['title']}"
            
            # Simple centering logic
            w, h = IMAGE_SIZE
            # Using basic coordinate math instead of textsize/anchor for compatibility
            draw.text((20, h//2 - 10), title_text, fill=(0, 0, 0), font=font_title)
            img.save(full_path)

create_dummy_info_images()

class InfoView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent") # Transparent to use parent bg
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        self.current_image_index = 0
        self.tk_images = []
        self._load_images()
        self.setup_ui()

    def _load_images(self):
        """Loads and prepares images."""
        for path_name in IMAGE_PATHS:
            full_path = os.path.join("images", path_name) 
            try:
                img = Image.open(full_path)
                # Use Resampling.LANCZOS if available, else LANCZOS (older Pillow)
                try:
                    resample_filter = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_filter = Image.LANCZOS
                    
                img = img.resize(IMAGE_SIZE, resample_filter)
                self.tk_images.append(ImageTk.PhotoImage(img))
            except Exception as e:
                print(f"Error: {e}")
                dummy_img = Image.new('RGB', IMAGE_SIZE, "#555")
                self.tk_images.append(ImageTk.PhotoImage(dummy_img))

    def setup_ui(self):
        # Configure grid for the main frame to center content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Content
        self.grid_rowconfigure(2, weight=0) # Footer

        # --- 1. Header Area (Top Bar) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        
        # Back Button (Icon style)
        self.btn_back = ctk.CTkButton(
            header_frame, 
            text="← Back", 
            command=self.controller.show_home,
            width=80, 
            height=32,
            fg_color="#333",
            hover_color="#444",
            font=("Arial", 14)
        )
        self.btn_back.pack(side="left")

        # Page Title
        ctk.CTkLabel(
            header_frame, 
            text="DISCOVER UGAL", 
            font=("Arial", 24, "bold"), 
            text_color=TITLE_BLUE
        ).pack(side="left", padx=20)

        # --- 2. Main Content Card ---
        self.content_card = ctk.CTkFrame(self, fg_color=ACCENT_COLOR, corner_radius=15)
        self.content_card.grid(row=1, column=0, sticky="nsew", padx=40, pady=10)
        
        self.content_card.grid_columnconfigure(0, weight=0) # Image column fixed width
        self.content_card.grid_columnconfigure(1, weight=1) # Text column expands
        self.content_card.grid_rowconfigure(0, weight=1)

        # Image (Left)
        self.image_label = ctk.CTkLabel(self.content_card, text="", image=None)
        self.image_label.grid(row=0, column=0, padx=20, pady=20)

        # Text Container (Right)
        text_frame = ctk.CTkFrame(self.content_card, fg_color="transparent")
        text_frame.grid(row=0, column=1, sticky="nw", padx=(0, 20), pady=25)

        # Title
        self.slide_title = ctk.CTkLabel(
            text_frame, 
            text="", 
            font=("Arial", 26, "bold"), 
            justify="left",
            anchor="w",
            text_color=TITLE_BLUE
        )
        self.slide_title.pack(fill="x", pady=(0, 15)) # Increased pady for separation
        
        # Description
        self.slide_desc = ctk.CTkLabel(
            text_frame, 
            text="", 
            font=("Arial", 16), 
            justify="left",
            anchor="w",
            wraplength=380, # Hard limit to prevent expansion
            text_color=TEXT_COLOR
            # Removed 'line_spacing' as it causes errors in CTk
        )
        self.slide_desc.pack(fill="x")

        # --- 3. Footer Navigation (Compact) ---
        nav_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        nav_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 15))

        # Centering container for nav buttons
        nav_center = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_center.pack(anchor="center")

        # Prev Button
        ctk.CTkButton(
            nav_center,
            text="<",
            command=self.show_previous_image,
            width=50,
            height=40,
            font=("Arial", 20, "bold"),
            fg_color="#444",
            hover_color="#555"
        ).pack(side="left", padx=10)

        # Indicator
        self.indicator_label = ctk.CTkLabel(
            nav_center, 
            text="1 / 3", 
            font=("Arial", 16, "bold"),
            text_color="#888",
            width=80
        )
        self.indicator_label.pack(side="left", padx=10)

        # Next Button
        ctk.CTkButton(
            nav_center,
            text=">",
            command=self.show_next_image,
            width=50,
            height=40,
            font=("Arial", 20, "bold"),
            fg_color="#444",
            hover_color="#555"
        ).pack(side="left", padx=10)
        
        # Initialize
        self.update_content()

    def update_content(self):
        """Updates UI with current slide data."""
        index = self.current_image_index
        slide = INFO_SLIDES[index]
        
        # Update Image
        if self.tk_images:
            self.image_label.configure(image=self.tk_images[index])
            
        # Update Text
        self.slide_title.configure(text=slide["title"])
        self.slide_desc.configure(text=slide["description"])
            
        # Update Indicator
        self.indicator_label.configure(text=f"{index + 1} / {len(IMAGE_PATHS)}")

    def show_next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(IMAGE_PATHS)
        self.update_content()

    def show_previous_image(self):
        self.current_image_index = (self.current_image_index - 1) % len(IMAGE_PATHS)
        self.update_content()

    def cleanup(self):
        pass