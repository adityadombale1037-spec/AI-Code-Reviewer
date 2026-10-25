import os
from google import genai

# Get API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found.")
else:
    try:
        # Create Gemini client
        client = genai.Client(api_key=api_key)

        print("Testing Gemini API...")

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents="Explain Python ZeroDivisionError in simple English in 2 sentences."
        )

        print("\nGemini AI Response:")
        print(response.text)

        print("\nSUCCESS: Gemini API is working!")

    except Exception as e:
        print("\nGemini API Error:")
        print(e)