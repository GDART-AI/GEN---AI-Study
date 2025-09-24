import streamlit as st
import random
import pyttsx3
import speech_recognition as sr

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Quiz Game App", page_icon="🧠", layout="centered")

# ------------------- CUSTOM CSS -------------------
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #000000, #1a1a1a, #0d0d0d);
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .stButton button {
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        color: white;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 18px;
        font-weight: bold;
        border: none;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #ff4b2b, #ff416c);
        color: black;
    }
    .question {
        font-size: 22px;
        font-weight: bold;
        color: #ffcc00;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------- QUIZ QUESTIONS -------------------
all_quiz_data = [
    {"question": "Which is the largest planet in our solar system?",
     "options": ["Earth", "Mars", "Jupiter", "Saturn"], "answer": "Jupiter"},
    {"question": "Who wrote the play Romeo and Juliet?",
     "options": ["William Wordsworth", "William Shakespeare", "Leo Tolstoy", "Mark Twain"], "answer": "William Shakespeare"},
    {"question": "What is the capital of France?",
     "options": ["Berlin", "Madrid", "Paris", "Rome"], "answer": "Paris"},
    {"question": "Which gas do plants absorb from the atmosphere?",
     "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Helium"], "answer": "Carbon Dioxide"},
    {"question": "Which is the fastest land animal?",
     "options": ["Cheetah", "Lion", "Horse", "Leopard"], "answer": "Cheetah"},
    {"question": "Who developed the theory of relativity?",
     "options": ["Isaac Newton", "Albert Einstein", "Galileo Galilei", "Nikola Tesla"], "answer": "Albert Einstein"},
]

# ------------------- SESSION STATE INIT -------------------
if "quiz_data" not in st.session_state:
    # shuffle once per session
    st.session_state.quiz_data = random.sample(all_quiz_data, len(all_quiz_data))
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "completed" not in st.session_state:
    st.session_state.completed = False

# ------------------- QUIZ LOGIC -------------------
def normalize(text: str) -> str:
    return text.strip().lower()

def next_question(selected_option):
    current_q = st.session_state.quiz_data[st.session_state.q_index]
    if selected_option and normalize(selected_option) == normalize(current_q["answer"]):
        st.session_state.score += 1
    st.session_state.q_index += 1
    if st.session_state.q_index >= len(st.session_state.quiz_data):
        st.session_state.completed = True

# ------------------- TEXT TO SPEECH -------------------
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    engine.say(text)
    engine.runAndWait()

# ------------------- SPEECH TO TEXT -------------------
def listen_answer():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("🎙️ Listening... Please speak now.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        response = recognizer.recognize_google(audio)
        return response
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

# ------------------- MAIN APP -------------------
st.title("🧠 Quiz Game App")
st.markdown("### Test your knowledge & have fun!")

if not st.session_state.completed:
    current_q = st.session_state.quiz_data[st.session_state.q_index]
    st.markdown(f"<p class='question'>Q{st.session_state.q_index+1}: {current_q['question']}</p>", unsafe_allow_html=True)

    # Show options
    option = st.radio("Choose your answer:", current_q["options"], index=None)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 Read Question"):
            q_text = current_q["question"] + " Options are: " + ", ".join(current_q["options"])
            speak_text(q_text)

    with col2:
        if st.button("🎙️ Answer with Voice"):
            voice_ans = listen_answer()
            if voice_ans:
                st.write(f"👉 You said: **{voice_ans}**")

                # Fuzzy match voice to option
                matched_option = None
                for opt in current_q["options"]:
                    if normalize(opt) in normalize(voice_ans):
                        matched_option = opt
                        break

                if matched_option:
                    st.success(f"✅ Voice matched: {matched_option}")
                    next_question(matched_option)   # move to next question
                else:
                    st.warning("⚠️ Couldn't match your voice with the given options. Try again.")
            else:
                st.warning("⚠️ Sorry, I couldn't hear you clearly.")

    if st.button("Submit Answer"):
        if option:
            next_question(option)
        else:
            st.warning("Please select an option before submitting!")

else:
    st.subheader("🎉 Quiz Completed! 🎉")
    score = st.session_state.score
    total = len(st.session_state.quiz_data)
    st.success(f"Your final score: {score}/{total}")

    # Encouragement
    if score == total:
        st.balloons()
        st.markdown("🌟 **Perfect Score! You’re a Quiz Master! 🏆**")
        speak_text("Congratulations! You got a perfect score!")
    elif score >= total/2:
        st.snow()
        st.markdown("👏 **Great Job! Keep improving.** 💪")
        speak_text("Well done! You did a great job.")
    else:
        st.markdown("💡 **Don’t worry, try again and you’ll do better! 🚀**")
        speak_text("Good try! Practice more and you'll improve.")

    if st.button("Play Again 🔄"):
        st.session_state.quiz_data = random.sample(all_quiz_data, len(all_quiz_data))
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.completed = False
