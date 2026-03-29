from agent.router import RouterAgent
from agent.workout import WorkoutAgent
from agent.nutrition import NutritionAgent
from agent.recovery import RecoveryAgent
from agent.general import GeneralAgent
from agent.email_agent import EmailAgent
from agent.planner import PlannerAgent

class AgentRouter:
    def __init__(self):
        self.router = RouterAgent()
        self.workout_agent = WorkoutAgent()
        self.nutrition_agent = NutritionAgent()
        self.recovery_agent = RecoveryAgent()
        self.general_agent = GeneralAgent()
        self.email_agent = EmailAgent()
        self.planner_agent = PlannerAgent(
            self.workout_agent,
            self.nutrition_agent,
            self.recovery_agent,
            self.email_agent
        )

    def _route_and_run(self, query, user_email=None):
        category = self.router.run(query)

        if category == "plan":
            return self.planner_agent.build_full_plan(query, user_email), "plan"
        elif category == "workout":
            return self.workout_agent.run(query), category
        elif category == "nutrition":
            return self.nutrition_agent.run(query), category
        elif category == "both":
            workout_reply = self.workout_agent.run(query)
            nutrition_reply = self.nutrition_agent.run(query)
            return f"💪 **Workout:**\n{workout_reply}\n\n🥗 **Nutrition:**\n{nutrition_reply}", category
        elif category == "recovery":
            return self.recovery_agent.run(query), category
        else:
            return None, "general"

    def run(self, user_input, user_email=None):
        reply, category = self._route_and_run(user_input, user_email)
        if category != "general":
            self.general_agent.add_assistant_reply(reply)
            return reply, category
        rewritten = self.general_agent.run(user_input)
        if rewritten:
            reply, category = self._route_and_run(rewritten, user_email)
            if category != "general":
                self.general_agent.add_assistant_reply(reply)
                return reply, category
        reply = self.general_agent.chat(user_input)
        return reply, "general"

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