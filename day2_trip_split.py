import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trip Expense Splitter", page_icon="🏔️", layout="centered")

st.title("🏔️ Kulumunali Trip - Split Expenses Fairly")

st.markdown("""
Friends are going on a Kulumunali trip and want to split expenses fairly.  
Add each friend's name and contribution.  
The app will calculate how much each person should pay or get back.
""")

# --- Inputs ---
total_amount = st.number_input("💰 Total Trip Cost", min_value=0.0, step=100.0)
num_people = st.number_input("👥 Number of Friends", min_value=1, step=1)

# Collect contributions
contributions = []
st.subheader("✍️ Enter Each Friend's Name & Contribution")
for i in range(int(num_people)):
    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input(f"Friend {i+1} Name", key=f"name_{i}")
    with col2:
        contrib = st.number_input("Contribution", min_value=0.0, step=50.0, key=f"contrib_{i}")
    if name:
        contributions.append({"Name": name, "Contribution": contrib})

# --- Calculate Fair Share ---
if st.button("💡 Calculate Settlement"):
    if len(contributions) != num_people:
        st.error("Please enter all friends' names and contributions.")
    else:
        df = pd.DataFrame(contributions)
        fair_share = total_amount / num_people
        df["Fair Share"] = fair_share
        df["Balance"] = df["Contribution"] - fair_share

        st.subheader("📊 Settlement Summary")
        st.dataframe(df)

        for _, row in df.iterrows():
            if row["Balance"] < 0:
                st.write(f"👉 {row['Name']} should **pay {-row['Balance']:.2f} more**.")
            elif row["Balance"] > 0:
                st.write(f"✅ {row['Name']} should **get back {row['Balance']:.2f}**.")
            else:
                st.write(f"👌 {row['Name']} is settled.")

        # Total check
        total_contrib = df["Contribution"].sum()
        if total_contrib != total_amount:
            st.warning(f"⚠️ Total contributions ({total_contrib:.2f}) do not match trip cost ({total_amount:.2f}).")
