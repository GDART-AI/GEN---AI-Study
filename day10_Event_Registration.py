import streamlit as st
import pandas as pd

st.set_page_config(page_title="Event Registration ", layout="centered")

st.title(" Event Registration ")

# Initialize session state
if "registrations" not in st.session_state:
    st.session_state["registrations"] = []

# Registration Form
with st.form("registration_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    event_choice = st.selectbox("Choose Event", ["Workshop on AI", "Digital Marketing Bootcamp", "Startup Networking", "Hackathon 2025"])

    submit = st.form_submit_button("Register")

    if submit:
        if name and email:
            st.session_state["registrations"].append({
                "Name": name,
                "Email": email,
                "Event": event_choice
            })
            st.success(f"✅ {name} registered successfully for {event_choice}!")
        else:
            st.error("⚠️ Please fill all fields before submitting.")

# Convert to DataFrame
if st.session_state["registrations"]:
    df = pd.DataFrame(st.session_state["registrations"])
    df.index = df.index + 1  # ✅ Start serial number from 1

    st.subheader("📋 Current Registrations")
    st.dataframe(df)

    st.write(f"**Total Registrations:** {len(df)}")

    # Export CSV
    csv = df.to_csv(index=True).encode('utf-8')
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="event_registrations.csv",
        mime="text/csv",
    )
