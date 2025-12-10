import customtkinter as ctk
from PIL import Image
import os 
from itertools import cycle

# --- Configuration ---
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
IMAGE_SIZE = (200, 200) 

# File names for your GIF faces
STATUS_IMAGES = [
    "Creating_A_Changing_Expression_Video.gif", # Index 0: New Image 1
    "Generating_Blinking_Face_Video.gif",       # Index 1: New Image 2
    "Generating_AFK_Sleepy_Face_Video-ezgif.com-video-to-gif-converter.gif"        # Index 2: Repeat of New Image 2
]

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GIFPlayerLabel(ctk.CTkLabel):
    """A CustomTkinter Label that handles loading and animating a GIF."""

    def __init__(self, master, image_path, size):
        # Initialize the CTkLabel
        super().__init__(master, text="", image=None, width=size[0], height=size[1])
        
        self.image_path = image_path
        self.size = size
        self.frames = []      # Stores CTkImage objects for all frames
        self.delay = 0        # Stores the delay (in ms) between frames
        self.frame_iterator = None # Iterator to cycle through frames
        self.animation_job = None # Stores the ID of the self.after job
        
        # 1. Load the GIF frames
        self._load_frames()
        
        # 2. Start the animation if frames exist
        # We start the animation only when the player is gridded/displayed
        # self.start_animation() # Commented out, the App class will handle starting it later
        
        if not self.frames:
            print(f"Warning: Could not load frames for {self.image_path}. Displaying placeholder.")
            # Set a gray placeholder if loading failed
            placeholder_img = ctk.CTkImage(Image.new('RGB', self.size, color='gray'), size=self.size)
            self.configure(image=placeholder_img)


    def _load_frames(self):
        """Loads all frames from the GIF file."""
        try:
            gif_img = Image.open(self.image_path)
            
            # Use the duration of the first frame as the delay for the whole animation
            # PIL stores the duration in milliseconds
            self.delay = gif_img.info.get('duration', 100) 

            while True:
                # Resize the frame
                frame = gif_img.copy().resize(self.size, Image.Resampling.LANCZOS)
                
                # Convert to CTkImage
                ctk_frame = ctk.CTkImage(light_image=frame, dark_image=frame, size=self.size)
                self.frames.append(ctk_frame)
                
                # Move to the next frame
                gif_img.seek(gif_img.tell() + 1)
        except EOFError:
            # End of file, we've loaded all frames
            pass
        except Exception as e:
            print(f"Error reading GIF frames for {self.image_path}: {e}")
            self.frames = [] # Clear list if an error occurred


    def start_animation(self):
        """Starts the animation loop."""
        if not self.frames:
            return

        if self.animation_job:
            self.stop_animation()
        
        # Reset iterator and set the first frame before starting the loop
        self.frame_iterator = cycle(self.frames)
        self._update_frame()


    def stop_animation(self):
        """Stops the animation loop."""
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None


    def _update_frame(self):
        """Displays the next frame and schedules itself to run again."""
        if self.frames and self.frame_iterator:
            # Get the next frame from the infinite cycle
            next_frame = next(self.frame_iterator)
            self.configure(image=next_frame)
            
            # Schedule the next call after the frame delay
            self.animation_job = self.after(self.delay, self._update_frame)


class ImageCyclerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Animated GIF Cycler")
        self.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.current_image_index = 0
        
        # --- Layout Setup ---
        self.grid_rowconfigure(0, weight=1)    # Image area
        self.grid_rowconfigure(1, weight=0)    # Button area
        self.grid_columnconfigure(0, weight=1) # Center content

        # 🔑 FIX: 1. CREATE Content Frame FIRST
        # --- Content Frame (holds the dynamically placed GIFPlayerLabel) ---
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # 🔑 FIX: 2. THEN Load GIF Players using the newly created frame
        # --- Load Image Player Objects ---
        self.gif_players = []
        self._load_gif_players() 
        
        # Start with the first player displayed
        self.active_player = self.gif_players[0] if self.gif_players else None
        if self.active_player:
            self.active_player.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)


        # --- Navigation Frame (holds the buttons) ---
        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.nav_frame.grid_columnconfigure(0, weight=1)
        self.nav_frame.grid_columnconfigure(1, weight=1)

        # --- Navigation Buttons ---
        ctk.CTkButton(self.nav_frame, text="< Previous", command=lambda: self._cycle_image(-1)).grid(
            row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(self.nav_frame, text="Next >", command=lambda: self._cycle_image(1)).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")

        # Initial display setup
        self._update_display()


    def _load_gif_players(self):
        """Initializes GIFPlayerLabel objects for each path."""
        script_dir = os.path.dirname(os.path.abspath(__file__))

        for filename in STATUS_IMAGES:
            image_path = os.path.join(script_dir, filename)
            
            if not os.path.exists(image_path):
                print(f"Error: Image file NOT found at: {image_path}. Skipping.")
                continue
            
            # Create a new GIFPlayerLabel instance for the GIF, using the now-existing self.content_frame
            player = GIFPlayerLabel(self.content_frame, image_path, IMAGE_SIZE)
            self.gif_players.append(player)

        if not self.gif_players:
            print("CRITICAL ERROR: No images were loaded.")


    def _cycle_image(self, direction):
        """Changes the current image index and updates the display."""
        if not self.gif_players:
            return 

        # 1. Stop the current animation
        if self.active_player:
            self.active_player.stop_animation()

        num_images = len(self.gif_players)
        
        # Calculate the new index, wrapping around
        new_index = (self.current_image_index + direction) % num_images
        self.current_image_index = new_index
        
        # Update the display
        self._update_display()


    def _update_display(self):
        """Updates the active GIFPlayerLabel and starts its animation."""
        if not self.gif_players:
            return
            
        # Hide the previous player
        if self.active_player:
            self.active_player.grid_forget()

        # Set the new active player
        self.active_player = self.gif_players[self.current_image_index]
        
        # Display the new player and start its animation
        self.active_player.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.active_player.start_animation() 

        print(f"Displaying GIF index: {self.current_image_index} ({STATUS_IMAGES[self.current_image_index]})")


if __name__ == "__main__":
    app = ImageCyclerApp()
    app.mainloop()