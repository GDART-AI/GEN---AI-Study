import streamlit as st
import random
import datetime

# ---------- Helper Data ----------
default_times = ["10:00 AM", "1:00 PM", "6:00 PM", "9:00 PM"]

hashtags_bank = {
    "marketing": ["#DigitalMarketing", "#MarketingTips", "#SocialMediaGrowth", "#MarketingStrategy", "#BrandGrowth"],
    "ai": ["#AI", "#ArtificialIntelligence", "#FutureOfAI", "#TechTrends", "#AITools"],
    "fashion": ["#Fashion", "#OOTD", "#StyleInspo", "#TrendAlert", "#Fashionista"],
    "food": ["#Foodie", "#Tasty", "#FoodPhotography", "#Homemade", "#Yummy"]
}

# ---------- Streamlit App ----------
st.title("📱 Digital Marketing Content Planner")
st.write("Generate 1-month Instagram strategy in a single click 🚀")

# Input
brand_name = st.text_input("Enter your Brand/Niche (e.g., AI Vibe Marketing, Food Blog, Fashion Brand):")

if st.button("Generate Plan"):
    if brand_name.strip() == "":
        st.warning("Please enter your brand/niche!")
    else:
        st.success(f"✨ Content plan generated for: {brand_name}")

        # 1. Instagram Post Topics
        st.subheader("📌 30 Instagram Post Topics")
        topics = [f"Day {i+1}: {brand_name} - Post Idea {i+1}" for i in range(30)]
        for t in topics:
            st.write("✔️", t)

        # 2. Content Calendar Planner
        st.subheader("📅 Content Calendar Planner")
        today = datetime.date.today()
        calendar = []
        for i, topic in enumerate(topics):
            post_date = today + datetime.timedelta(days=i)
            time_slot = random.choice(default_times)
            calendar.append((post_date, time_slot, topic))

        for date, time, topic in calendar:
            st.write(f"🗓️ {date} at {time} → {topic}")

        # 3. Instagram Post Caption Generator
        st.subheader("✍️ Auto-Generated Captions")
        for i, topic in enumerate(topics):
            caption = f"🔥 {topic} — Stay tuned for more insights from {brand_name}! 🚀 #GrowthMindset"
            st.write(f"**{topic}**")
            st.text(caption)

        # 4. Hashtag Suggester
        st.subheader("🔖 Hashtag Suggestions")
        niche = brand_name.lower()
        chosen_tags = []
        for key, tags in hashtags_bank.items():
            if key in niche:
                chosen_tags = tags
                break
        if not chosen_tags:
            chosen_tags = ["#Business", "#Success", "#Motivation", "#Growth", "#Trending"]

        st.write("Here are suggested hashtags you can mix with each post:")
        st.write(" ".join(chosen_tags))
