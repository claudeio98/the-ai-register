import os
from openai import OpenAI

_client = None


def get_client():
    """Lazily initialize and return the OpenRouter client.
    This avoids OpenAI import errors at module load time when
    OPENROUTER_API_KEY is not set (e.g., in test environments).
    """
    global _client
    if _client is None:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            print("Warning: OPENROUTER_API_KEY not set in environment")
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "AI Events Intelligence Pipeline",
            }
        )
    return _client


def query_llm(system_prompt, user_prompt, response_format="text"):
    """Generic helper to query the LLM via OpenRouter."""
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "deepseek/deepseek-v4-flash"),
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
