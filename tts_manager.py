import pygame
from gtts import gTTS
import threading
import time
import os

class TTSManager:
    def __init__(self):
        # 1. Configurare Audio Forțată
        try:
            # Pre-inițializare pentru a evita lag-ul
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            pygame.mixer.music.set_volume(1.0) # Volum maxim
            print("🔊 Mixer Audio: CONECTAT.")
        except Exception as e:
            print(f"❌ CRITIC: Nu pot inițializa audio: {e}")

        self.stop_event = threading.Event()
        self.paused = False
        self.current_lang = 'ro'

    def set_language(self, lang_code):
        self.current_lang = lang_code

    def set_gender(self, gender):
        pass 

    def speak(self, text):
        # Oprim ce era inainte
        self.stop()
        
        if not text or len(text.strip()) == 0: return

        self.paused = False
        self.unpause()
        
        # Curățare text
        clean_text = text.replace('*', '').replace('#', '').strip()
        
        # Pornim thread-ul
        thread = threading.Thread(target=self._speak_thread, args=(clean_text,), daemon=True)
        thread.start()

    def _speak_thread(self, text):
        self.stop_event.clear()
        
        filename = f"tts_{int(time.time())}.mp3"
        success = False

        # --- 1. DESCĂRCARE (gTTS) ---
        try:
            print(f"⬇️ Descarc audio pentru: '{text[:15]}...'")
            lang = 'ro' if self.current_lang == 'ro' else self.current_lang
            if lang not in ['ro', 'en', 'ru']: lang = 'ro'
            
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(f"audio/{filename}")
            success = True
            print("✅ Audio descărcat.")
        except Exception as e:
            print(f"❌ EROARE NET/gTTS: {e}")
            return # Ieșim dacă nu avem fișier

        # --- 2. REDARE (Pygame) ---
        if success and os.path.exists(filename):
            try:
                # Verificare ultim moment
                if self.stop_event.is_set():
                    try: os.remove(filename); 
                    except: pass
                    return

                print("▶️ Încep redarea...")
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                
                # Bucla de așteptare
                while pygame.mixer.music.get_busy() or self.paused:
                    if self.stop_event.is_set():
                        pygame.mixer.music.stop()
                        break
                    
                    if self.paused:
                        time.sleep(0.1)
                        continue
                        
                    time.sleep(0.1)
            
            except Exception as e:
                print(f"❌ EROARE REDARE: {e}")
            
            finally:
                # --- 3. CURĂȚENIE ---
                try:
                    pygame.mixer.music.unload()
                    time.sleep(0.1) # Dăm timp sistemului să elibereze fișierul
                    if os.path.exists(filename):
                        os.remove(filename)
                        print("🗑️ Cache șters.")
                except:
                    pass

    def pause(self):
        self.paused = True
        if pygame.mixer.music.get_busy(): 
            pygame.mixer.music.pause()
            print("II Pauză.")

    def unpause(self):
        self.paused = False
        try: 
            pygame.mixer.music.unpause()
            print("▶ Reluare.")
        except: pass

    def stop(self):
        self.stop_event.set()
        self.paused = False
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except: pass