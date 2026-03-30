import os
from dotenv import load_dotenv
from google import genai
load_dotenv()

class RouterAgent:
    def __init__(self):
        self._api_key = None  # lazy init
        self.model = "gemini-2.5-flash"
        self.system_prompt = """You are a routing agent for a fitness assistant app.

Your job is to classify the user's message into exactly one of these categories:

- workout   → questions about exercise, gym, training plans, sets/reps, muscle groups, fitness routines
- nutrition → questions about food, diet, calories, macros, protein, meal plans, supplements
- recovery  → questions about rest, sleep, soreness, injury, fatigue, stretching, overtraining
- both      → message clearly involves BOTH workout and nutrition together (e.g. "give me a diet and gym plan to lose fat")
- plan      → user wants a COMPLETE package: workout + nutrition + recovery together
              (e.g. "give me a full weekly plan", "create a complete fitness routine", "full package for weight loss")
- general   → conversational messages, follow-ups, short replies (e.g. "ok", "thanks", "I can't provide that", "what do you mean"), or anything unclear

Rules:
- Reply with ONLY one word from the list above. No punctuation, no explanation.
- When in doubt between workout and nutrition, pick both.
- Only use general if the message is conversational, a follow-up, or cannot be clearly mapped to a fitness topic.

Examples:
"Give me a complete weekly fitness plan" → plan
"Full package to lose 10kg" → plan
"How many sets for biceps?" → workout
"What should I eat after the gym?" → nutrition
"I'm feeling sore and tired" → recovery
"Help me lose fat with a gym and diet plan" → both
"ok", "thanks", "I can't provide that", "what is the capital of France?" → general
"""
        print("RouterAgent created!")

    @property
    def client(self):
        if not hasattr(self, "_client"):
            from agent.config import get_gemini_api_key
            self._client = __import__("google.genai", fromlist=["genai"]).Client(api_key=get_gemini_api_key())
        return self._client


    def run(self, user_input):
        response = self.client.models.generate_content(
            model=self.model,
            contents=[{"role": "user", "parts": [{"text": user_input}]}],
            config={"system_instruction": self.system_prompt}
        )
        result = response.candidates[0].content.parts[0].text.strip().lower()
        valid = {"workout", "nutrition", "recovery", "both", "general", "plan"}  # ✅ plan added
        return result if result in valid else "general"