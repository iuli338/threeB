from gtts import gTTS
import pygame
import os
import threading
import time

class TTSManager:
    def __init__(self):
        try:
            pygame.mixer.init()
        except:
            print("Eroare audio mixer")

        self.stop_event = threading.Event()
        self.current_lang = 'ro' # Default

    def set_language(self, lang_code):
        """Setează limba pentru pronunție: 'ro', 'en', 'ru'"""
        self.current_lang = lang_code

    def speak(self, text):
        """Generează și redă audio"""
        # Oprim orice rulează acum
        self.stop()
        
        thread = threading.Thread(target=self._speak_thread, args=(text,), daemon=True)
        thread.start()

    def _speak_thread(self, text):
        self.stop_event.clear()
        try:
            # Generăm audio cu limba selectată
            tts = gTTS(text=text, lang=self.current_lang, slow=False)
            filename = "temp_audio.mp3"
            tts.save(filename)
            
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Loop care ține thread-ul viu cât timp cântă
            while pygame.mixer.music.get_busy() or self.is_paused():
                if self.stop_event.is_set():
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Eroare TTS: {e}")

    def pause(self):
        """Pune pauză la redare"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def unpause(self):
        """Reia redarea de unde a rămas"""
        pygame.mixer.music.unpause()

    def stop(self):
        """Oprește complet"""
        self.stop_event.set()
        pygame.mixer.music.stop()
        
    def is_paused(self):
        # Pygame nu are o funcție directă "is_paused", dar putem deduce
        # Pentru simplitate, ne bazăm pe logică externă sau doar pe unpause
        return False