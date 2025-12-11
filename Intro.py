import customtkinter as ctk
# Import the necessary modules for image handling
from PIL import Image

# Set the appearance mode for the entire application (e.g., "System", "Dark", "Light")
ctk.set_appearance_mode("Dark")
# Set the default color theme
ctk.set_default_color_theme("blue")

# --- Image Definitions (Placeholder Paths) ---
# IMPORTANT: Replace these with the actual file paths to your images.
IMAGE_PATHS = {
    "quiz": "image2.jpg",  # e.g., an icon for a test/question
    "info": "image1.jpg",  # e.g., an icon for information/details
    "chat": "image3.jpg",  # e.g., an icon for a message/chat bubble
}
# ADJUSTED BUTTON SIZE for 800px width (3 * 240px buttons + 4 * 10px padding = 760px total width)
BUTTON_DIMENSIONS = (240, 240) 
# The image will be scaled down from this size to fit the button
IMAGE_SIZE = (480, 480) 

# --- Constants for Hover Scaling Effect (ADJUSTED FOR NEW SIZE) ---
INITIAL_PADDING = 10
GROWTH_PADDING_DECREASE = 3 # Reduces padding by 3 on each side for a 6px total expansion
HOVER_PADDING = INITIAL_PADDING - GROWTH_PADDING_DECREASE # 10 - 3 = 7
# -------------------------------------------

class App(ctk.CTk):
    """
    The main application window (Root).
    """
    def __init__(self):
        super().__init__()

        # --- Configure the main window ---
        self.title("THREE B - Main Menu")
        # ADJUSTED GEOMETRY to 800x480
        self.geometry("800x480") 
        
        # Ensure columns have equal weight for symmetrical layout
        self.grid_columnconfigure((0, 1, 2), weight=1) 
        self.grid_rowconfigure(0, weight=1)
        
        # Keep track of the open Toplevel windows
        self.quiz_window = None
        self.info_window = None
        self.chat_window = None

        # --- Load and Prepare Images ---
        try:
            # Load images to fill the button space
            self.quiz_image = ctk.CTkImage(
                light_image=Image.open(IMAGE_PATHS["quiz"]),
                dark_image=Image.open(IMAGE_PATHS["quiz"]),
                size=IMAGE_SIZE
            )
            self.info_image = ctk.CTkImage(
                light_image=Image.open(IMAGE_PATHS["info"]),
                dark_image=Image.open(IMAGE_PATHS["info"]),
                size=IMAGE_SIZE
            )
            self.chat_image = ctk.CTkImage(
                light_image=Image.open(IMAGE_PATHS["chat"]),
                dark_image=Image.open(IMAGE_PATHS["chat"]),
                size=IMAGE_SIZE
            )
        except FileNotFoundError as e:
            print(f"ERROR: Image file not found: {e.filename}")
            print("Please ensure you have created placeholder image files (image2.jpg, image1.jpg, image3.jpg) in the script's directory, or updated the paths.")
            # Set images to None if they fail to load
            self.quiz_image = None
            self.info_image = None
            self.chat_image = None
            
        # --- Create the three image buttons using CTkLabel ---
        
        # NOTE: Text format is "TITLE\nDESCRIPTION"
        
        # 1. QUIZ Label/Button
        self.quiz_button = self._create_image_button(
            text="QUIZ\nGet Your Perfect Field",
            image_obj=self.quiz_image,
            command=self.open_quiz_window,
            column=0
        )

        # 2. INFO Label/Button
        self.info_button = self._create_image_button(
            text="INFO\nExplore What We Can Offer",
            image_obj=self.info_image,
            command=self.open_info_window,
            column=1
        )

        # 3. CHAT Label/Button
        self.chat_button = self._create_image_button(
            text="CHAT\nGet Intelligent Recommendation",
            image_obj=self.chat_image,
            command=self.open_chat_window,
            column=2
        )

    def _create_image_button(self, text, image_obj, command, column):
        """Helper function to create a clickable label with centered, divided text and hover effect."""
        
        # Split the input text into Title and Description
        try:
            title, description = text.split('\n', 1)
        except ValueError:
            title = text
            description = ""
        
        # 1. Main Label (Acts as the button background and contains the image)
        main_label = ctk.CTkLabel(
            self,
            text="", # Empty text for the main label
            image=image_obj,
            width=BUTTON_DIMENSIONS[0],
            height=BUTTON_DIMENSIONS[1],
            corner_radius=30
        )
        # Use INITIAL_PADDING constant
        main_label.grid(row=0, column=column, padx=INITIAL_PADDING, pady=INITIAL_PADDING, sticky="nsew")
        
        # --- Text Overlays ---
        
        # 2. Title Label (The bold, large part)
        title_label = ctk.CTkLabel(
            main_label, # Place the title INSIDE the main label
            text=title,
            font=ctk.CTkFont(size=36, weight="bold"), 
            text_color="white", 
            # KEY CHANGE: Set fg_color to None and removed padding/corner_radius
            fg_color=None, 
            corner_radius=0,
            padx=0,
            pady=0
        )
        # Position the title slightly above the vertical center
        title_label.place(relx=0.5, rely=0.45, anchor="s") 

        # 3. Description Label (The smaller, descriptive part)
        description_label = ctk.CTkLabel(
            main_label, # Place the description INSIDE the main label
            text=description,
            font=ctk.CTkFont(size=16),
            text_color="white", 
            # KEY CHANGE: Set fg_color to None and removed padding/corner_radius
            fg_color=None, 
            corner_radius=0,
            padx=0,
            pady=0
        )
        # Position the description slightly below the vertical center
        description_label.place(relx=0.5, rely=0.55, anchor="n") 
        
        # 4. Bind the click event to the main label
        main_label.bind("<Button-1>", lambda event: command())
        
        # 5. HOVER EFFECT IMPLEMENTATION 
        
        def on_enter(e):
            # 1. Apply color overlay
            main_label.configure(fg_color="#3498db") 
            # 2. Apply 'grow' effect by reducing padding
            main_label.grid_configure(padx=HOVER_PADDING, pady=HOVER_PADDING)
            
        def on_leave(e):
            # 1. Remove color overlay
            main_label.configure(fg_color="transparent") 
            # 2. Reset 'grow' effect by restoring padding
            main_label.grid_configure(padx=INITIAL_PADDING, pady=INITIAL_PADDING)

        # Bind hover events to all three widgets to ensure the effect works everywhere
        main_label.bind("<Enter>", on_enter)
        main_label.bind("<Leave>", on_leave)
        title_label.bind("<Enter>", on_enter) 
        title_label.bind("<Leave>", on_leave)
        description_label.bind("<Enter>", on_enter) 
        description_label.bind("<Leave>", on_leave)


        return main_label


    # --- Button Command Methods (No Changes) ---
    def open_quiz_window(self):
        """Opens the QUIZ Toplevel window."""
        if self.quiz_window is None or not self.quiz_window.winfo_exists():
            self.quiz_window = QuizWindow(self) 
        else:
            self.quiz_window.focus()

    def open_info_window(self):
        """Opens the INFO Toplevel window."""
        if self.info_window is None or not self.info_window.winfo_exists():
            self.info_window = InfoWindow(self) 
        else:
            self.info_window.focus()

    def open_chat_window(self):
        """Opens the CHAT Toplevel window."""
        if self.chat_window is None or not self.chat_window.winfo_exists():
            self.chat_window = ChatWindow(self)
        else:
            self.chat_window.focus()


class QuizWindow(ctk.CTkToplevel):
# ... (Toplevel window classes remain the same) ...
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("QUIZ Interface")
        self.geometry("400x300")
        self.transient(self.master) 
        label = ctk.CTkLabel(self, text="Welcome to the QUIZ Section!", font=ctk.CTkFont(size=18))
        label.pack(padx=20, pady=20)
        info = ctk.CTkLabel(self, text="Ready to find your perfect field?")
        info.pack(padx=20, pady=10)


class InfoWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("INFO Interface")
        self.geometry("400x300")
        self.transient(self.master) 
        label = ctk.CTkLabel(self, text="Welcome to the INFO Section!", font=ctk.CTkFont(size=18))
        label.pack(padx=20, pady=20)
        info = ctk.CTkLabel(self, text="Here you can explore all our offerings.")
        info.pack(padx=20, pady=10)


class ChatWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("CHAT Interface")
        self.geometry("400x300")
        self.transient(self.master) 
        label = ctk.CTkLabel(self, text="Welcome to the CHAT Section!", font=ctk.CTkFont(size=18))
        label.pack(padx=20, pady=20)
        info = ctk.CTkLabel(self, text="Get your intelligent recommendations here.")
        info.pack(padx=20, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()