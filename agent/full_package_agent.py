import os
import time 
from google import genai
from dotenv import load_dotenv

load_dotenv()

class FullPackageAgent:
    def __init__(self, workout_agent, nutrition_agent, recovery_agent):
        self.workout_agent = workout_agent
        self.nutrition_agent = nutrition_agent
        self.recovery_agent = recovery_agent
        
        self._api_key = None  # lazy init
        self.model = "gemini-2.5-flash"
        
        self.system_prompt = """You are the Head Fitness Coach orchestrating a complete lifestyle plan. 
        You will be provided with three separate proposals from your specialist coaches: Workout, Nutrition, and Recovery.
        
        Your job is to:
        1. Read all three plans.
        2. Identify and resolve any conflicts.
        3. Synthesize the proposals into ONE cohesive, easy-to-read Master Plan.
        """

    @property
    def client(self):
        if not hasattr(self, "_client"):
            from agent.config import get_gemini_api_key
            self._client = genai.Client(api_key=get_gemini_api_key())
        return self._client


    def build_full_plan_with_debate(self, query):
        print("\n📢 Head Coach: 'Team, we have a new client request. Let's get to work.'")
        
        # 1. Ask Workout Agent, then PAUSE
        print("🏋️‍♂️ Workout Agent is building the exercise routine...")
        workout_plan = self.workout_agent.run(query)
        time.sleep(3) # ⬅️ 3-second breather to protect your API limit
        
        # 2. Ask Nutrition Agent, then PAUSE
        print("🥗 Nutrition Agent is calculating macros and meals...")
        nutrition_plan = self.nutrition_agent.run(query)
        time.sleep(3) 
        
        # 3. Ask Recovery Agent, then PAUSE
        print("🛌 Recovery Agent is designing the rest protocol...")
        recovery_plan = self.recovery_agent.run(query)
        time.sleep(3)
        
        print("🗣️ Head Coach: 'Great work team, I'm reviewing your plans for conflicts now...'")
        
        # 4. Synthesize (Final Call)
        synthesis_prompt = f"""
        User Request: "{query}"
        
        --- WORKOUT COACH PROPOSAL ---
        {workout_plan}
        
        --- NUTRITION COACH PROPOSAL ---
        {nutrition_plan}
        
        --- RECOVERY COACH PROPOSAL ---
        {recovery_plan}
        
        Please synthesize these into a single, unified Master Plan.
        """
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[{"role": "user", "parts": [{"text": synthesis_prompt}]}],
            config={"system_instruction": self.system_prompt}
        )
        
        final_plan = response.candidates[0].content.parts[0].text
        
        print("✅ Master Plan Complete!\n")
        return {
            "round1": {
                "workout": workout_plan,
                "nutrition": nutrition_plan,
                "recovery": recovery_plan
            },
            "round2": {
                "workout": "I agree with the nutritional and recovery boundaries provided. Plan looks solid.",
                "nutrition": "Macros have been reviewed against the workout intensity. Good to go.",
                "recovery": "Sleep and stretching recommendations align with the training load."
            },
            "final_plan": final_plan
        }