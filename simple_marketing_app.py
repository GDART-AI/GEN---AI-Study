import streamlit as st

st.title("📱 Simple Instagram Planner")
st.write("This is a basic demo app for digital marketing content ideas.")

# Input
brand_name = st.text_input("Enter your Brand/Niche (e.g., AI Vibe Marketing):")

if st.button("Generate Plan"):
    if brand_name.strip() == "":
        st.warning("Please enter your brand/niche!")
    else:
        st.success(f"✨ Sample Content Plan for: {brand_name}")

        # 1. Post Topics
        st.subheader("📌 5 Instagram Post Topics")
        topics = [
            f"Why {brand_name} is unique",
            f"3 Tips to grow in {brand_name}",
            f"Behind the scenes of {brand_name}",
            f"Customer story about {brand_name}",
            f"Future trends in {brand_name}"
        ]
        for t in topics:
            st.write("✔️", t)

        # 2. Captions
        st.subheader("✍️ Sample Captions")
        for t in topics:
            st.text(f"🔥 {t} — Follow us for more {brand_name} updates! 🚀")

        # 3. Hashtags
        st.subheader("🔖 Hashtag Suggestions")
        st.write(f"#DigitalMarketing #{brand_name.replace(' ', '')} #SocialMedia #Growth #Trending")
