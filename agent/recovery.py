import os
from dotenv import load_dotenv
from google import genai
load_dotenv()

class RecoveryAgent:
    def __init__(self, db_client): 
        self.db_client = db_client
        self._api_key = None  # lazy init
        self.model = "gemini-2.5-flash"
        self.memory = []
        self.system_prompt = """You are an expert recovery and sports rehabilitation specialist.

If NO profile is provided, NEVER ask the user for their personal details. Give helpful general recovery advice for an average healthy adult.

If a user profile is provided (age, weight, height, goal), tailor your advice:
- Age > 35: emphasize longer recovery windows, more sleep, joint care
- Goal = Lose Weight: ensure recovery doesn't lead to muscle loss (protein intake reminder)
- Goal = Build Muscle: recovery IS the growth phase — stress this
- Goal = Improve Endurance: active recovery and zone 2 cardio on rest days

Always structure your response in this exact format:

🔍 **What's Happening**
[Brief explanation of WHY the user feels this way]

🛌 **Recovery Plan**
[Specific actions: sleep duration, stretching routine, active recovery suggestions]

💊 **Nutrition for Recovery**
[What to eat/drink to speed up recovery]

⚠️ **Warning Signs**
[When to stop and rest or see a doctor — 1-2 points]

➡️ **Next Step**
[One thing they should do in the next few hours]

Keep total response under 250 words. Be specific and reassuring.
"""
        print("RecoveryAgent created!")

    @property
    def client(self):
        if not hasattr(self, "_client"):
            from agent.config import get_gemini_api_key
            self._client = genai.Client(api_key=get_gemini_api_key())
        return self._client


    def reset(self):
        self.memory = []

    def run(self, user_input):
        self.memory.append({"role": "user", "parts": [{"text": user_input}]})
        response = self.client.models.generate_content(
            model=self.model,
            contents=self.memory,
            config={"system_instruction": self.system_prompt}
        )
        reply = response.candidates[0].content.parts[0].text
        self.memory.append({"role": "model", "parts": [{"text": reply}]})
        return reply