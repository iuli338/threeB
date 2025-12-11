#!/usr/bin/env python3
"""
Presence Detector for Raspberry Pi 4 with Picamera2
Camera runs as a SINGLETON - never stops until app exits
Only face detection toggles on/off when switching views
"""

import time
import threading
import os
import atexit

import cv2
from picamera2 import MappedArray, Picamera2, Preview

# --- CONFIGURATION ---
FACE_AREA_THRESHOLD = 0.20
TIME_TO_TRIGGER = 1.0
PREVIEW_SIZE = (640, 480)
DETECT_SIZE = (320, 240)

CASCADE_PATHS = [
    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
    "/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml",
    "haarcascade_frontalface_default.xml",
]


class CameraSingleton:
    """
    Singleton camera manager - camera is initialized ONCE and stays running.
    This prevents the 'Device busy' error when switching views.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.picam2 = None
        self.running = False
        self.w0 = self.h0 = 0
        self.w1 = self.h1 = 0
        self.stride = 0
        self._initialized = True
        
        # Register cleanup on program exit
        atexit.register(self.shutdown)
    
    def start(self):
        """Start camera (only once for entire app lifetime)"""
        if self.running:
            print("Camera already running")
            return True
            
        print("Starting camera singleton...")
        try:
            self.picam2 = Picamera2()
            
            config = self.picam2.create_preview_configuration(
                main={"size": PREVIEW_SIZE, "format": "XRGB8888"},
                lores={"size": DETECT_SIZE, "format": "YUV420"},
                buffer_count=4
            )
            self.picam2.configure(config)
            
            self.w0, self.h0 = self.picam2.stream_configuration("main")["size"]
            self.w1, self.h1 = self.picam2.stream_configuration("lores")["size"]
            self.stride = self.picam2.stream_configuration("lores")["stride"]
            
            print(f"Preview: {self.w0}x{self.h0}, Detection: {self.w1}x{self.h1}")
            
            self.picam2.start_preview(Preview.QTGL)
            self.picam2.start()
            
            self.running = True
            print("Camera started successfully!")
            return True
            
        except Exception as e:
            print(f"Camera start error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_detection_frame(self):
        """Get grayscale frame for face detection"""
        if not self.running or not self.picam2:
            return None
        try:
            buffer = self.picam2.capture_buffer("lores")
            grey = buffer[:self.stride * self.h1].reshape((self.h1, self.stride))
            return grey[:, :self.w1].copy()
        except:
            return None
    
    def set_overlay_callback(self, callback):
        """Set the drawing callback"""
        if self.picam2:
            self.picam2.post_callback = callback
    
    def clear_overlay_callback(self):
        """Remove drawing callback"""
        if self.picam2:
            self.picam2.post_callback = None
    
    def shutdown(self):
        """Full shutdown - only call on app exit"""
        if not self.running:
            return
        print("Shutting down camera...")
        self.running = False
        if self.picam2:
            try:
                self.picam2.stop_preview()
                self.picam2.stop()
                self.picam2.close()
            except:
                pass
            self.picam2 = None
        print("Camera shutdown complete")


# Global camera instance
_camera = None

def get_camera():
    """Get the singleton camera instance"""
    global _camera
    if _camera is None:
        _camera = CameraSingleton()
    return _camera


class PresenceDetector:
    """
    Face presence detector - uses the singleton camera.
    Can be started/stopped multiple times without affecting camera.
    """
    def __init__(self, on_detect_callback=None):
        self.on_detect_callback = on_detect_callback
        self.face_detector = None
        self.detection_active = False
        self.detection_thread = None
        
        # Detection state
        self.faces = []
        self.start_look_time = None
        self.action_triggered = False
        
        # Get camera singleton
        self.camera = get_camera()
        
        self._load_cascade()
    
    def _load_cascade(self):
        for path in CASCADE_PATHS:
            if os.path.exists(path):
                self.face_detector = cv2.CascadeClassifier(path)
                if not self.face_detector.empty():
                    print(f"Loaded cascade: {path}")
                    return True
        print("ERROR: Could not load face cascade!")
        return False
    
    def _draw_overlay(self, request):
        """Draw face boxes on preview"""
        if not self.detection_active:
            return
            
        with MappedArray(request, "main") as m:
            frame = m.array
            
            for (x, y, w, h) in self.faces:
                x_s = x * self.camera.w0 // self.camera.w1
                y_s = y * self.camera.h0 // self.camera.h1
                w_s = w * self.camera.w0 // self.camera.w1
                h_s = h * self.camera.h0 // self.camera.h1
                
                face_area = w * h
                total_area = self.camera.w1 * self.camera.h1
                ratio = face_area / total_area
                
                color = (0, 255, 0, 255) if ratio >= FACE_AREA_THRESHOLD else (0, 255, 255, 255)
                cv2.rectangle(frame, (x_s, y_s), (x_s + w_s, y_s + h_s), color, 2)
                cv2.putText(frame, f"{ratio:.0%}", (x_s, y_s - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Status indicator
            if self.action_triggered:
                cv2.circle(frame, (30, 30), 20, (0, 0, 255, 255), -1)
            elif self.start_look_time:
                cv2.circle(frame, (30, 30), 20, (0, 255, 255, 255), 2)
            else:
                cv2.circle(frame, (30, 30), 20, (0, 255, 0, 255), 2)
    
    def _process_detection(self, grey_frame):
        if not self.detection_active or self.face_detector is None:
            return
        
        self.faces = self.face_detector.detectMultiScale(grey_frame, 1.1, 5)
        
        face_found_close = False
        total_area = self.camera.w1 * self.camera.h1
        
        for (x, y, w, h) in self.faces:
            if (w * h) / total_area >= FACE_AREA_THRESHOLD:
                face_found_close = True
                break
        
        if face_found_close:
            if self.start_look_time is None:
                self.start_look_time = time.time()
            
            if time.time() - self.start_look_time >= TIME_TO_TRIGGER:
                if not self.action_triggered:
                    print(">> PRESENCE CONFIRMED!")
                    if self.on_detect_callback:
                        try:
                            self.on_detect_callback()
                        except Exception as e:
                            print(f"Callback error: {e}")
                    self.action_triggered = True
        else:
            self.start_look_time = None
            self.action_triggered = False
    
    def _detection_loop(self):
        """Detection loop - runs in background thread"""
        print("Detection loop started")
        while self.detection_active:
            try:
                grey = self.camera.get_detection_frame()
                if grey is not None:
                    self._process_detection(grey)
                time.sleep(0.033)  # ~30fps
            except Exception as e:
                time.sleep(0.1)
        print("Detection loop stopped")
    
    def start(self):
        """Start detection (camera must already be running)"""
        if self.detection_active:
            print("Detection already active")
            return
        
        # Ensure camera is running
        if not self.camera.running:
            if not self.camera.start():
                print("Failed to start camera")
                return
        
        # Reset state
        self.faces = []
        self.start_look_time = None
        self.action_triggered = False
        self.detection_active = True
        
        # Set overlay callback
        self.camera.set_overlay_callback(self._draw_overlay)
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        print("Detection started")
    
    def stop(self):
        """Stop detection (camera keeps running!)"""
        if not self.detection_active:
            return
            
        print("Stopping detection...")
        self.detection_active = False
        self.faces = []
        
        # Clear overlay but DON'T stop camera
        self.camera.clear_overlay_callback()
        
        # Wait for thread to finish
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=0.5)
        
        print("Detection stopped (camera still running)")
    
    def pause(self):
        """Alias for stop - clearer intent"""
        self.stop()
    
    def resume(self):
        """Alias for start - clearer intent"""
        self.start()


def shutdown_camera():
    """Call this only when the entire app is closing"""
    global _camera
    if _camera:
        _camera.shutdown()