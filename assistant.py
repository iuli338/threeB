import google.generativeai as genai
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_KEY") or "PUNE_CHEIA_AICI_DACA_NU_AI_ENV"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
except:
    model = None

class UniversityAI:
    def __init__(self):
        self.data = self.load_data()
        self.current_personality = 1
        
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
        if not model: return "Eroare API Key."

        # --- DEFINIREA PERSONAJELOR ---
        if self.current_personality == 1:
            role = "Ești ANA, o studentă eminentă la FACIEE. Ești calmă, politicoasă și vorbești clar. Te prezinți ca Ana."
        elif self.current_personality == 2:
            role = "Ești DOMNUL PROFESOR IONESCU. Ești un bărbat în vârstă, foarte respectat. Vorbești formal, academic și puțin sever dar corect. Te prezinți ca Profesorul Ionescu."
        elif self.current_personality == 3:
            role = "Ești ALEX, un student anul 2. Ești super relaxat, folosești slang ('frate', 'gen', 'nașpa'). Ești prietenos și glumeț. Te prezinți ca Alex."
        else:
            role = "Ești un asistent util."

        context = f"""
        {role}
        SARCINA: Răspunde utilizatorului folosind datele din JSON.
        REGULĂ AUDIO: Răspunsul tău va fi citit de un sintetizator vocal, așa că nu folosi prea multe emoticoane în text, scrie cuvintele întregi.
        DATE: {json.dumps(self.data, ensure_ascii=False)}
        ÎNTREBARE: {user_question}
        """
        
        try:
            response = model.generate_content(context)
            return response.text
        except:
            return "Nu pot răspunde acum."