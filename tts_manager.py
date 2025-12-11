import pygame
from gtts import gTTS
import threading
import time
import os
import subprocess
import sys
import glob

class TTSManager:
    def __init__(self):
        try:
            pygame.mixer.init()
        except:
            print("Eroare audio mixer")

        self.stop_event = threading.Event()
        self.current_lang = 'ro'
        self.current_gender = 'female'
        
        # --- MODIFICARE: Configurare folder audio ---
        self.audio_folder = "audio"
        self.last_filename = None
        
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)
        else:
            # Opțional: Curăță folderul la pornirea aplicației
            self._clean_folder()

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

    def _clean_folder(self):
        """Șterge toate fișierele mp3 din folderul audio"""
        try:
            files = glob.glob(os.path.join(self.audio_folder, "*.mp3"))
            for f in files:
                try: os.remove(f)
                except: pass
        except Exception as e:
            print(f"Eroare curățare folder: {e}")

    def _delete_last_file(self):
        """Șterge specific ultimul fișier redat"""
        # Important: Eliberăm resursa din pygame înainte de ștergere
        try:
            pygame.mixer.music.unload()
        except:
            pass
            
        if self.last_filename and os.path.exists(self.last_filename):
            try:
                os.remove(self.last_filename)
                self.last_filename = None
            except Exception as e:
                print(f"Nu s-a putut șterge fișierul vechi: {e}")

    def speak(self, text):
        # 1. Oprim orice redare curentă
        self.stop()
        
        # 2. Ștergem fișierul anterior (pentru a nu se aduna gunoi)
        self._delete_last_file()

        if not text or len(text.strip()) == 0: return

        # Curățăm textul
        clean_text = text.replace('"', '').replace("'", "")
        
        thread = threading.Thread(target=self._speak_thread, args=(clean_text,), daemon=True)
        thread.start()

    def _speak_thread(self, text):
        self.stop_event.clear()
        
        # --- MODIFICARE: Cale fișier în folderul audio ---
        filename_only = f"tts_{int(time.time())}.mp3"
        filepath = os.path.join(self.audio_folder, filename_only)
        
        self.last_filename = filepath
        success = False

        # --- ÎNCERCARE 1: EDGE-TTS ---
        try:
            lang_voices = self.neural_voices.get(self.current_lang, self.neural_voices['ro'])
            voice_name = lang_voices.get(self.current_gender, lang_voices['female'])
            
            cmd = [
                sys.executable, "-m", "edge_tts",
                "--text", text,
                "--write-media", filepath,
                "--voice", voice_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(filepath) and os.path.getsize(filepath) > 0:
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
                tts.save(filepath)
                success = True
            except Exception as e:
                print(f"❌ Și gTTS a eșuat: {e}")

        # --- REDARE ---
        if success and os.path.exists(filepath):
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    if self.stop_event.is_set():
                        pygame.mixer.music.stop()
                        break
                    time.sleep(0.1)
                
                # După ce termină redarea naturală, eliberăm fișierul
                pygame.mixer.music.unload()
                
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
        try:
            pygame.mixer.music.unload()
        except:
            pass