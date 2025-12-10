from gtts import gTTS
import pygame
import os
import threading
import time

class TTSManager:
    def __init__(self):
        # Inițializăm mixerul audio
        try:
            pygame.mixer.init()
        except:
            print("Eroare la inițializare audio (poate lipsesc drivere)")

        self.is_speaking = False
        self.stop_event = threading.Event()

    def speak(self, text):
        """Rulează procesul de vorbire într-un thread separat"""
        # Dacă vorbește deja, îl oprim pe cel vechi (opțional)
        if self.is_speaking:
            self.stop()
        
        # Pornim un nou thread
        thread = threading.Thread(target=self._speak_thread, args=(text,), daemon=True)
        thread.start()

    def _speak_thread(self, text):
        self.is_speaking = True
        try:
            # 1. Generăm fișierul audio cu Google
            # lang='ro' e esențial
            tts = gTTS(text=text, lang='ro', slow=False)
            filename = "temp_audio.mp3"
            
            # Salvăm
            tts.save(filename)
            
            # 2. Redăm fișierul
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Așteptăm să termine de vorbit
            while pygame.mixer.music.get_busy():
                if self.stop_event.is_set():
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)
                
            # Curățenie (Opțional)
            # os.remove(filename) 
            
        except Exception as e:
            print(f"Eroare TTS: {e}")
        
        self.is_speaking = False
        self.stop_event.clear()

    def stop(self):
        """Oprește vorbirea curentă"""
        self.stop_event.set()
        pygame.mixer.music.stop()