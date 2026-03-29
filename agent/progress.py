import os
from dotenv import load_dotenv
from google import genai
from firebase_admin import firestore

load_dotenv()

class ProgressAgent:
    def __init__(self, db_client):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
        self.db = db_client # We pass the Firebase connection in here!
        
        self.system_prompt = """You are an analytical fitness coach. 
        You will receive a list of the user's logged activities for the past week.
        
        Your task is to analyze this data and provide a brief, structured summary:
        1. 🌟 **The Win:** Identify one positive trend or accomplishment based on their logs.
        2. 📉 **The Slip:** Identify one area where they might be falling short (e.g., missed days, low protein).
        3. 🚀 **Next Week's Goal:** Give a highly specific, one-sentence actionable goal for next week.
        
        Keep it encouraging but strictly data-driven. Do not invent data. If the logs are empty, encourage them to start tracking.
        """
        print("ProgressAgent created!")

    def fetch_weekly_data(self, username):
        """Pulls the most recent logs for a specific user from Firebase."""
        try:
            
            logs_ref = self.db.collection("users").document(username).collection("daily_logs")

            recent_logs = logs_ref.order_by("date", direction=firestore.Query.DESCENDING).limit(10).stream()
            
            log_text = "USER'S RECENT LOGS:\n"
            count = 0
            for log in recent_logs:
                data = log.to_dict()
                log_text += f"- Date: {data.get('date', 'Unknown')}, Category: {data.get('category', 'Unknown')}, Details: {data}\n"
                count += 1
                
            if count == 0:
                return "No logs found for this user."
            return log_text
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return "Error retrieving data."

    def run_analysis(self, username):
        """Fetches data and sends it to the LLM for analysis."""
        weekly_data_string = self.fetch_weekly_data(username)
        
        if "No logs found" in weekly_data_string or "Error" in weekly_data_string:
             return f"I couldn't find enough logged data to run an analysis yet. Start logging your workouts and meals in the sidebar!"
        
       
        prompt = f"Analyze the following data for user '{username}':\n\n{weekly_data_string}"
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
                config={"system_instruction": self.system_prompt}
            )
            return response.candidates[0].content.parts[0].text
        except Exception as e:
            return f"Error running analysis: {e}"