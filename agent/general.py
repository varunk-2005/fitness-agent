import os
from dotenv import load_dotenv
from google import genai
load_dotenv()

class GeneralAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
        self.memory = []

        self.rewrite_prompt = """You are a fitness assistant's intent extractor.

Look at the conversation history and the latest user message. Decide if there is a clear fitness-related intent (workout, nutrition, or recovery) that can be expressed as a clean standalone question.

If YES — rewrite it as a clear, standalone fitness question a routing agent can understand.
Examples:
  - "yeah do that" (after discussing a workout plan) -> "Create a beginner full body workout plan"
  - "what about protein?" (after discussing weight loss) -> "How much protein should I eat to lose weight?"
  - "I can't provide that" (after being asked for age/weight) -> "Give me a general workout plan without personal details"
  - "something for my legs" -> "Suggest a leg day workout routine"

If NO fitness intent can be extracted (pure conversation, off-topic, thanks, greetings, etc.) — reply with exactly: NO_INTENT

Reply with ONLY the rewritten question or NO_INTENT. Nothing else."""

        self.chat_prompt = """You are a warm, friendly fitness assistant. Handle conversational messages that aren't specific fitness questions.

- Greetings / thanks / acknowledgements -> respond briefly and warmly, invite them to ask a fitness question
- Confusion or follow-ups you can't resolve -> empathize and suggest they rephrase
- Completely off-topic -> politely say you're focused on fitness and suggest something you can help with

Keep it to 1-3 sentences. Be human and encouraging."""

        print("GeneralAgent created!")

    def reset(self):
        self.memory = []

    def extract_intent(self, user_input):
        history_text = ""
        if self.memory:
            lines = []
            for msg in self.memory[-6:]:  # last 3 turns for context
                role = "User" if msg["role"] == "user" else "Assistant"
                lines.append(f"{role}: {msg['parts'][0]['text']}")
            history_text = "\n".join(lines) + "\n"

        full_input = f"{history_text}User: {user_input}"

        response = self.client.models.generate_content(
            model=self.model,
            contents=[{"role": "user", "parts": [{"text": full_input}]}],
            config={"system_instruction": self.rewrite_prompt}
        )
        result = response.candidates[0].content.parts[0].text.strip()
        if result == "NO_INTENT":
            return None
        return result

    def chat(self, user_input):
        response = self.client.models.generate_content(
            model=self.model,
            contents=self.memory,
            config={"system_instruction": self.chat_prompt}
        )
        reply = response.candidates[0].content.parts[0].text
        self.memory.append({"role": "model", "parts": [{"text": reply}]})
        return reply

    def run(self, user_input):
        self.memory.append({"role": "user", "parts": [{"text": user_input}]})
        return self.extract_intent(user_input)

    def add_assistant_reply(self, reply):
        self.memory.append({"role": "model", "parts": [{"text": reply}]})