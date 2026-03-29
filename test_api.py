import os
from dotenv import load_dotenv
from google import genai

# Load your .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Checking API Key... (Starts with: {str(api_key)[:5]}...)")

try:
    client = genai.Client(api_key=api_key)
    print("Sending test message to Gemini...")
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with exactly one word: 'Success'"
    )
    
    print(f"Response received: {response.text}")
    print("✅ YOUR API KEY IS WORKING PERFECTLY!")

except Exception as e:
    print(f"❌ API FAILED. Here is the exact reason:")
    print(e)