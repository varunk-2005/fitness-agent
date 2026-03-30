from agent.router import RouterAgent
from agent.workout import WorkoutAgent
from agent.nutrition import NutritionAgent
from agent.recovery import RecoveryAgent
from agent.general import GeneralAgent
import time
from agent.email_agent import EmailAgent
from agent.full_package_agent import FullPackageAgent # ⬅️ Replaced PlannerAgent

class AgentRouter:
    def __init__(self):
        self.router = RouterAgent()
        
        self.workout_agent = WorkoutAgent()
        self.nutrition_agent = NutritionAgent()
        self.recovery_agent = RecoveryAgent()
        self.general_agent = GeneralAgent()
        
        self.email_agent = EmailAgent()
        
        # FullPackageAgent facilitates the debate
        self.full_package_agent = FullPackageAgent()

    def set_username(self, username):
        """Helper to let app.py easily pass the logged-in user to the email agent"""
        self.email_agent.username = username

    def run(self, user_input, profile_text=None):
        # 1. Route the initial query
        category = self.router.run(user_input)

        # 2. If the category is general, let the GeneralAgent decide what to do
        if category == "general":
            # This single call will either rewrite the query or return a chat response
            reply, action = self.general_agent.run(user_input)
            
            if action == "reroute":
                # The query was rewritten, so we re-route it and update the input
                user_input = reply 
                category = self.router.run(user_input)
                # If the rewritten query is ALSO general, fallback to a safe chat response
                if category == "general":
                    reply = "I'm not sure how to help with that. Could you try rephrasing your request?"
                    self.general_agent.add_assistant_reply(reply)
                    return reply, "general"
            else: # action == "general"
                # It was a chat message, so we're done.
                self.general_agent.add_assistant_reply(reply)
                return reply, "general"

        # 3. Now we have a definitive, non-general category. Run the specialist agent.
        # Construct the full input with profile for the specialist agents.
        full_input = f"{profile_text}\n\nUser Request: {user_input}" if profile_text else user_input
        
        reply = None
        if category == "plan":
            reply = self.full_package_agent.run(full_input)
        elif category == "workout":
            reply = self.workout_agent.run(full_input)
        elif category == "nutrition":
            reply = self.nutrition_agent.run(full_input)
        elif category == "both":
            # Create a temporary prompt to handle both in one call
            both_system_prompt = """You are an expert fitness coach who specializes in creating integrated workout and nutrition plans.
            - If a user profile is provided, use it to tailor the response.
            - If no profile is provided, give a general-purpose plan.
            - Structure your response with two main sections: '💪 Workout Plan' and '🥗 Nutrition Plan'.
            """
            print("🤖 Running 'both' route with a single API call...")
            response = self.general_agent.client.models.generate_content(
                model=self.general_agent.model,
                contents=[{"role": "user", "parts": [{"text": full_input}]}],
                config={"system_instruction": both_system_prompt}
            )
            reply = response.candidates[0].content.parts[0].text
        elif category == "recovery":
            reply = self.recovery_agent.run(full_input)
        else: # Should not happen, but as a fallback
            reply = "I seem to be stuck! Please try asking in a different way."
            category = "general"

        self.general_agent.add_assistant_reply(reply)
        return reply, category

if __name__ == "__main__":
    agent = AgentRouter() 
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        reply, route = agent.run(user_input)
        print(f"\nAgent [{route}]: {reply}\n")