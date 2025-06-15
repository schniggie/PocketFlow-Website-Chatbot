from google import genai
import os

def call_llm(prompt: str) -> str:
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY", ""),
    )
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-04-17")
    response = client.models.generate_content(model=model, contents=[prompt])
    return response.text

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"

    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")