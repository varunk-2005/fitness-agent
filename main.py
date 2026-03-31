import time
from agent.router import RouterAgent
from agent.workout import WorkoutAgent
from agent.nutrition import NutritionAgent
from agent.recovery import RecoveryAgent
from agent.general import GeneralAgent
from agent.email_agent import EmailAgent
from agent.full_package_agent import FullPackageAgent


def _run_with_retry(fn, *args, retries=2, delay=5, **kwargs):
    """
    Call fn(*args, **kwargs). On a Gemini 429 / RESOURCE_EXHAUSTED error,
    wait `delay` seconds and retry up to `retries` times.
    All other exceptions propagate immediately.
    """
    for attempt in range(retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            err = str(e)
            is_rate_limit = "429" in err or "RESOURCE_EXHAUSTED" in err
            if is_rate_limit and attempt < retries:
                print(f"Rate limit hit — retrying in {delay}s (attempt {attempt + 1}/{retries})...")
                time.sleep(delay)
            else:
                raise


class AgentRouter:
    def __init__(self):
        self.router = RouterAgent()
        self.workout_agent = WorkoutAgent()
        self.nutrition_agent = NutritionAgent()
        self.recovery_agent = RecoveryAgent()
        self.general_agent = GeneralAgent()
        self.email_agent = EmailAgent()
        self.full_package_agent = FullPackageAgent()

    def set_username(self, username):
        """Let app.py pass the logged-in username to the email agent."""
        self.email_agent.username = username

    def reset_all(self):
        """Clear memory on all stateful agents (called on 'Clear Chat')."""
        self.workout_agent.reset()
        self.nutrition_agent.reset()
        self.recovery_agent.reset()
        self.general_agent.reset()

    def run(self, user_input, profile_text=None):
        # 1. Route the initial query (with retry)
        category = _run_with_retry(self.router.run, user_input)

        # 2. General branch: let GeneralAgent decide to chat or reroute
        if category == "general":
            reply, action = _run_with_retry(self.general_agent.run, user_input)

            if action == "reroute":
                user_input = reply
                category = _run_with_retry(self.router.run, user_input)
                if category == "general":
                    reply = (
                        "I'm not sure how to help with that. "
                        "Could you try rephrasing your fitness question?"
                    )
                    self.general_agent.add_assistant_reply(reply)
                    return reply, "general"
            else:
                self.general_agent.add_assistant_reply(reply)
                return reply, "general"

        # 3. Build input with optional profile context
        full_input = (
            f"{profile_text}\n\nUser Request: {user_input}"
            if profile_text
            else user_input
        )

        # 4. Dispatch to the correct specialist agent (all with retry)
        reply = None

        if category == "plan":
            reply = _run_with_retry(self.full_package_agent.run, full_input)

        elif category == "workout":
            reply = _run_with_retry(self.workout_agent.run, full_input)

        elif category == "nutrition":
            reply = _run_with_retry(self.nutrition_agent.run, full_input)

        elif category == "both":
            both_prompt = (
                f"{full_input}\n\n"
                "Focus only on the Workout Plan and Nutrition Plan sections. "
                "Skip the Recovery section unless the user explicitly asked for it."
            )
            print("Running 'both' route via FullPackageAgent...")
            reply = _run_with_retry(self.full_package_agent.run, both_prompt)

        elif category == "recovery":
            reply = _run_with_retry(self.recovery_agent.run, full_input)

        else:
            reply = "I seem to be stuck! Please try asking in a different way."
            category = "general"

        self.general_agent.add_assistant_reply(reply)
        return reply, category


# CLI entry-point (optional, for local testing)
if __name__ == "__main__":
    agent = AgentRouter()
    print("Fitness AI Agent — type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break
        reply, route = agent.run(user_input)
        print(f"\nAgent [{route}]: {reply}\n")