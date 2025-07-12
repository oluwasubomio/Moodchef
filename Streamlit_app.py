import streamlit as st
from dotenv import load_dotenv
import os
import re

from Models.mood_models import MoodRequest, MoodResponse
from Prompts.prompts import build_prompt
from Gemini.gemini_service import parse_moodchef_response
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Create or load chat session
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Page setup
st.set_page_config(page_title="MoodChef 🍜", layout="centered")
st.title("🥣 MoodChef – Your Food Mood Matchmaker")
st.markdown("🧊 What’s in Your Fridge?")
st.write("""
MoodChef helps you match your feelings with the perfect meal!
Type how you're feeling and what ingredients you have. Get cheerful, comforting food suggestions — safe, evidence-based, and personalized just for your mood.
""")

# Mood input
user_mood = st.text_input("Describe your mood:", placeholder="e.g., I feel tired and stressed")

# Mood validation
VALID_MOODS = [
    "happy", "sad", "stressed", "tired", "angry", "anxious",
    "romantic", "lazy", "excited", "bored", "lonely", "calm", "overwhelmed"
]
mood_matched = any(mood in user_mood.lower() for mood in VALID_MOODS)
if user_mood and not mood_matched:
    st.error("Please enter a valid mood like 'happy', 'sad', 'tired', or 'anxious'.")
    st.stop()

# Fridge input
fridge_contents = st.text_area("What's in your fridge or kitchen?", placeholder="e.g., rice, beans, tomatoes, sardines")

COMMON_FOODS = {
    "rice", "beans", "tomato", "pepper", "onions", "chicken", "egg", "milk", "bread",
    "apple", "banana", "yam", "plantain", "butter", "cheese", "sardine", "carrot",
    "cabbage", "spinach", "fish", "meat", "pasta", "corn", "oil", "salt", "maggi", "pap"
}

# Clean and validate fridge items
fridge_items = [item.strip().lower() for item in fridge_contents.split(",") if item.strip()]
invalid_items = [
    item for item in fridge_items 
    if item not in COMMON_FOODS and not re.search(r"\b(egg|rice|meat|fish|yam|oil|fruit|veg|leftover|spice)\b", item)
]

if invalid_items:
    st.warning(f"The following items are not recognized as food: {', '.join(invalid_items)}")
    st.info("Please list common foods like rice, tomato, eggs, chicken, stew, etc.")

# Main button logic
if st.button("Get Recommendation") and user_mood and fridge_contents and not invalid_items:
    # Step 1: Create request
    mood_request = MoodRequest(user_mood=user_mood)

    # Step 2: Build prompt using your prompt builder
    full_prompt = build_prompt(mood_request.user_mood, fridge_contents)

    # Step 3: Send to Gemini
    with st.spinner("Cooking up something tasty..."):
        response = st.session_state.chat.send_message(full_prompt)
        result = parse_moodchef_response(response.text)
        mood_response = MoodResponse(suggestion=result, encouragement="Enjoy your meal!")

        # Step 4: Show result
        st.success("Here's what MoodChef recommends:")
        st.markdown(f"**{mood_response.suggestion}**")

        # Optional: Show chat history
        with st.expander("Chat History"):
            for msg in st.session_state.chat.history:
                st.markdown(f"**{msg.role.capitalize()}:** {msg.parts[0].text}")

# GitHub footer
st.markdown("---")
st.markdown("[📂 View on GitHub](https://github.com/oluwasubomio/moodchef)")
