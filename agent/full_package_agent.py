import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class FullPackageAgent:
    def __init__(self, workout_agent, nutrition_agent, recovery_agent):
        self.workout_agent = workout_agent
        self.nutrition_agent = nutrition_agent
        self.recovery_agent = recovery_agent
        self.username = None # Set by app.py
        
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    def build_full_plan_with_debate(self, user_input):
        """Runs the 3-round debate and returns a dictionary for the UI"""
      
        workout_r1 = self.workout_agent.run(user_input)
        nutrition_r1 = self.nutrition_agent.run(user_input)
        recovery_r1 = self.recovery_agent.run(user_input)

  
        critique_prompt_template = """
        You are reviewing proposals from other fitness experts based on the user's request: "{user_input}"
        
        Workout Proposal: {w}
        Nutrition Proposal: {n}
        Recovery Proposal: {r}
        
        Provide a 2-sentence critique. Do these plans clash? (e.g., Is the workout too intense for the calories provided? Is there enough sleep for this volume?)
        """
        
        combined_r1 = critique_prompt_template.format(
            user_input=user_input, w=workout_r1, n=nutrition_r1, r=recovery_r1
        )

        try:
            w_critique = self.client.models.generate_content(
                model=self.model,
                contents=f"As the Workout Expert, critique this: {combined_r1}"
            ).text
            
            n_critique = self.client.models.generate_content(
                model=self.model,
                contents=f"As the Nutrition Expert, critique this: {combined_r1}"
            ).text
            
            r_critique = self.client.models.generate_content(
                model=self.model,
                contents=f"As the Recovery Expert, critique this: {combined_r1}"
            ).text
        except Exception as e:
            w_critique, n_critique, r_critique = "Critique failed.", "Critique failed.", "Critique failed."

      
        synth_prompt = f"""
        Act as the Head Coach. Create a unified, final fitness plan for the user based on this debate:
        User Goal: {user_input}
        
        Round 1 (Initial Thoughts):
        Workout: {workout_r1}
        Nutrition: {nutrition_r1}
        Recovery: {recovery_r1}
        
        Round 2 (Critiques):
        Workout Expert says: {w_critique}
        Nutrition Expert says: {n_critique}
        Recovery Expert says: {r_critique}
        
        Write a final, cohesive, highly structured plan that resolves any conflicts mentioned in the critiques.
        """
        
        try:
            final_plan = self.client.models.generate_content(
                model=self.model,
                contents=synth_prompt
            ).text
        except Exception as e:
            final_plan = "Error generating final plan."

   
        return {
            "round1": {"workout": workout_r1, "nutrition": nutrition_r1, "recovery": recovery_r1},
            "round2": {"workout": w_critique, "nutrition": n_critique, "recovery": r_critique},
            "final_plan": final_plan
        }