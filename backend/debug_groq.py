import os
import sys

print(f"Python Executable: {sys.executable}")
print("Attempting to import groq...")

try:
    from groq import Groq
    print("SUCCESS: Groq module imported.")
except ImportError as e:
    print(f"ERROR: Could not import groq. {e}")
    sys.exit(1)

API_KEY = os.getenv("GROQ_API_KEY", "YOUR_API_KEY_HERE")

try:
    print("Initializing Client...")
    client = Groq(api_key=API_KEY)
    
    print("Testing API Call...")
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print(f"SUCCESS: API Responded: {completion.choices[0].message.content}")

except Exception as e:
    print(f"ERROR: API Call Failed. {e}")
