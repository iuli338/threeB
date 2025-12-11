import google.generativeai as genai
import json
import random
import os
import re
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_KEY")

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
except:
    model = None

class UniversityAI:
    def __init__(self):
        self.data = self.load_data()
        self.current_personality = 1
        self.current_lang = 'ro'
        
        # Baza de date cu întrebări (RU înlocuit cu UA)
        self.questions_db = {
            'ro': ["Ce specializări există?", "Cât durează studiile?", "Unde e facultatea?", "Locuri la buget?", "Admiterea e grea?", "Există cantină?", "Cum sunt căminele?", "Burse Erasmus?", "Număr studenți?", "De ce FACIEE?"],
            'en': ["What majors are there?", "How long are studies?", "Where is the faculty?", "Tuition free spots?", "Is admission hard?", "Is there a cafeteria?", "How are the dorms?", "Erasmus scholarships?", "Student count?", "Why FACIEE?"],
            'ua': ["Які є спеціальності?", "Скільки триває навчання?", "Де знаходиться факультет?", "Бюджетні місця?", "Чи важко вступити?", "Чи є їдальня?", "Як гуртожитки?", "Стипендії Erasmus?", "Кількість студентів?", "Чому FACIEE?"]
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
        pool = self.questions_db.get(self.current_lang, self.questions_db['ro'])
        return random.sample(pool, 3)

    def ask_gemini(self, user_question):
        if not model: 
            return {"msg": "Eroare API Key.", "ref_ids": []}

        # Instrucțiuni Limbă (UA Update)
        if self.current_lang == 'ro': lang_instr = "Răspunde în ROMÂNĂ."
        elif self.current_lang == 'en': lang_instr = "Reply in ENGLISH."
        elif self.current_lang == 'ua': lang_instr = "Відповідай УКРАЇНСЬКОЮ (Ukrainian)."
        else: lang_instr = "Răspunde în ROMÂNĂ."

        if self.current_personality == 1: p_desc = "Ești THREEB, asistent oficial. Neutru."
        elif self.current_personality == 2: p_desc = "Ești PROFESOR. Formal."
        else: p_desc = "Ești BRO (Student). Slang, chill."

        prompt = f"""
        {p_desc}
        {lang_instr}
        Te rog să analizezi întrebarea utilizatorului pe baza datelor: {json.dumps(self.data, ensure_ascii=False)}
        
        REGULĂ STRICTĂ DE FORMAT:
        Trebuie să răspunzi DOAR cu un obiect JSON valid, fără ```json.
        Format:
        {{
            "msg": "Textul răspunsului tău aici (max 2 propoziții).",
            "ref_ids": [lista_de_iduri]
        }}

        REGULA REF_IDS:
        Dacă se menționează una dintre specializări, adaugă ID-ul ei:
        1 = Automatică (AIA)
        2 = Calculatoare (C / CTI)
        3 = Electronică (IETTI)
        4 = Inginerie Electrică (IEC)
        Altfel: []
        
        ÎNTREBARE: {user_question}
        """
        
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            raw_text = re.sub(r'```json', '', raw_text)
            raw_text = re.sub(r'```', '', raw_text).strip()
            return json.loads(raw_text)
        except:
            return {"msg": "Eroare procesare răspuns.", "ref_ids": []}