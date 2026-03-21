import os
from dotenv import load_dotenv
from google import genai
load_dotenv()

class RouterAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
        self.system_prompt = """You are a routing agent. Classify the user's message into one of these categories:
- workout: if the message is about exercise, training, gym, fitness routines
- nutrition: if the message is about food, diet, calories, macros
- both: if the message involves both workout and nutrition
- recovery: if the message is about recovery, rest, sleep, injury, soreness, fatigue

Reply with ONLY one word: workout, nutrition, both, or recovery. Nothing else."""
        print("RouterAgent created!")

    def run(self, user_input):
        response = self.client.models.generate_content(
            model=self.model,
            contents=[{"role": "user", "parts": [{"text": user_input}]}],
            config={"system_instruction": self.system_prompt}
        )
        return response.candidates[0].content.parts[0].text.strip().lower()