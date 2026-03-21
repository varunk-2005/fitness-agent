from agent.router import RouterAgent
from agent.workout import WorkoutAgent
from agent.nutrition import NutritionAgent
from agent.recovery import recoveryAgent
class AgentRouter:
    def __init__(self):
        self.router = RouterAgent()
        self.workout_agent = WorkoutAgent()
        self.nutrition_agent = NutritionAgent()
        self.recovery_agent = recoveryAgent()

    def run(self, user_input):
        category = self.router.run(user_input)
        if category == "workout":
            return self.workout_agent.run(user_input), category
        elif category == "nutrition":
            return self.nutrition_agent.run(user_input), category
        elif category == "both":
            workout_reply = self.workout_agent.run(user_input)
            nutrition_reply = self.nutrition_agent.run(user_input)
            return f"💪 **Workout:**\n{workout_reply}\n\n🥗 **Nutrition:**\n{nutrition_reply}", category
        elif category == "recovery":
            return self.recovery_agent.run(user_input), category
        else:
            return "Sorry, I couldn't classify your message.", "unknown"

if __name__ == "__main__":
    agent = AgentRouter()
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        reply = agent.run(user_input)
        print(f"\nAgent: {reply}\n")