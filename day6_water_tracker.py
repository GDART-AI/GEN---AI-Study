# day6_water_tracker.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
import os

# -------------------------
# Config
# -------------------------
DATA_FILE = "water_data.csv"  # saved in current working directory
DEFAULT_GOAL_LITERS = 3.0

st.set_page_config(page_title="💧 Water Intake Tracker", page_icon="💧", layout="wide")

# -------------------------
# Helpers
# -------------------------
def load_data(filepath=DATA_FILE):
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath, parse_dates=["date"])
            df = df[["date", "ml"]]
            df["date"] = pd.to_datetime(df["date"]).dt.date
            return df
        except Exception:
            return pd.DataFrame(columns=["date", "ml"])
    else:
        return pd.DataFrame(columns=["date", "ml"])

def save_data(df, filepath=DATA_FILE):
    df_to_save = df.copy()
    df_to_save["date"] = pd.to_datetime(df_to_save["date"]).dt.strftime("%Y-%m-%d")
    df_to_save.to_csv(filepath, index=False)

def add_entry(df, entry_date: date, ml: int):
    entry = pd.DataFrame([{"date": entry_date, "ml": int(ml)}])
    if df is None or df.empty:
        new_df = entry
    else:
        new_df = pd.concat([df, entry], ignore_index=True)
    # aggregate same-day entries
    new_df["date"] = pd.to_datetime(new_df["date"]).dt.date
    agg = new_df.groupby("date", as_index=False)["ml"].sum()
    return agg

def get_last_n_days_df(df, n=7, end_date: date = None):
    if end_date is None:
        end_date = date.today()
    start = end_date - timedelta(days=n-1)
    dates = pd.DataFrame({"date": [start + timedelta(days=i) for i in range(n)]})
    if df is None or df.empty:
        merged = dates.merge(pd.DataFrame(columns=["date","ml"]), on="date", how="left")
        merged["ml"] = merged["ml"].fillna(0).astype(int)
    else:
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"]).dt.date
        agg = df_copy.groupby("date", as_index=False)["ml"].sum()
        merged = dates.merge(agg, on="date", how="left")
        merged["ml"] = merged["ml"].fillna(0).astype(int)
    return merged

def ml_to_l(ml):
    return ml / 1000.0

def l_to_ml(l):
    return int(round(l * 1000))

# -------------------------
# App UI
# -------------------------
st.title("💧 Water Intake Tracker")
st.markdown("Log your water intake, track progress toward a daily goal, and view a 7-day hydration chart.")

# Load or initialize data
data = load_data()

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    goal_liters = st.number_input("Daily Goal (liters)", min_value=0.25, max_value=10.0, value=float(DEFAULT_GOAL_LITERS), step=0.25, format="%.2f")
    persist = st.checkbox("Persist data to CSV file", value=True, help="If unchecked, data will only be stored in memory for this session.")
    st.markdown("---")
    st.write("Actions")
    if st.button("Export CSV"):
        if data is None or data.empty:
            st.info("No data to export.")
        else:
            try:
                save_data(data)
                st.success(f"Data saved to `{DATA_FILE}` in this working directory.")
            except Exception as e:
                st.error(f"Failed to save CSV: {e}")

    # Reset flow: click once to "arm" reset, then confirm with a second button
    if "confirm_reset" not in st.session_state:
        st.session_state["confirm_reset"] = False

    if st.session_state["confirm_reset"]:
        st.warning("Click 'Confirm Reset' to permanently delete all stored data (CSV will be removed).")
        if st.button("Confirm Reset"):
            data = pd.DataFrame(columns=["date", "ml"])
            if os.path.exists(DATA_FILE):
                try:
                    os.remove(DATA_FILE)
                except Exception as e:
                    st.error(f"Could not remove {DATA_FILE}: {e}")
            st.success("All data removed.")
            st.session_state["confirm_reset"] = False
    else:
        if st.button("Reset All Data"):
            st.session_state["confirm_reset"] = True

# Main input area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Log Intake")
    entry_date = st.date_input("Date", value=date.today(), key="entry_date")

    # Preset buttons set session_state value for input convenience
    preset_cols = st.columns([1,1,1,1])
    if preset_cols[0].button("200 ml"):
        st.session_state["amount_input"] = 200
    if preset_cols[1].button("250 ml"):
        st.session_state["amount_input"] = 250
    if preset_cols[2].button("500 ml"):
        st.session_state["amount_input"] = 500
    if preset_cols[3].button("1 L"):
        st.session_state["amount_input"] = 1000

    amount_unit = st.radio("Unit", options=["ml", "liters"], index=0, horizontal=True, key="unit_radio")
    default_amt = st.session_state.get("amount_input", 250)
    if amount_unit == "ml":
        amount = st.number_input("Amount", min_value=0, value=int(default_amt), step=50, format="%d", key="amount_ml")
        ml_value = int(amount)
    else:
        amount_l = st.number_input("Amount (L)", min_value=0.0, value=default_amt/1000.0, step=0.1, format="%.2f", key="amount_l")
        ml_value = l_to_ml(amount_l)

    if st.button("Add Intake"):
        if ml_value <= 0:
            st.error("Please enter an amount greater than zero.")
        else:
            data = add_entry(data, entry_date, ml_value)
            if persist:
                try:
                    save_data(data)
                    st.success(f"Added {ml_to_l(ml_value):.2f} L for {entry_date} and saved to {DATA_FILE}.")
                except Exception as e:
                    st.error(f"Added locally but failed to save to file: {e}")
            else:
                st.success(f"Added {ml_to_l(ml_value):.2f} L for {entry_date} (session only).")
            # clear session quick preset
            st.session_state["amount_input"] = None

with col2:
    st.subheader("Today's Progress")
    today = date.today()
    if data is None or data.empty:
        today_total_ml = 0
    else:
        df_copy = data.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"]).dt.date
        today_total_ml = int(df_copy.loc[df_copy["date"] == today, "ml"].sum()) if (df_copy["date"] == today).any() else 0

    show_date = st.date_input("Show progress for date", value=today, key="show_date")
    if data is None or data.empty:
        selected_total_ml = 0
    else:
        selected_total_ml = int(df_copy.loc[df_copy["date"] == show_date, "ml"].sum()) if (df_copy["date"] == show_date).any() else 0

    pct = min(selected_total_ml / l_to_ml(goal_liters), 1.0) if goal_liters > 0 else 0
    st.metric(f"Total for {show_date.isoformat()}", f"{ml_to_l(selected_total_ml):.2f} L")
    st.progress(pct)

    remaining_ml = max(l_to_ml(goal_liters) - selected_total_ml, 0)
    if remaining_ml <= 0:
        st.success(f"🎉 Goal reached! You met your {goal_liters:.2f} L target.")
    else:
        st.info(f"Drink {ml_to_l(remaining_ml):.2f} L more to reach {goal_liters:.2f} L.")

# Weekly hydration chart
st.markdown("---")
st.subheader("📈 Weekly Hydration (last 7 days)")

last7 = get_last_n_days_df(data, n=7, end_date=date.today())
last7["day"] = last7["date"].apply(lambda d: d.strftime("%a\n%d %b"))
last7["liters"] = last7["ml"].apply(ml_to_l)
last7["goal_liters"] = goal_liters

fig = px.bar(last7, x="day", y="liters", text=last7["liters"].apply(lambda v: f"{v:.2f} L"))
fig.update_layout(yaxis_title="Liters", xaxis_title="", height=380, template="simple_white")
fig.add_hline(y=goal_liters, line_dash="dash", annotation_text=f"Goal: {goal_liters:.2f} L", annotation_position="top left")

st.plotly_chart(fig, use_container_width=True)

# Show raw aggregated data table
st.markdown("### 📋 Raw data (daily totals)")
if data is None or data.empty:
    st.write("No entries yet. Add intake above to start tracking.")
else:
    agg = data.copy()
    agg["date"] = pd.to_datetime(agg["date"]).dt.date
    agg = agg.groupby("date", as_index=False)["ml"].sum().sort_values("date", ascending=False)
    agg["liters"] = agg["ml"].apply(ml_to_l).round(2)
    st.dataframe(agg[["date", "liters", "ml"]].rename(columns={"date":"Date", "liters":"Liters", "ml":"Milliliters"}))

# Helpful tips
st.markdown("---")
st.markdown(
    """
    **Tips**
    - Aim to sip water regularly throughout the day rather than drinking large amounts at once.
    - If you exercise or are in hot weather, increase your daily goal accordingly.
    - You can persist data to a CSV in the app's working directory (toggle in Settings).
    """
)

# Footer
st.markdown(
    f"<div style='text-align:center; color:#666; padding:8px;'>Made with ❤️ • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>",
    unsafe_allow_html=True
)
