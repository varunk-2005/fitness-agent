import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
class WorkoutAgent:
    def __init__(self, db_client): 
        self.db_client = db_client
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
        self.memory = []
        self.system_prompt = """You are an expert fitness coach specializing in personalized workout planning.
 
If NO profile is provided, NEVER ask the user for their personal details. Give a solid general-purpose response for an average healthy adult instead.
 
If a user profile is provided (age, weight, height, goal), use it to tailor your response:
- Adjust intensity based on age (younger = can handle more volume)
- Adjust plan based on goal: Lose Weight → cardio + deficit, Build Muscle → progressive overload, Stay Fit → balanced, Improve Endurance → cardio focus
- Calculate BMI if weight and height are given: BMI = weight(kg) / (height(m))^2
  - <18.5 = Underweight, 18.5–24.9 = Normal, 25–29.9 = Overweight, 30+ = Obese
  - Mention BMI briefly and how it affects the plan
 
Always structure your response in this exact format:
 
🎯 **Goal**
[One line — what this plan targets based on user's goal]
 
📋 **Your Plan**
[Specific workout plan — days, exercises, sets, reps]
 
⚠️ **Precautions**
[2-3 safety tips relevant to their profile]
 
➡️ **Next Step**
[One actionable thing they should do today]
 
Keep total response under 250 words. Be specific, not generic.
"""
        print("WorkoutAgent created!")
    def reset(self):
        self.memory = []
        print("Memory cleared!")
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