import os
from dotenv import load_dotenv
from google import genai
load_dotenv()

class RouterAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
        self.system_prompt = """You are a routing agent for a fitness assistant app.

Your job is to classify the user's message into exactly one of these categories:

- workout   → questions about exercise, gym, training plans, sets/reps, muscle groups, fitness routines
- nutrition → questions about food, diet, calories, macros, protein, meal plans, supplements
- recovery  → questions about rest, sleep, soreness, injury, fatigue, stretching, overtraining
- both      → message clearly involves BOTH workout and nutrition together (e.g. "give me a diet and gym plan to lose fat")
- unknown   → message is completely unrelated to fitness (e.g. greetings, random questions)

Rules:
- Reply with ONLY one word from the list above. No punctuation, no explanation.
- When in doubt between workout and nutrition, pick both.
- Only use unknown if the message has nothing to do with fitness at all.

Examples:
"How many sets for biceps?" → workout
"What should I eat after the gym?" → nutrition
"I'm feeling sore and tired" → recovery
"Help me lose fat with a gym and diet plan" → both
"What is the capital of France?" → unknown
"""
        print("RouterAgent created!")

    def run(self, user_input):
        response = self.client.models.generate_content(
            model=self.model,
            contents=[{"role": "user", "parts": [{"text": user_input}]}],
            config={"system_instruction": self.system_prompt}
        )
        result = response.candidates[0].content.parts[0].text.strip().lower()
        # Safety check — if Gemini returns something unexpected, fall back
        valid = {"workout", "nutrition", "recovery", "both", "unknown"}
        return result if result in valid else "unknown"