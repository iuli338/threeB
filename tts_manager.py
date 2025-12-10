import pygame
from gtts import gTTS
import threading
import time
import os
import subprocess
import sys

class TTSManager:
    def __init__(self):
        try:
            pygame.mixer.init()
        except:
            print("Eroare audio mixer")

        self.stop_event = threading.Event()
        self.current_lang = 'ro'
        self.current_gender = 'female'

        # Numele vocilor (Exacte pentru comanda CLI)
        self.neural_voices = {
            'ro': {'female': 'ro-RO-AlinaNeural', 'male': 'ro-RO-EmilNeural'},
            'en': {'female': 'en-US-AriaNeural',  'male': 'en-US-ChristopherNeural'},
            'ru': {'female': 'ru-RU-SvetlanaNeural', 'male': 'ru-RU-DmitryNeural'}
        }

    def set_language(self, lang_code):
        self.current_lang = lang_code

    def set_gender(self, gender):
        self.current_gender = gender

    def speak(self, text):
        self.stop()
        if not text or len(text.strip()) == 0: return

        # Curățăm textul de ghilimele care ar putea strica comanda
        clean_text = text.replace('"', '').replace("'", "")
        
        thread = threading.Thread(target=self._speak_thread, args=(clean_text,), daemon=True)
        thread.start()

    def _speak_thread(self, text):
        self.stop_event.clear()
        filename = f"temp_tts_{int(time.time())}.mp3"
        success = False

        # --- ÎNCERCARE 1: EDGE-TTS prin LINIA DE COMANDĂ (Subprocess) ---
        # Asta ocolește complet problemele de async din Python
        try:
            lang_voices = self.neural_voices.get(self.current_lang, self.neural_voices['ro'])
            voice_name = lang_voices.get(self.current_gender, lang_voices['female'])
            
            # Construim comanda: python3 -m edge_tts ...
            # Folosim sys.executable pentru a fi siguri că folosim același Python
            cmd = [
                sys.executable, "-m", "edge_tts",
                "--text", text,
                "--write-media", filename,
                "--voice", voice_name
            ]
            
            # Executăm comanda și așteptăm să termine
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(filename) and os.path.getsize(filename) > 0:
                success = True
            else:
                print(f"⚠️ Edge-TTS CLI Error: {result.stderr}")

        except Exception as e:
            print(f"⚠️ Edge-TTS Subprocess a eșuat: {e}")

        # --- ÎNCERCARE 2: gTTS (Backup) ---
        if not success:
            print("🔄 Trecem pe gTTS (Backup)...")
            try:
                tts = gTTS(text=text, lang=self.current_lang, slow=False)
                tts.save(filename)
                success = True
            except Exception as e:
                print(f"❌ Și gTTS a eșuat: {e}")

        # --- REDARE ---
        if success and os.path.exists(filename):
            try:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    if self.stop_event.is_set():
                        pygame.mixer.music.stop()
                        break
                    time.sleep(0.1)
                
                pygame.mixer.music.unload()
                # Mică pauză ca să elibereze fișierul înainte de ștergere
                time.sleep(0.1)
                try: os.remove(filename)
                except: pass
            except Exception as e:
                print(f"Eroare la redare: {e}")

    def pause(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()

    def stop(self):
        self.stop_event.set()
        pygame.mixer.music.stop()