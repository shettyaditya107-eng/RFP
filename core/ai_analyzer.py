import json
import time
import random

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL


SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "business_area": {"type": "string"},
            "requirement_group": {"type": "string"},
            "capability": {"type": "string"},
            "requirement": {"type": "string"},
            "page_number": {"type": "integer"},
            "source_excerpt": {"type": "string"},
            "confidence": {"type": "number"}
        },
        "required": [
            "business_area",
            "requirement_group",
            "capability",
            "requirement",
            "page_number",
            "source_excerpt",
            "confidence"
        ]
    }
}


PROMPT = """
You are an enterprise requirements analyst. Analyze the supplied RFP content.
Extract only requirements explicitly supported by the source.
Organize each item as:
Business Area -> Requirement Group -> Capability -> Requirement.
Do not invent functionality. Remove duplicates. Preserve the original PDF page number.
Include a short supporting source excerpt and a confidence value from 0 to 1.
Return only the requested JSON structure.
"""


def analyze_requirements(pages):
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to the .env file."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    content = PROMPT + "\n\nDOCUMENT:\n"

    for p in pages:
        content += (
            f"\n--- PAGE {p['page_number']} ---\n"
            f"{p['text']}\n"
        )

    # Retry temporary 503 errors
    max_retries = 5

    for attempt in range(max_retries):
        try:
            print(
                f"Calling Gemini model: {GEMINI_MODEL} "
                f"(attempt {attempt + 1}/{max_retries})"
            )

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=content,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SCHEMA
                )
            )

            return json.loads(response.text)

        except Exception as e:
            error_text = str(e)

            # Only retry temporary availability errors
            if "503" not in error_text and "UNAVAILABLE" not in error_text:
                raise

            if attempt == max_retries - 1:
                raise RuntimeError(
                    "Gemini is temporarily unavailable after "
                    f"{max_retries} attempts. Please try again later."
                ) from e

            # Exponential backoff: ~2, 4, 8, 16 seconds
            wait_time = (2 ** (attempt + 1)) + random.uniform(0, 1)

            print(
                f"Gemini returned 503 (temporarily unavailable). "
                f"Retrying in {wait_time:.1f} seconds..."
            )

            time.sleep(wait_time)
