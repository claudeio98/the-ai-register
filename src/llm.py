import os
from openai import OpenAI

# Using the key found in the system logs
OPENROUTER_API_KEY = "OPENROUTER_API_KEY_REMOVED"

# Configure OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "AI Events Intelligence Pipeline",
    }
)

def query_llm(system_prompt, user_prompt, response_format="text"):
    """Generic helper to query the LLM via OpenRouter."""
    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "google/gemma-4-31b-it"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} if response_format == "json" else None
        )
        content = response.choices[0].message.content
        return content
    except Exception as e:
        print(f"LLM Error: {e}")
        return None
