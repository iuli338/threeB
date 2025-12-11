import pygame
from gtts import gTTS
import threading
import time
import os

class TTSManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(1)
        except:
            print("❌ Eroare mixer audio")

        self.stop_event = threading.Event()
        self.paused = False
        self.current_lang = 'ro'

    def set_language(self, lang_code):
        self.current_lang = lang_code

    def set_gender(self, gender):
        pass # gTTS nu are gen, ignorăm

    def speak(self, text):
        # 1. KILL SWITCH: Oprim orice rulează acum
        self.stop()
        
        if not text or len(text.strip()) == 0: return

        # Resetăm starea
        self.paused = False
        self.unpause()
        
        # Curățare text pentru viteză
        clean_text = text.replace('*', '').replace('#', '').strip()
        
        # Pornim thread
        thread = threading.Thread(target=self._speak_thread, args=(clean_text,), daemon=True)
        thread.start()

    def _speak_thread(self, text):
        self.stop_event.clear()
        
        # Nume unic
        filename = f"tts_{int(time.time())}.mp3"
        success = False

        # --- GENERARE (Doar gTTS) ---
        try:
            lang = self.current_lang
            if lang == 'en': lang = 'en'
            elif lang == 'ru': lang = 'ru'
            else: lang = 'ro'
            
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(filename)
            success = True
        except Exception as e:
            print(f"⚠️ Eroare Net: {e}")

        # --- REDARE CU LOGICĂ DE PAUZĂ ---
        if success and os.path.exists(filename):
            try:
                # Verificare finală înainte de play
                if self.stop_event.is_set():
                    try: os.remove(filename)
                    except: pass
                    return

                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                
                # Bucle de așteptare (Pauză inteligentă)
                while pygame.mixer.music.get_busy() or self.paused:
                    # 1. Dacă userul a dat STOP (alt mesaj), ieșim instant
                    if self.stop_event.is_set():
                        pygame.mixer.music.stop()
                        break
                    
                    # 2. Dacă e PAUZĂ, stăm aici și așteptăm
                    if self.paused:
                        time.sleep(0.1)
                        continue
                        
                    time.sleep(0.05)
            
            except:
                pass
            
            finally:
                # Curățenie obligatorie
                try:
                    pygame.mixer.music.unload()
                    time.sleep(0.05)
                    if os.path.exists(filename):
                        os.remove(filename)
                except:
                    pass

    def pause(self):
        """Pune pauză (îngheață sunetul)"""
        self.paused = True
        if pygame.mixer.music.get_busy(): 
            pygame.mixer.music.pause()

    def unpause(self):
        """Reia de unde a rămas"""
        self.paused = False
        try: pygame.mixer.music.unpause()
        except: pass

    def stop(self):
        """Oprește tot și resetează"""
        self.stop_event.set()
        self.paused = False
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except: pass