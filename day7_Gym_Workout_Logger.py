# gym_workout_logger.py
"""
Gym Workout Logger 🏋️
- Log exercises: name, date, sets, reps, weight per set (or average weight)
- Persist history to a local JSON file (safe atomic writes)
- Show history table with filter + edit/delete rows
- Weekly progress graph (volume = sum(sets * reps * weight) per week)
- CSV export
Designed as a productivity-ready Streamlit app (clean, modular, and efficient).
"""

from datetime import datetime, date
import json
import os
import tempfile
from typing import List, Dict

import pandas as pd
import streamlit as st

# ---------- Config ----------
DATA_FILE = "workout_history.json"
DATE_FORMAT = "%Y-%m-%d"

st.set_page_config(page_title="Gym Workout Logger 🏋️", layout="centered", initial_sidebar_state="expanded")

# ---------- Utilities ----------
def atomic_write_json(filepath: str, data):
    """Write JSON atomically to reduce corruption risk during concurrent writes."""
    dirpath = os.path.dirname(os.path.abspath(filepath)) or "."
    with tempfile.NamedTemporaryFile("w", dir=dirpath, delete=False, encoding="utf-8") as tf:
        json.dump(data, tf, ensure_ascii=False, indent=2)
        tempname = tf.name
    os.replace(tempname, filepath)

@st.cache_data
def read_history(file_path: str) -> List[Dict]:
    """Cached read - cache invalidates when file content changes (Streamlit uses file-mtime indirectly)."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure proper structure
            if isinstance(data, list):
                return data
    except Exception:
        return []
    return []

def save_history(file_path: str, history: List[Dict]):
    """Save history with atomic write and clear the read cache so next read shows updates."""
    atomic_write_json(file_path, history)
    # clear cache so read_history will reload next time
    read_history.clear()

def compute_volume(entry: Dict) -> float:
    """Compute workout volume for an entry: sets * reps * weight (supports multiple sets as list)."""
    # Accept either single set_info or list of sets
    sets_info = entry.get("sets_info")
    if isinstance(sets_info, list):
        vol = 0.0
        for s in sets_info:
            # s: {"sets": int, "reps": int, "weight": float} or direct set row
            sets = int(s.get("sets", 0))
            reps = int(s.get("reps", 0))
            weight = float(s.get("weight", 0.0))
            vol += sets * reps * weight
        return vol
    else:
        # fallback: use sets, reps, weight top-level
        return float(entry.get("sets", 0)) * float(entry.get("reps", 0)) * float(entry.get("weight", 0.0))

def add_entry(history: List[Dict], entry: Dict):
    history.append(entry)
    save_history(DATA_FILE, history)

def delete_entry(history: List[Dict], idx: int):
    if 0 <= idx < len(history):
        history.pop(idx)
        save_history(DATA_FILE, history)

# ---------- Session State Initialization ----------
if "history" not in st.session_state:
    st.session_state.history = read_history(DATA_FILE)

# ---------- UI ----------
st.title("🏋️ Gym Workout Logger — Productivity Edition")
st.caption("Log exercises, track weekly volume, export data. Designed for real gym workflows.")

with st.sidebar:
    st.header("Quick Actions")
    if st.button("Clear all history"):
        if st.confirm("Are you sure? This will delete all saved workout history."):
            st.session_state.history = []
            save_history(DATA_FILE, st.session_state.history)
            st.success("All history cleared.")
    st.markdown("---")
    st.markdown("**Import / Export**")
    uploaded = st.file_uploader("Upload history JSON", accept_multiple_files=False, type=["json"])
    if uploaded:
        try:
            uploaded_data = json.load(uploaded)
            if isinstance(uploaded_data, list):
                st.session_state.history = uploaded_data
                save_history(DATA_FILE, st.session_state.history)
                st.success("History imported.")
            else:
                st.error("Uploaded JSON must be a list of entries.")
        except Exception as e:
            st.error(f"Import failed: {e}")

    if st.download_button("Export CSV", data=pd.DataFrame(st.session_state.history).to_csv(index=False).encode("utf-8"),
                          file_name=f"workout_history_{date.today().isoformat()}.csv", mime="text/csv"):
        st.info("CSV exported.")

# Layout: tabs for Log / History / Progress / Settings
tabs = st.tabs(["➕ Log Workout", "📋 History", "📈 Weekly Progress", "⚙️ Settings"])

# ---- Tab: Log Workout ----
with tabs[0]:
    st.subheader("Log a Workout")
    col1, col2 = st.columns([2, 1])
    with col1:
        exercise = st.text_input("Exercise name", placeholder="e.g., Bench Press")
        # date selector
        entry_date = st.date_input("Date", value=date.today(), max_value=date.today())
        notes = st.text_area("Notes (optional)", placeholder="E.g., felt strong, paused reps, tempo", height=80)
    with col2:
        # Allow either enter single-set summary or multiple set rows
        mode = st.radio("Input mode", ("Single set summary", "Multiple set rows"))

    # Single set summary inputs
    if mode == "Single set summary":
        sets = st.number_input("Sets", min_value=1, value=3, step=1)
        reps = st.number_input("Reps per set (avg)", min_value=1, value=8, step=1)
        weight = st.number_input("Weight (kg)", min_value=0.0, value=20.0, step=0.5, format="%.1f")
        if st.button("Add Entry"):
            entry = {
                "exercise": exercise.strip() or "Unnamed Exercise",
                "date": entry_date.strftime(DATE_FORMAT),
                "sets": int(sets),
                "reps": int(reps),
                "weight": float(weight),
                "sets_info": [{"sets": int(sets), "reps": int(reps), "weight": float(weight)}],
                "notes": notes.strip(),
                "created_at": datetime.utcnow().isoformat(),
            }
            add_entry(st.session_state.history, entry)
            st.session_state.history = read_history(DATA_FILE)
            st.success(f"Logged {entry['exercise']} — {sets}×{reps} @ {weight}kg")
    else:
        # Multiple set rows: dynamic input table using form
        st.markdown("Enter multiple set rows (sets, reps, weight). Example: 3, 8, 50")
        with st.form("multi_sets_form"):
            rows = st.number_input("Number of different set rows", min_value=1, max_value=10, value=1, step=1)
            set_rows = []
            for i in range(rows):
                c1, c2, c3 = st.columns([1,1,1])
                with c1:
                    s_sets = st.number_input(f"Sets #{i+1}", key=f"s_sets_{i}", min_value=1, value=1, step=1)
                with c2:
                    s_reps = st.number_input(f"Reps #{i+1}", key=f"s_reps_{i}", min_value=1, value=8, step=1)
                with c3:
                    s_weight = st.number_input(f"Weight #{i+1} (kg)", key=f"s_weight_{i}", min_value=0.0, value=20.0, step=0.5, format="%.1f")
                set_rows.append({"sets": int(s_sets), "reps": int(s_reps), "weight": float(s_weight)})
            add_multi = st.form_submit_button("Add Multi-set Entry")
        if add_multi:
            entry = {
                "exercise": exercise.strip() or "Unnamed Exercise",
                "date": entry_date.strftime(DATE_FORMAT),
                "sets_info": set_rows,
                "notes": notes.strip(),
                "created_at": datetime.utcnow().isoformat(),
            }
            # for compatibility, compute top-level sets/reps/weight as summary (first row)
            if set_rows:
                entry["sets"] = set_rows[0]["sets"]
                entry["reps"] = set_rows[0]["reps"]
                entry["weight"] = set_rows[0]["weight"]
            add_entry(st.session_state.history, entry)
            st.session_state.history = read_history(DATA_FILE)
            st.success(f"Logged {entry['exercise']} — {len(set_rows)} set rows")

# ---- Tab: History ----
with tabs[1]:
    st.subheader("Workout History")
    df = pd.DataFrame(st.session_state.history)
    if df.empty:
        st.info("No workout logged yet. Use the 'Log Workout' tab to add entries.")
    else:
        # Expand sets_info into readable summary column
        def summarize_sets(si):
            try:
                if isinstance(si, list):
                    parts = [f"{r['sets']}×{r['reps']}@{r['weight']}kg" for r in si]
                    return "; ".join(parts)
            except Exception:
                pass
            return ""

        df_display = df.copy()
        df_display["summary"] = df_display.get("sets_info", pd.Series([""]*len(df_display))).apply(summarize_sets)
        df_display["volume"] = df_display.apply(lambda r: compute_volume(r.to_dict()), axis=1)
        # Filter by exercise and date range
        exercises = sorted(df_display["exercise"].dropna().unique().tolist())
        colf1, colf2 = st.columns([2, 2])
        with colf1:
            sel_ex = st.multiselect("Filter exercise(s)", options=exercises, default=exercises)
        with colf2:
            min_date = pd.to_datetime(df_display["date"]).min().date()
            max_date = pd.to_datetime(df_display["date"]).max().date()
            dr = st.date_input("Date range", value=(min_date, max_date))
        # apply filters
        mask = pd.to_datetime(df_display["date"]).dt.date.between(dr[0], dr[1])
        if sel_ex:
            mask &= df_display["exercise"].isin(sel_ex)
        filtered = df_display[mask].reset_index(drop=True)

        st.markdown(f"Showing **{len(filtered)}** records")
        st.dataframe(filtered[["date", "exercise", "summary", "volume", "notes"]], use_container_width=True)

        # Row-level delete
        st.markdown("---")
        st.write("Delete a row (by index in the filtered view):")
        idx_to_delete = st.number_input("Index (0-based) from filtered view", min_value=0, max_value=max(0, len(filtered)-1), value=0, step=1)
        if st.button("Delete selected row"):
            # find original index in session history
            original = filtered.iloc[idx_to_delete]
            # Find a match in history (simple approach: match created_at or exact content)
            matched_idx = None
            for i, h in enumerate(st.session_state.history):
                # Use created_at if present for exact match
                if h.get("created_at") == original.get("created_at"):
                    matched_idx = i
                    break
                # fallback: match by date+exercise+volume
                if h.get("date") == original.get("date") and h.get("exercise") == original.get("exercise") and abs(compute_volume(h) - original.get("volume", 0)) < 1e-6:
                    matched_idx = i
                    break
            if matched_idx is not None:
                delete_entry(st.session_state.history, matched_idx)
                st.session_state.history = read_history(DATA_FILE)
                st.success("Deleted row from history.")
            else:
                st.error("Could not find matching row to delete.")

# ---- Tab: Weekly Progress ----
with tabs[2]:
    st.subheader("Weekly Progress — Volume by Exercise")
    hist = pd.DataFrame(st.session_state.history)
    if hist.empty:
        st.info("No data yet. Log workouts to see weekly progress.")
    else:
        # Normalize date
        hist["date"] = pd.to_datetime(hist["date"])
        # compute volume per entry
        hist["volume"] = hist.apply(lambda r: compute_volume(r.to_dict()), axis=1)
        hist["week_start"] = hist["date"].dt.to_period("W").apply(lambda r: r.start_time.date())
        # Group by week and exercise
        grouped = hist.groupby(["week_start", "exercise"])["volume"].sum().reset_index()
        # Pivot for plotting
        pivot = grouped.pivot(index="week_start", columns="exercise", values="volume").fillna(0)
        st.markdown("**Select exercises to include in the chart**")
        chosen = st.multiselect("Exercises", options=list(pivot.columns), default=list(pivot.columns)[:3])
        if not chosen:
            st.warning("Select at least one exercise to plot.")
        else:
            plot_df = pivot[chosen]
            st.line_chart(plot_df)  # Streamlit will handle axes and legend

        st.markdown("**Weekly volume table**")
        st.dataframe(grouped.sort_values(["week_start", "exercise"], ascending=[False, True]).reset_index(drop=True))

# ---- Tab: Settings ----
with tabs[3]:
    st.subheader("Settings & Tips")
    st.markdown("""
- Data stored locally in `workout_history.json` in the app folder.  
- For multi-user or cloud deployment, replace JSON persistence with a database (SQLite, Supabase, Postgres).  
- Export CSV to move data to Excel or analytics tools.  
- Weekly volume = sum(sets * reps * weight) — helpful proxy for work done; not perfect but practical.
""")
    st.markdown("**Deployment tips**")
    st.write("""
1. For Streamlit Cloud: add `workout_history.json` to persistent storage or connect to a DB.  
2. Running behind a multi-user server: use an authenticated DB and user_id in each entry.  
3. To add authentication quickly, integrate `stauth` or OAuth.
""")
