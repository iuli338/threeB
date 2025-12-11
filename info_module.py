# info_module.py

import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import textwrap

# --- Configuration (using constants from home_module for consistency) ---
TITLE_BLUE = "#4da6ff" 
ACCENT_COLOR = "#343638" # Slightly lighter gray for the content background
IMAGE_PATHS = [
    "burse.jpg",
    "cantine.jpg",
    "erasmus.jpg"
]
# Image size adjusted to fit the new, cleaner layout
IMAGE_SIZE = (320, 260) 

# Descriptions specific to UGAL (University 'Dunărea de Jos' of Galați)
INFO_SLIDES = [
    {
        "title": "Scholarship Success (Burse)",
        "description": "Unlock your potential! UGAL offers various merit scholarships for high achievers and social scholarships for financial support. Think smart, apply early! Check the faculty for deadlines and detailed criteria.",
        "color": "#77AADD"
    },
    {
        "title": "Your New Home: Student Dorms",
        "description": "Moving away? No stress! UGAL provides modern, comfortable housing close to campus. It's the perfect place to meet people and focus on your studies. Dorm assignments are competitive, so keep those grades up!",
        "color": "#A958F4"
    },
    {
        "title": "Eat Well, Learn Better: Cafeteria",
        "description": "Fuel your brain! The UGAL Cantină offers diverse, delicious, and highly subsidized meals—it's super affordable. Forget cooking—enjoy quick, balanced, and cheap lunches right on campus. Great food equals great studying!",
        "color": "#77FFF4"
    }
]


# Create dummy images for the info slides if they don't exist
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
            print(f"Creating placeholder image: {full_path}")
            img = Image.new('RGB', IMAGE_SIZE, slide["color"])
            draw = ImageDraw.Draw(img)
            
            # Center the title text on the placeholder image
            title_text = f"PLACEHOLDER:\n{slide['title']}"
            try:
                # Use a simplified approach for centering placeholder text
                text_w, text_h = draw.textsize(title_text, font=font_title)
            except AttributeError:
                text_w = 200 
                text_h = 40
                
            text_x = (IMAGE_SIZE[0] - text_w) // 2
            text_y = (IMAGE_SIZE[1] - text_h) // 2
            
            draw.text((text_x, text_y), title_text, fill=(0, 0, 0), font=font_title, align="center")
            img.save(full_path)

create_dummy_info_images()

class InfoView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        self.current_image_index = 0
        self.tk_images = []
        self._load_images()
        self.setup_ui()

    def _load_images(self):
        """Loads and prepares images for display."""
        for path_name in IMAGE_PATHS:
            full_path = os.path.join("images", path_name) 
            try:
                img = Image.open(full_path)
                img = img.resize(IMAGE_SIZE, Image.LANCZOS)
                self.tk_images.append(ImageTk.PhotoImage(img))
            except Exception as e:
                print(f"Error loading image {full_path}: {e}. Using fallback image.")
                dummy_img = Image.new('RGB', IMAGE_SIZE, "#FF0000")
                self.tk_images.append(ImageTk.PhotoImage(dummy_img))


    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 20))
        
        # Increased font size for impact
        ctk.CTkLabel(
            header_frame, text="DISCOVER UGAL: YOUR FUTURE", font=("Arial", 32, "bold"), text_color=TITLE_BLUE
        ).pack()

        # --- Main Content Frame (Styled background) ---
        self.content_frame = ctk.CTkFrame(self, fg_color=ACCENT_COLOR, corner_radius=15)
        self.content_frame.pack(pady=10, padx=40, fill='x', expand=False)
        
        # Column 0: Image (Left) - Uses inner padding for margin
        self.image_label = ctk.CTkLabel(self.content_frame, text="", image=None)
        self.image_label.grid(row=0, column=0, padx=(20, 15), pady=20, sticky="nsw") 

        # Column 1: Description (Right)
        # Bolder, larger title
        self.description_title_label = ctk.CTkLabel(
            self.content_frame, 
            text="", 
            font=("Arial", 24, "bold"), 
            justify=ctk.LEFT,
            wraplength=350,
            text_color=TITLE_BLUE
        )
        self.description_title_label.grid(row=0, column=1, padx=(15, 20), pady=(20, 5), sticky="nw")
        
        # Readable description text
        self.description_text_label = ctk.CTkLabel(
            self.content_frame, 
            text="", 
            font=("Arial", 16), 
            justify=ctk.LEFT,
            wraplength=350
        )
        self.description_text_label.grid(row=0, column=1, padx=(15, 20), pady=(50, 20), sticky="nw")

        # --- Navigation Buttons positioned below the content frame ---
        
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=(20, 10))

        # Previous Button - Wider and more prominent
        ctk.CTkButton(
            nav_frame,
            text="< PREVIOUS",
            command=self.show_previous_image,
            width=140,
            height=45,
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=30)

        # Slide Indicator Label
        self.indicator_label = ctk.CTkLabel(
            nav_frame, text=f"Slide 1 of {len(IMAGE_PATHS)}", font=("Arial", 18, "bold")
        )
        self.indicator_label.grid(row=0, column=1, padx=30)

        # Next Button - Wider and more prominent
        ctk.CTkButton(
            nav_frame,
            text="NEXT >",
            command=self.show_next_image,
            width=140,
            height=45,
            font=("Arial", 16, "bold")
        ).grid(row=0, column=2, padx=30)
        
        # Back Button (Bottom)
        ctk.CTkButton(
            self,
            text="< Back to Home",
            command=self.controller.show_home,
            width=220,
            height=45,
            font=("Arial", 18, "bold")
        ).pack(pady=(10, 20))
        
        # Initial display
        self.update_content()

    def update_content(self):
        """Updates the displayed image, title, description, and indicator."""
        index = self.current_image_index
        slide = INFO_SLIDES[index]
        
        # Update Image
        if self.tk_images:
            img = self.tk_images[index]
            self.image_label.configure(image=img)
            self.image_label.image = img 
            
        # Update Title and Description
        self.description_title_label.configure(text=slide["title"])
        self.description_text_label.configure(text=slide["description"])
            
        # Update Indicator
        self.indicator_label.configure(
            text=f"Slide {index + 1} of {len(IMAGE_PATHS)}"
        )

    def show_next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(IMAGE_PATHS)
        self.update_content()

    def show_previous_image(self):
        self.current_image_index = (self.current_image_index - 1) % len(IMAGE_PATHS)
        self.update_content()

    def cleanup(self):
        pass