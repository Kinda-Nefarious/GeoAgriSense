import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class GeminiService:
    """
    GeoAgriSense Gemini service.

    Provides:
    - agricultural text Q&A
    - crop-image analysis
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured in the .env file."
            )

        self.client = genai.Client(api_key=self.api_key)

    def ask(self, question: str) -> str:
        """
        Ask Gemini an agricultural/scouting question.
        """

        prompt = f"""
You are GeoAgriSense, an agricultural decision-support assistant.

Your role is to help farmers and agricultural field scouts interpret
crop observations and make practical scouting decisions.

Question:
{question}

Provide a concise, practical answer suitable for a farmer or field scout.

Where appropriate:
- identify possible causes
- explain what should be checked in the field
- recommend practical next steps
- distinguish observation from certainty
- do not claim a disease diagnosis unless the available evidence supports it
"""

        return self._generate(prompt)

    def analyze_crop_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        crop: str = "Unknown crop",
        location: str = "Unknown field location",
        additional_context: str = "",
    ) -> str:
        """
        Analyze a crop photograph using Gemini vision capabilities.
        """

        prompt = f"""
You are the AI crop-scanning component of GeoAgriSense.

Analyze the supplied photograph of a crop.

Known context:
Crop: {crop}
Field/location: {location}
Additional scout context: {additional_context or "None provided"}

Produce a practical agricultural scouting report with these sections:

## 1. Visual observations
Describe what is visibly present in the photograph.

## 2. Crop condition
Give an overall assessment of the apparent crop condition.

## 3. Possible causes
Identify plausible causes of the observed symptoms.
Do not present a possibility as a confirmed diagnosis.

## 4. Risk level
Classify the apparent field risk as:
LOW, MEDIUM, or HIGH.

Explain why.

## 5. Recommended field checks
Give specific things a farmer/scout should inspect next.

## 6. Recommended action
Give practical immediate actions, prioritising:
- containment where appropriate
- monitoring
- irrigation/nutrition checks
- pest scouting
- disease confirmation
- escalation to an agricultural specialist where necessary

## 7. Confidence and limitations
Explain what cannot reliably be determined from a single photograph.

Important:
This is agricultural decision support, not a definitive plant disease diagnosis.
Base conclusions only on visible evidence and the provided context.
"""

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

        return self._generate(
            contents=[
                image_part,
                prompt,
            ]
        )

    def _generate(self, contents) -> str:
        """
        Generate a Gemini response.

        Uses the configured model and provides a clean error for temporary
        Gemini service outages.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
            )

            if not response.text:
                return "Gemini returned an empty response."

            return response.text

        except Exception as exc:
            error_text = str(exc)

            if "503" in error_text or "UNAVAILABLE" in error_text:
                return (
                    "Gemini is temporarily unavailable because the selected "
                    "model is experiencing high demand. Please try again "
                    "shortly."
                )

            if "404" in error_text or "NOT_FOUND" in error_text:
                return (
                    f"The configured Gemini model '{self.model}' is not "
                    "currently available to this API key."
                )

            return f"Gemini request failed: {error_text}"