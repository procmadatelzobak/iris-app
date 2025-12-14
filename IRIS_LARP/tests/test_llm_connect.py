import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import app modules if needed, 
# but for this standalone test we'll try to keep imports minimal or direct.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_google():
    print("\n--- Testing Google (Gemini Native) ---")
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("❌ GEMINI_API_KEY not found in env")
        return
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-pro') 
        # Just a simple generation or listing models
        # Listing models is safer/cheaper to verify auth
        print("Authenticating...")
        # response = model.generate_content("Hello")
        # print(f"✅ Response received: {response.text[:20]}...")
        # Actually list_models is better 
        count = 0
        for m in genai.list_models():
            count += 1
            if count > 0: break
        print(f"✅ Google Auth Successful (Found {count}+ models)")
    except Exception as e:
        print(f"❌ Google Error: {e}")

def test_openrouter():
    print("\n--- Testing OpenRouter ---")
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        print("❌ OPENROUTER_API_KEY not found in env")
        return

    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
        )
        
        print("Listing available models on OpenRouter...")
        try:
            models = client.models.list()
            print(f"✅ OpenRouter Auth Successful (Found {len(models.data)} models)")
            
            # Print first 5 models to debug ID format
            print("Examples:")
            for m in models.data[:5]:
                print(f" - {m.id}")
                
            # Try to find a google model
            google_models = [m.id for m in models.data if 'gemini' in m.id.lower()][:3]
            if google_models:
                print(f"Found Gemini models: {google_models}")
                test_model = google_models[0]
            else:
                test_model = "mistralai/mistral-7b-instruct:free"

            print(f"Sending request to {test_model}...")
            completion = client.chat.completions.create(
                model=test_model,
                messages=[
                    {"role": "user", "content": "Say 'OK' if you hear me."}
                ]
            )
            print(f"✅ OpenRouter Response ({test_model}): {completion.choices[0].message.content}")

        except Exception as e:
            print(f"❌ OpenRouter Error: {e}")
            
    except Exception as e:
        print(f"❌ OpenRouter Setup Error: {e}")

def test_openai():
    print("\n--- Testing OpenAI ---")
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("❌ OPENAI_API_KEY not found in env")
        return

    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        print("Sending request to gpt-3.5-turbo...")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'OK' if you hear me."}
            ]
        )
        print(f"✅ OpenAI Response: {completion.choices[0].message.content}")
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")

if __name__ == "__main__":
    print(f"Loading env from: {os.path.join(os.path.dirname(__file__), '..', '.env')}")
    test_google()
    test_openrouter()
    test_openai()
