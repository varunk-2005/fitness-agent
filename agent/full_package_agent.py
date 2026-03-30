import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class FullPackageAgent:
    def __init__(self):
        self._api_key = None  # lazy init
        self.model = "gemini-2.5-flash"
        
        self.system_prompt = """You are an elite Head Fitness Coach, an expert in synthesizing workout, nutrition, and recovery into a single, cohesive, and easy-to-follow master plan.
        
        You will receive a user request, which may include a personal profile (age, weight, height, goal).
        
        **YOUR TASK:**
        Generate a complete, actionable, and personalized weekly fitness plan that integrates:
        1.  **Workout Plan:** A structured exercise routine (e.g., days, exercises, sets, reps).
        2.  **Nutrition Plan:** Key dietary guidelines, including calorie/protein targets and sample meals.
        3.  **Recovery Plan:** Essential recovery protocols, such as sleep recommendations, stretching, and rest day activities.
        
        **CRITICAL INSTRUCTIONS:**
        - **If a user profile is provided,** you MUST use it to tailor every aspect of the plan. Calculate BMI and calorie/protein targets where applicable, and adjust intensity and recovery advice based on age and goals.
        - **If NO profile is provided,** create a high-quality, general-purpose plan for a healthy adult. DO NOT ask for their details.
        - **Structure the output clearly** with markdown headings for "Workout Plan", "Nutrition Plan", and "Recovery Plan".
        - Be encouraging, clear, and concise. The final output should be a single, unified document.
        """
        print("FullPackageAgent created!")

    @property
    def client(self):
        if not hasattr(self, "_client"):
            from agent.config import get_gemini_api_key
            self._client = genai.Client(api_key=get_gemini_api_key())
        return self._client


    def run(self, full_input):
        print("\n📢 FullPackageAgent: Generating a complete, unified plan...")
        response = self.client.models.generate_content(
            model=self.model,
            contents=[{"role": "user", "parts": [{"text": full_input}]}],
            config={"system_instruction": self.system_prompt}
        )
        
        final_plan = response.candidates[0].content.parts[0].text
        
        print("✅ Master Plan Complete!\n")
        return final_plan