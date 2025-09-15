import streamlit as st

st.title("Day 1 - Greeting Form 🎉")

# Input fields
name = st.text_input("Enter your name")
age = st.slider("Select your age", 1, 100, 18)

# Show custom welcome message
if name:
    st.write(f"👋 Welcome to G DART, {name}! You are {age} years old.")
