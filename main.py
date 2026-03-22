from agent.router import RouterAgent
from agent.workout import WorkoutAgent
from agent.nutrition import NutritionAgent
from agent.recovery import RecoveryAgent
from agent.general import GeneralAgent

class AgentRouter:
    def __init__(self):
        self.router = RouterAgent()
        self.workout_agent = WorkoutAgent()
        self.nutrition_agent = NutritionAgent()
        self.recovery_agent = RecoveryAgent()
        self.general_agent = GeneralAgent()

    def _route_and_run(self, query):
        category = self.router.run(query)
        if category == "workout":
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
    agent = AgentRouter()
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        reply, route = agent.run(user_input)
        print(f"\nAgent [{route}]: {reply}\n")