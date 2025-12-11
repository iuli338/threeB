import customtkinter as ctk
from animation_module import AnimationView
from home_module import HomeView
from chat_module import ChatView

# Import camera shutdown function
from presence_detector import shutdown_camera

IS_FULLSCREEN = True

class MainController(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("3B Intelligent Interface")
        self.geometry("800x480")
        
        if IS_FULLSCREEN:
            self.overrideredirect(True)
            self.attributes("-fullscreen", True)
        self.resizable(False, False)
        
        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.current_view = None
        
        self.bind("<Escape>", self.close_app)
        
        # Start with Animation
        self.show_animation()
        
    def _switch_view(self, new_view_class):
        """Helper to handle switching views cleanly"""
        # 1. Cleanup existing view (pauses detection, but camera keeps running)
        if self.current_view:
            if hasattr(self.current_view, 'cleanup'):
                self.current_view.cleanup()
            self.current_view.destroy()
            
        # 2. Create new view (resumes detection if AnimationView)
        self.current_view = new_view_class(parent=self, controller=self)

    def show_animation(self):
        self._switch_view(AnimationView)
        
    def show_home(self):
        self._switch_view(HomeView)
        
    def show_chat(self):
        self._switch_view(ChatView)
        
    def close_app(self, event=None):
        print("Shutting down application...")
        
        # 1. Cleanup current view
        if self.current_view and hasattr(self.current_view, 'cleanup'):
            self.current_view.cleanup()
        
        # 2. Shutdown camera completely (only here, on app exit!)
        shutdown_camera()
        
        # 3. Destroy window
        self.destroy()

if __name__ == "__main__":
    app = MainController()
    app.mainloop()