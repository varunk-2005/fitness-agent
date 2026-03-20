import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
class WorkoutAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
        self.memory = []
        self.system_prompt = "You are an expert fitness coach. Give specific, actionable workout advice.Keep your response under 200 words. Be concise and specific"
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
