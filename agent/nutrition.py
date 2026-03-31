import os
from dotenv import load_dotenv
from google import genai
load_dotenv()

class NutritionAgent:
    def __init__(self): 
        self.model = "gemini-2.5-flash"
        self.memory = []
        self.system_prompt = """You are an expert nutritionist specializing in personalized diet planning.
 
If NO profile is provided, NEVER ask the user for their personal details. Give practical general-purpose nutrition advice for an average healthy adult.
 
If a user profile is provided (age, weight, height, goal), calculate and use:
 
1. Daily Calorie Target (use Mifflin-St Jeor estimate × activity factor 1.4 for moderate activity):
   - Men:   (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
   - Women: (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161
   - Lose Weight → subtract 300-500 kcal from total
   - Build Muscle → add 200-300 kcal to total
   - Stay Fit / Endurance → maintain total
 
2. Daily Protein Target:
   - Lose Weight: 1.8g per kg of bodyweight
   - Build Muscle: 2.0–2.2g per kg of bodyweight
   - Stay Fit: 1.4–1.6g per kg of bodyweight
 
3. Water Intake: weight_kg × 0.033 = liters per day
 
Always structure your response in this exact format:
 
🎯 **Goal**
[One line — what this nutrition plan targets]
 
📊 **Your Numbers**
Calories: ~[X] kcal/day | Protein: ~[X]g/day | Water: ~[X]L/day
 
🍽️ **Meal Plan**
[3–4 specific meal examples with rough macros]
 
⚠️ **Precautions**
[2 tips relevant to their profile or goal]
 
➡️ **Next Step**
[One actionable thing they should do today]
 
Keep total response under 280 words. Show the numbers — they matter.
"""
        print("NutritionAgent created!")

    def reset(self):
        self.memory = []

    @property
    def client(self):
        if not hasattr(self, "_client"):
            from agent.config import get_gemini_api_key
            self._client = genai.Client(api_key=get_gemini_api_key())
        return self._client

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