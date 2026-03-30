import os
from dotenv import load_dotenv
import json
from google import genai
load_dotenv()

class GeneralAgent:
    def __init__(self):
        self._api_key = None  # lazy init
        self.model = "gemini-2.5-flash"
        self.memory = []

        self.system_prompt = """You are a helpful and intelligent fitness assistant that processes user messages.

Your primary goal is to determine if the user has a clear fitness-related intent that can be passed to a specialized agent.

Analyze the conversation history and the latest user message.

1.  **If a clear fitness intent can be extracted**, rewrite the user's message as a standalone, actionable question. The output MUST be formatted as a JSON object:
    `{"action": "reroute", "query": "Your rewritten, standalone question here."}`

    Examples of rewriting:
    - User says "yeah do that" after you proposed a workout plan -> `{"action": "reroute", "query": "Create a beginner full body workout plan for me."}`
    - User says "what about protein?" after discussing weight loss -> `{"action": "reroute", "query": "How much protein should I eat per day to lose weight?"}`
    - User says "something for my legs" -> `{"action": "reroute", "query": "Can you suggest a leg day workout routine?"}`

2.  **If there is NO clear fitness intent** (e.g., the user is just chatting, saying thanks, asking off-topic questions), you should respond as a warm, friendly fitness assistant. The output MUST be formatted as a JSON object:
    `{"action": "chat", "reply": "Your friendly, conversational response here."}`

    Examples of chatting:
    - User says "thanks!" -> `{"action": "chat", "reply": "You're welcome! Let me know if you have any other fitness questions."}`
    - User says "hello" -> `{"action": "chat", "reply": "Hi there! How can I help you with your fitness goals today?"}`
    - User says "what is the weather like?" -> `{"action": "chat", "reply": "I'm a fitness AI, so I'm best at helping with workouts and nutrition. What can I help you with?"}`

Reply with ONLY the JSON object. Nothing else."""

        print("GeneralAgent created!")

    @property
    def client(self):
        if not hasattr(self, "_client"):
            from agent.config import get_gemini_api_key
            self._client = genai.Client(api_key=get_gemini_api_key())
        return self._client


    def reset(self):
        self.memory = []

    def run(self, user_input):
        self.memory.append({"role": "user", "parts": [{"text": user_input}]})

        history_text = ""
        if len(self.memory) > 1: # Only include history if it exists
            lines = []
            # Use all but the last message (which is the current user_input)
            for msg in self.memory[-7:-1]: 
                role = "User" if msg["role"] == "user" else "Assistant"
                lines.append(f"{role}: {msg['parts'][0]['text']}")
            history_text = "CONVERSATION HISTORY:\n" + "\n".join(lines)

        full_prompt = f"{history_text}\n\nLATEST USER MESSAGE: {user_input}".strip()

        response = self.client.models.generate_content(
            model=self.model,
            contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
            config={"system_instruction": self.system_prompt}
        )
        reply_text = response.candidates[0].content.parts[0].text.strip()

        try:
            # Clean up markdown code block if present
            if reply_text.startswith("```json"):
                reply_text = reply_text[7:-3].strip()

            parsed_reply = json.loads(reply_text)
            action = parsed_reply.get("action")
            
            if action == "reroute":
                return parsed_reply.get("query"), "reroute"
            elif action == "chat":
                return parsed_reply.get("reply", "Sorry, I had trouble with that request."), "general"
        except (json.JSONDecodeError, AttributeError, KeyError):
            # If JSON fails, assume it's a chat response that forgot to use JSON
            return reply_text, "general"

    def add_assistant_reply(self, reply):
        if isinstance(reply, dict) and "final_plan" in reply:
            text_reply = reply["final_plan"]
        else:
            text_reply = str(reply)
        self.memory.append({"role": "model", "parts": [{"text": text_reply}]})