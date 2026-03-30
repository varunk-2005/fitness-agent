from agent.router import RouterAgent
from agent.workout import WorkoutAgent
from agent.nutrition import NutritionAgent
from agent.recovery import RecoveryAgent
from agent.general import GeneralAgent
from agent.email_agent import EmailAgent
from agent.full_package_agent import FullPackageAgent # ⬅️ Replaced PlannerAgent

class AgentRouter:
    def __init__(self, db_client=None): # ⬅️ Now accepts the DB connection
        self.router = RouterAgent()
        
        # Pass db_client to core agents so they can save themselves to Firestore
        self.workout_agent = WorkoutAgent(db_client)
        self.nutrition_agent = NutritionAgent(db_client)
        self.recovery_agent = RecoveryAgent(db_client)
        self.general_agent = GeneralAgent()
        
        # EmailAgent is now standalone
        self.email_agent = EmailAgent(db_client)
        
        # FullPackageAgent facilitates the debate (No EmailAgent passed in!)
        self.full_package_agent = FullPackageAgent(
            self.workout_agent,
            self.nutrition_agent,
            self.recovery_agent
        )

    def set_username(self, username):
        """Helper to let app.py easily pass the logged-in user to all agents"""
        self.workout_agent.username = username
        self.nutrition_agent.username = username
        self.recovery_agent.username = username
        self.full_package_agent.username = username
        self.email_agent.username = username

    def _route_and_run(self, query):
        category = self.router.run(query)

        if category == "plan":
            # Triggers the new Debate + Synthesis logic
            return self.full_package_agent.build_full_plan_with_debate(query), "plan"
            
        elif category == "workout":
            return self.workout_agent.run(query), category
            
        elif category == "nutrition":
            return self.nutrition_agent.run(query), category
            
        elif category == "both":
            # Because agents now self-save, calling run() automatically updates the DB for both!
            workout_reply = self.workout_agent.run(query)
            nutrition_reply = self.nutrition_agent.run(query)
            return f"💪 **Workout:**\n{workout_reply}\n\n🥗 **Nutrition:**\n{nutrition_reply}", category
            
        elif category == "recovery":
            return self.recovery_agent.run(query), category
            
        else:
            return None, "general"

    def run(self, user_input):
        reply, category = self._route_and_run(user_input)
        
        if category != "general":
            self.general_agent.add_assistant_reply(reply)
            return reply, category
            
        rewritten = self.general_agent.run(user_input)
        if rewritten:
            reply, category = self._route_and_run(rewritten)
            if category != "general":
                self.general_agent.add_assistant_reply(reply)
                return reply, category
                
        reply = self.general_agent.chat(user_input)
        return reply, "general"

if __name__ == "__main__":
    # If running locally for testing, we can pass None for the DB
    agent = AgentRouter(db_client=None) 
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        reply, route = agent.run(user_input)
        print(f"\nAgent [{route}]: {reply}\n")