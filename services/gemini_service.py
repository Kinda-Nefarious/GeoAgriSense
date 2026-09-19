from __future__ import annotations

import os

from google import genai


def ask_gemini(question: str) -> dict:
    """
    Send an agricultural question to Gemini.

    API failures are converted into controlled responses
    so that the Streamlit application does not crash.
    """

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    if not api_key:
        return {
            "ok": False,
            "message": "Gemini is not configured. Add GEMINI_API_KEY to .env.",
            "technical_detail": "GEMINI_API_KEY was not found.",
        }

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=model,
            contents=(
                "You are GeoAgriSense, an agricultural crop-scouting assistant. "
                "Provide practical, concise and cautious advice for farmers. "
                "Do not claim to diagnose crop disease from text alone. "
                "Encourage physical inspection when appropriate. "
                f"Farmer question: {question}"
            ),
        )

        text = getattr(response, "text", None)

        if not text:
            return {
                "ok": False,
                "message": "Gemini returned no usable response. Please try again.",
                "technical_detail": (
                    "The Gemini response did not contain response.text."
                ),
            }

        return {
            "ok": True,
            "text": text,
        }

    except Exception as exc:
        message = str(exc)
        lowered = message.lower()

        # Temporary Gemini availability problem
        if (
            "503" in lowered
            or "unavailable" in lowered
            or "high demand" in lowered
        ):
            return {
                "ok": False,
                "message": (
                    "Gemini is temporarily unavailable. "
                    "Please try again in a moment."
                ),
                "technical_detail": message,
            }

        # Invalid/non-existent model
        if "404" in lowered or "not_found" in lowered:
            return {
                "ok": False,
                "message": (
                    f"The configured Gemini model '{model}' "
                    "is not available. Check GEMINI_MODEL in .env."
                ),
                "technical_detail": message,
            }

        # Authentication
        if (
            "401" in lowered
            or "403" in lowered
            or "permission" in lowered
        ):
            return {
                "ok": False,
                "message": (
                    "Gemini authentication or permission failed. "
                    "Check the API key."
                ),
                "technical_detail": message,
            }

        return {
            "ok": False,
            "message": "Gemini could not complete the request.",
            "technical_detail": message,
        }