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
        self.full_package_agent = FullPackageAgent(
            self.workout_agent,
            self.nutrition_agent,
            self.recovery_agent
        )

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
            reply = self.full_package_agent.build_full_plan_with_debate(full_input)
        elif category == "workout":
            reply = self.workout_agent.run(full_input)
        elif category == "nutrition":
            reply = self.nutrition_agent.run(full_input)
        elif category == "both":
            workout_reply = self.workout_agent.run(full_input)
            time.sleep(5) # Add a pause to avoid hitting API rate limits
            nutrition_reply = self.nutrition_agent.run(full_input)
            reply = f"💪 **Workout:**\n{workout_reply}\n\n🥗 **Nutrition:**\n{nutrition_reply}"
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