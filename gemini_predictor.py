import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_risk_reason(city, area, crime):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(
            f"Explain crime risk for {crime} in {area}, {city} in simple terms."
        )
        return response.text
    except Exception as e:
        return "AI risk explanation unavailable"
