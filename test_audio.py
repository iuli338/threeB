import asyncio
import edge_tts
import pygame
import os

# PUNE AICI UN NUME DE VOCE PE CARE L-AI GĂSIT LA PASUL 1
VOICE = "ro-RO-AlinaNeural" 
TEXT = "Salut! Acesta este un test de sunet."
OUTPUT = "test_sunet.mp3"

async def generate():
    print(f"Generăm audio cu vocea: {VOICE}...")
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT)
    print("Fișier salvat!")

def play():
    print("Redăm sunetul...")
    pygame.mixer.init()
    pygame.mixer.music.load(OUTPUT)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass
    print("Gata.")

if __name__ == "__main__":
    try:
        asyncio.run(generate())
        play()
    except Exception as e:
        print(f"EROARE: {e}")