import google.generativeai as genai
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_KEY") or "PUNE_CHEIA_TA_AICI"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except:
    model = None

class UniversityAI:
    def __init__(self):
        self.data = self.load_data()
        self.current_personality = 1
        self.current_lang = 'ro' # Default
        
        # Dicționar de întrebări traduse pentru butoane
        self.questions_db = {
            'ro': ["Ce specializări există?", "Cât durează studiile?", "Unde e facultatea?", "Locuri la buget?", "Admiterea e grea?", "Există cantină?", "Cum sunt căminele?", "Burse Erasmus?", "Număr studenți?", "De ce FACIEE?"],
            'en': ["What majors are there?", "How long are studies?", "Where is the faculty?", "Tuition free spots?", "Is admission hard?", "Is there a cafeteria?", "How are the dorms?", "Erasmus scholarships?", "Student count?", "Why FACIEE?"],
            'ru': ["Какие есть специальности?", "Сколько длится обучение?", "Где факультет?", "Бюджетные места?", "Сложно ли поступить?", "Есть ли столовая?", "Как общежития?", "Стипендии Erasmus?", "Сколько студентов?", "Почему FACIEE?"]
        }

    def set_personality(self, index):
        self.current_personality = index

    def set_language(self, lang_code):
        self.current_lang = lang_code

    def load_data(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, 'data.json')
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def get_random_shortcuts(self):
        # Returnăm întrebări în limba curentă
        pool = self.questions_db.get(self.current_lang, self.questions_db['ro'])
        return random.sample(pool, 3)

    def ask_gemini(self, user_question):
        if not model: return "Eroare API Key."

        # Instrucțiuni de limbă
        lang_instruction = ""
        if self.current_lang == 'ro': lang_instruction = "Răspunde în limba ROMÂNĂ."
        if self.current_lang == 'en': lang_instruction = "Reply in ENGLISH language."
        if self.current_lang == 'ru': lang_instruction = "Отвечай на РУССКОМ языке."

        # Personaje
        if self.current_personality == 1:
            role = "Ești ANA, studentă. Calmă, politicoasă."
        elif self.current_personality == 2:
            role = "Ești PROFESORUL IONESCU. Academic, formal, serios."
        elif self.current_personality == 3:
            role = "Ești ALEX (Student). Folosește slang, relaxat."
        else:
            role = "Ești asistent."

        context = f"""
        {role}
        REGULI DE REDACTARE: 2-3 propozitii, fara caractere speciale.
        IMPORTANT: {lang_instruction}
        Folosește aceste date: {json.dumps(self.data, ensure_ascii=False)}
        ÎNTREBARE: {user_question}
        """
        
        try:
            response = model.generate_content(context)
            return response.text
        except:
            return "Connection error."