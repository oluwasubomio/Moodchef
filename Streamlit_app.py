import streamlit as st
from dotenv import load_dotenv
import os
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

# Create or load chat session from Streamlit state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

st.set_page_config(page_title="MoodChef 🍜", layout="centered")
st.title("🥣 MoodChef – Your Food Mood Matchmaker")
st.markdown("🧊 What’s in Your Fridge?")
st.write("""
To help you relax and get a personalized meal suggestion,  
**please list everything you currently have in your fridge or kitchen.**  
That includes vegetables, proteins, snacks, drinks — even leftovers!

_The more details you give, the better I can suggest a mood-boosting Nigerian meal for you!
""")

# User mood input
user_mood = st.text_input("Describe your mood:", placeholder="e.g., I feel a little anxious and drained")

# New: Fridge input
fridge_contents = st.text_area("What's in your fridge or kitchen?", placeholder="e.g., rice, tomatoes, eggs, sardines, yam, leftover stew")

if st.button("Get Recommendation") and user_mood and fridge_contents:
    # Create MoodRequest and build prompt
    mood_request = MoodRequest(user_mood=user_mood)
    
    # Add fridge content to the prompt building logic
    full_prompt = build_prompt(mood_request.user_mood, fridge_contents)

    with st.spinner("Cooking up something tasty..."):
        # Use the chat object to send and retain conversation
        response = st.session_state.chat.send_message(full_prompt)
        result = parse_moodchef_response(response.text)
        mood_response = MoodResponse(suggestion=result, encouragement="Enjoy your meal!")

        # Display result
        st.success("Here's what MoodChef recommends:")
        st.markdown(f"**{mood_response.suggestion}**")

        # Optional: show chat history 
        with st.expander("Chat History"):
            for msg in st.session_state.chat.history:
                st.markdown(f"**{msg.role.capitalize()}:** {msg.parts[0].text}")

# GitHub link
st.markdown("---")
st.markdown("[📂 View on GitHub](https://github.com/oluwasubomio/moodchef)")
