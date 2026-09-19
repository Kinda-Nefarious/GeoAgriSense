import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class GeminiService:
    """
    Gemini integration for GeoAgriSense.

    Gemini is used for:
    1. Agricultural Q&A
    2. Multimodal crop-image analysis
    3. Context-aware analysis of field observations
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash",
        )

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def ask(self, question):
        prompt = f"""
You are GeoAgriSense, an agricultural decision-support
assistant.

Help a farmer or field scout understand the following question:

{question}

Provide:
- likely explanations
- what should be checked in the field
- practical next steps
- important limitations

Do not present an uncertain diagnosis as fact.
"""

        return self._generate(prompt)

    def analyze_observation(
        self,
        image_bytes,
        mime_type,
        observation,
    ):
        """
        Analyze a crop photograph using Gemini with
        geospatial/scouting context.
        """

        crop = observation.get("crop", "Unknown")
        block = observation.get("block_id", "Unknown")
        symptom = observation.get(
            "symptom",
            observation.get("observation", "Unknown"),
        )
        severity = observation.get(
            "severity",
            "Unknown",
        )
        date = observation.get(
            "date",
            observation.get("observed_at", "Unknown"),
        )
        notes = observation.get(
            "notes",
            "No additional notes.",
        )

        latitude = observation.get(
            "latitude",
            "Unknown",
        )

        longitude = observation.get(
            "longitude",
            "Unknown",
        )

        prompt = f"""
You are the multimodal agricultural intelligence component
of GeoAgriSense.

A field scout captured the attached crop photograph.

FIELD CONTEXT
-------------
Crop: {crop}
Block: {block}
Reported symptom: {symptom}
Reported severity: {severity}
Observation date: {date}
Latitude: {latitude}
Longitude: {longitude}
Scout notes: {notes}

Analyze the photograph together with this field context.

Return a practical scouting report using exactly these sections:

## Visual observations

Describe only what can reasonably be seen.

## Crop condition

Give an overall assessment.

## Possible causes

List plausible causes, but do not claim certainty.

## Risk assessment

Classify the apparent risk as:
LOW, MEDIUM, or HIGH.

Explain the reasoning.

## Recommended field checks

List specific checks the farmer/scout should perform.

## Recommended next action

Give practical next steps.

## Limitations

Explain what cannot reliably be determined from one photograph.

This is decision support, not a definitive plant disease diagnosis.
"""

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

        return self._generate(
            [
                image_part,
                prompt,
            ]
        )

    def analyze_crop_image(
        self,
        image_bytes,
        mime_type,
        crop="Unknown",
        location="Unknown",
        additional_context="",
    ):
        """Generic crop-image analysis."""

        observation = {
            "crop": crop,
            "block_id": location,
            "symptom": "General crop condition",
            "severity": "Unknown",
            "notes": additional_context,
        }

        return self.analyze_observation(
            image_bytes,
            mime_type,
            observation,
        )

    def _generate(self, contents):

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
            )

            if not response.text:
                return "Gemini returned an empty response."

            return response.text

        except Exception as exc:

            message = str(exc)

            if "503" in message or "UNAVAILABLE" in message:
                return (
                    "Gemini is temporarily unavailable because "
                    "the selected model is experiencing high demand. "
                    "Please try again shortly."
                )

            if "404" in message or "NOT_FOUND" in message:
                return (
                    f"The Gemini model '{self.model}' is unavailable "
                    "for this API configuration."
                )

            return f"Gemini request failed: {message}"