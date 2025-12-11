import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time
import random
from dataclasses import dataclass
from typing import List
from enum import Enum

# --- CONSTANTE ȘI STRUCTURI DE DATE ---
SLEEP_IN_SECONDS = 60

@dataclass
class AnimationFrame:
    image_path: str
    duration_ms: int

@dataclass
class Animation:
    frames: List[AnimationFrame]
    is_loop: bool

class State(Enum):
    SLEEPING = "sleeping"
    LOOKING_AROUND_SLEEP = "looking_around_sleep"
    LOOKING_AROUND = "looking_around"
    NORMAL = "normal"
    CLICK_ME = "click_me"
    WINKING = "winking"

# Define animations
ANIMATIONS = {
    State.NORMAL: Animation(
        frames=[    
            AnimationFrame("faces/smile.png", 2000),
            AnimationFrame("faces/closed_eyes.png", 100),
            AnimationFrame("faces/smile.png", 0),
        ], is_loop=True
    ),
    State.SLEEPING: Animation(
        frames=[
            AnimationFrame("faces/sleep1.png", 1000),
            AnimationFrame("faces/sleep2.png", 1000),
            AnimationFrame("faces/sleep1.png", 0),
        ], is_loop=True
    ),
    State.LOOKING_AROUND_SLEEP: Animation(
        frames=[
            AnimationFrame("faces/sleep_look_right2.png", 1000),
            AnimationFrame("faces/sleep_look_right1.png", 250),
            AnimationFrame("faces/sleep_look_front.png", 250),
            AnimationFrame("faces/sleep_look_left1.png", 250),
            AnimationFrame("faces/sleep_look_left2.png", 1000),
            AnimationFrame("faces/sleep_look_left1.png", 250),
            AnimationFrame("faces/sleep_look_front.png", 250),
            AnimationFrame("faces/sleep_look_right1.png", 250),
            AnimationFrame("faces/sleep_look_right2.png", 1000)
        ], is_loop=False
    ),
    State.LOOKING_AROUND: Animation(
        frames=[
            AnimationFrame("faces/look_right1.png", 250),
            AnimationFrame("faces/look_right2.png", 1000),
            AnimationFrame("faces/look_right1.png", 250),
            AnimationFrame("faces/smile.png", 250),
            AnimationFrame("faces/look_left1.png", 250),
            AnimationFrame("faces/look_left2.png", 1000),
            AnimationFrame("faces/look_left1.png", 250),
            AnimationFrame("faces/smile.png", 250),
            AnimationFrame("faces/look_right1.png", 250),
            AnimationFrame("faces/look_right2.png", 1000),
            AnimationFrame("faces/look_right1.png", 250)
        ], is_loop=False
    ),
    State.CLICK_ME: Animation(
        frames=[
            AnimationFrame("faces/here1.png", 400),
            AnimationFrame("faces/here2.png", 400),
            AnimationFrame("faces/here1.png", 0),
        ], is_loop=True
    ),
    State.WINKING: Animation(
        frames=[
            AnimationFrame("faces/wink.png", 1000),
            AnimationFrame("faces/smile.png", 1000),
        ], is_loop=False
    ),
}

class Character:
    def __init__(self, app_view):
        self.app = app_view
        self.current_state = State.SLEEPING
        self.current_frame = 0
        self.is_awake = False
        self.normal_timer = 0
        self.running = True
        self.image_cache = {}
        self.force_restart = False
        
    def load_image(self, path):
        if path not in self.image_cache:
            try:
                pil_image = Image.open(path)
                pil_image = pil_image.resize((800, 480), Image.Resampling.LANCZOS)
                self.image_cache[path] = ImageTk.PhotoImage(pil_image)
            except Exception as e:
                # print(f"Error loading image {path}: {e}")
                return None
        return self.image_cache[path]
        
    def run_animation(self):
        """Main animation loop - Thread Safe"""
        while self.running:
            try:
                if self.force_restart:
                    self.force_restart = False
                    self.current_frame = 0
                
                animation = ANIMATIONS[self.current_state]
                
                # Safety check
                if self.current_frame >= len(animation.frames):
                    self.current_frame = 0
                    
                frame = animation.frames[self.current_frame]
                
                # Încărcare imagine (operație grea, ok în thread)
                tk_image = self.load_image(frame.image_path)
                
                # Actualizare GUI (DOAR pe main thread prin after)
                if tk_image:
                    if hasattr(self.app, 'winfo_exists') and self.app.winfo_exists():
                        self.app.after(0, lambda img=tk_image: self._safe_gui_update(img))
                    else:
                        break

                if frame.duration_ms > 0:
                    time.sleep(frame.duration_ms / 1000.0)
                
                self.current_frame += 1
                if self.current_frame >= len(animation.frames):
                    if animation.is_loop:
                        self.current_frame = 0
                    else:
                        self.on_animation_complete()
                        
            except Exception as e:
                print(f"Animation Error: {e}")
                time.sleep(0.1)

    def _safe_gui_update(self, img):
        try:
            if hasattr(self.app, 'image_label') and self.app.image_label.winfo_exists():
                self.app.image_label.configure(image=img)
                self.app.image_label.image = img
        except Exception:
            pass

    def on_animation_complete(self):
        """Called when a non-looping animation completes"""
        if self.current_state == State.LOOKING_AROUND_SLEEP:
            self.change_state(State.SLEEPING)
            
        elif self.current_state == State.LOOKING_AROUND:
            self.change_state(State.NORMAL)

        elif self.current_state == State.WINKING:
            # --- MODIFICARE AICI ---
            # Când termină de făcut cu ochiul, navigăm la Home
            print("Wink finished. Going to Home.")
            if hasattr(self.app, 'navigate_to_home'):
                # Folosim .after pentru a fi siguri că rulăm pe main thread
                self.app.after(0, self.app.navigate_to_home)
            else:
                self.change_state(State.NORMAL)
    
    def change_state(self, new_state: State):
        self.current_state = new_state
        self.current_frame = 0
        self.force_restart = True
        
    def behavior_loop(self):
        while self.running:
            time.sleep(1)
            if self.current_state == State.NORMAL:
                if random.random() < 0.05:
                    self.change_state(State.LOOKING_AROUND)
                self.normal_timer += 1
                if self.normal_timer >= SLEEP_IN_SECONDS:
                    self.change_state(State.SLEEPING)
                    self.normal_timer = 0
                    self.is_awake = False
            elif self.current_state == State.SLEEPING and not self.is_awake:
                if random.random() < 0.05:
                    self.change_state(State.LOOKING_AROUND_SLEEP)
                
    def wake_up(self):
        if not self.is_awake:
            self.is_awake = True
            self.change_state(State.CLICK_ME)
    
    def on_click(self):
        if self.current_state == State.CLICK_ME:
            self.change_state(State.NORMAL)
            self.normal_timer = 0
        elif self.current_state == State.NORMAL:
            # Click -> Wink -> (apoi on_animation_complete va schimba pagina)
            self.change_state(State.WINKING)
            
    def stop(self):
        self.running = False

class AnimationView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.pack(fill="both", expand=True)
        
        self.character = Character(self)
        
        self.image_label = ctk.CTkLabel(self, text="", width=800, height=480)
        self.image_label.place(x=0, y=0)
        
        # BINDINGS
        self.image_label.bind("<Button-1>", self.on_image_click)
        
        # Optional: Păstrăm și double click dacă vrei navigare instantanee
        self.image_label.bind("<Double-Button-1>", self.on_double_click)
        
        self.animation_thread = threading.Thread(target=self.character.run_animation, daemon=True)
        self.behavior_thread = threading.Thread(target=self.character.behavior_loop, daemon=True)
        self.animation_thread.start()
        self.behavior_thread.start()
        
        self.controller.bind("<space>", self.on_space_key)

    def on_image_click(self, event):
        self.character.on_click()
    
    def on_double_click(self, event):
        if self.character.current_state == State.NORMAL:
            self.navigate_to_home()
            
    def navigate_to_home(self):
        """Helper method called by Character class"""
        self.controller.show_home()
    
    def on_space_key(self, event):
        self.character.wake_up()

    def cleanup(self):
        self.character.stop()
        self.controller.unbind("<space>")