def parse_moodchef_response(gemini_text: str) -> str:
    return gemini_text.strip().replace("MoodChef:", "").strip()
