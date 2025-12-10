import google.generativeai as genai
import json
import random
import os
from dotenv import load_dotenv # <--- IMPORT NOU

# 1. Încărcăm variabilele din fișierul .env
load_dotenv()

# 2. Citim cheia din sistem
API_KEY = os.getenv("GEMINI_KEY")

# Verificare de siguranță
if not API_KEY:
    print("EROARE: Nu am găsit cheia în fișierul .env!")

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"!!! EROARE LA CONFIGURARE: {e}")
    model = None

class UniversityAI:
    def __init__(self):
        self.data = self.load_data()
        self.current_personality = 1 # 1 = Standard, 2 = Profesor, 3 = Student
        
        self.all_questions = [
            "Ce specializări există?", "Cât durează studiile?",
            "Ce învăț la CTI?", "Joburi după AIA?",
            "Unde e facultatea?", "Locuri la buget?",
            "Admiterea e grea?", "Parteneriate firme?",
            "Limbaje programare?", "Există cantină?",
            "Cum sunt căminele?", "Inginerie Electrică?",
            "Burse Erasmus?", "Laboratoare dotate?",
            "Medie admitere?", "Ligă studențească?",
            "Job din facultate?", "Telecomunicații?",
            "Număr studenți?", "De ce FACIEE?"
        ]

    def set_personality(self, index):
        """Schimbă personalitatea activă"""
        self.current_personality = index

    def load_data(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, 'data.json')
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def get_random_shortcuts(self):
        return random.sample(self.all_questions, 3)

    def ask_gemini(self, user_question):
        if not model:
            return "Eroare: API Key lipsă."

        # --- DEFINIREA PERSONALITĂȚILOR ---
        if self.current_personality == 1:
            role_desc = "Ești THREEB, un asistent echilibrat și prietenos. Răspunde clar și concis (max 2 fraze)."
        elif self.current_personality == 2:
            role_desc = "Ești un DOMN PROFESOR universitar foarte serios și academic. Folosește cuvinte elevate, fii politicos și detaliat. Începe propozițiile cu 'Stimate student...' sau 'Din punct de vedere academic...'."
        elif self.current_personality == 3:
            role_desc = "Ești un student 'de gașcă' (Bro). Folosește slang studențesc (gen: 'frate', 'fain', 'nașpa'), emoji-uri multe (🔥, 🚀) și fii foarte relaxat. Vorbește ca și cum ai vorbi cu un prieten la o bere."
        else:
            role_desc = "Ești un asistent util."

        context = f"""
        TIP RASPUNS: 2-3 propozitii maxim
        ROL: {role_desc}
        CONTEXT: Ești la Facultatea FACIEE Galați, stii aproape tot ce se intampla pe acolo
        DATE OFICIALE: {json.dumps(self.data, ensure_ascii=False)}
        
        ÎNTREBARE: {user_question}
        """
        
        try:
            response = model.generate_content(context)
            return response.text
        except:
            return "Eroare conexiune."