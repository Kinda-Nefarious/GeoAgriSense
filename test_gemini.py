import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from .env"
    )


print("API key loaded: OK")
print(f"Testing model: {model}")


client = genai.Client(api_key=api_key)

print("Gemini client created: OK")


try:

    response = client.models.generate_content(
        model=model,
        contents=(
            "In one sentence, explain why regular "
            "crop scouting is important."
        ),
    )

    print()
    print("Gemini response:")
    print(response.text)

except Exception as exc:

    print()
    print("Gemini request failed:")
    print(exc)