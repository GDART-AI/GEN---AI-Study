import streamlit as st
import time
from datetime import datetime, timedelta
import threading

def initialize_session_state():
    """Initialize session state variables"""
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'elapsed_time' not in st.session_state:
        st.session_state.elapsed_time = 0.0
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'lap_times' not in st.session_state:
        st.session_state.lap_times = []
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()

def format_time(seconds):
    """Format time in HH:MM:SS.MS format"""
    if seconds < 0:
        seconds = 0
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 100)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}.{milliseconds:02d}"

def get_current_elapsed_time():
    """Get current elapsed time"""
    if st.session_state.is_running and st.session_state.start_time:
        current_time = time.time()
        return st.session_state.elapsed_time + (current_time - st.session_state.start_time)
    else:
        return st.session_state.elapsed_time

def start_stopwatch():
    """Start the stopwatch"""
    if not st.session_state.is_running:
        st.session_state.start_time = time.time()
        st.session_state.is_running = True

def stop_stopwatch():
    """Stop the stopwatch"""
    if st.session_state.is_running:
        current_time = time.time()
        st.session_state.elapsed_time += (current_time - st.session_state.start_time)
        st.session_state.is_running = False
        st.session_state.start_time = None

def reset_stopwatch():
    """Reset the stopwatch"""
    st.session_state.start_time = None
    st.session_state.elapsed_time = 0.0
    st.session_state.is_running = False
    st.session_state.lap_times = []

def add_lap():
    """Add a lap time"""
    current_elapsed = get_current_elapsed_time()
    lap_number = len(st.session_state.lap_times) + 1
    
    # Calculate split time (time since last lap)
    if st.session_state.lap_times:
        split_time = current_elapsed - st.session_state.lap_times[-1]['total_time']
    else:
        split_time = current_elapsed
    
    lap_data = {
        'lap_number': lap_number,
        'total_time': current_elapsed,
        'split_time': split_time,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    
    st.session_state.lap_times.append(lap_data)

def display_main_timer():
    """Display the main stopwatch timer"""
    current_time = get_current_elapsed_time()
    formatted_time = format_time(current_time)
    
    # Large timer display
    st.markdown(
        f"""
        <div style='
            text-align: center;
            font-size: 4em;
            font-weight: bold;
            font-family: monospace;
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            padding: 20px;
            margin: 20px 0;
            border: 2px solid #ddd;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        '>
            ⏱️ {formatted_time}
        </div>
        """,
        unsafe_allow_html=True
    )

def display_control_buttons():
    """Display start/stop/reset control buttons"""
    st.markdown("### 🎛️ Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.is_running:
            if st.button("⏸️ **Stop**", use_container_width=True, type="secondary"):
                stop_stopwatch()
                st.rerun()
        else:
            if st.button("▶️ **Start**", use_container_width=True, type="primary"):
                start_stopwatch()
                st.rerun()
    
    with col2:
        if st.button("🔄 **Reset**", use_container_width=True):
            reset_stopwatch()
            st.rerun()
    
    with col3:
        if st.button("📍 **Lap**", use_container_width=True, disabled=not st.session_state.is_running):
            add_lap()
            st.rerun()
    
    with col4:
        if st.button("🔄 **Refresh**", use_container_width=True):
            st.rerun()

def display_status():
    """Display current stopwatch status"""
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        status = "🟢 Running" if st.session_state.is_running else "🔴 Stopped"
        st.metric("Status", status)
    
    with status_col2:
        total_laps = len(st.session_state.lap_times)
        st.metric("Total Laps", total_laps)
    
    with status_col3:
        session_time = datetime.now() - st.session_state.session_start
        session_duration = str(session_time).split('.')[0]  # Remove microseconds
        st.metric("Session Duration", session_duration)

def display_lap_times():
    """Display lap times table"""
    if not st.session_state.lap_times:
        st.info("📍 No lap times recorded yet. Click 'Lap' while the timer is running to record lap times!")
        return
    
    st.markdown("### 📊 Lap Times")
    
    # Create lap times table
    lap_data = []
    for lap in st.session_state.lap_times:
        lap_data.append({
            "Lap #": lap['lap_number'],
            "Split Time": format_time(lap['split_time']),
            "Total Time": format_time(lap['total_time']),
            "Recorded At": lap['timestamp']
        })
    
    # Display as dataframe
    import pandas as pd
    df = pd.DataFrame(lap_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Lap statistics
    if len(st.session_state.lap_times) > 1:
        split_times = [lap['split_time'] for lap in st.session_state.lap_times]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fastest_lap = min(split_times)
            st.metric("🏃 Fastest Lap", format_time(fastest_lap))
        
        with col2:
            slowest_lap = max(split_times)
            st.metric("🐌 Slowest Lap", format_time(slowest_lap))
        
        with col3:
            avg_lap = sum(split_times) / len(split_times)
            st.metric("📊 Average Lap", format_time(avg_lap))

def display_preset_timers():
    """Display preset timer options"""
    st.markdown("### ⚡ Quick Timers")
    
    presets = {
        "30 seconds": 30,
        "1 minute": 60,
        "5 minutes": 300,
        "10 minutes": 600,
        "15 minutes": 900,
        "30 minutes": 1800,
        "1 hour": 3600
    }
    
    cols = st.columns(len(presets))
    
    for i, (label, seconds) in enumerate(presets.items()):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"preset_{i}"):
                # Set the timer to the preset value and start it
                reset_stopwatch()
                st.session_state.elapsed_time = 0
                start_stopwatch()
                st.rerun()

def display_timer_features():
    """Display additional timer features"""
    with st.expander("⚙️ Timer Features & Tips"):
        st.markdown("""
        ### 🎯 **Stopwatch Features:**
        - **Precision Timing**: Accurate to centiseconds (1/100th second)
        - **Lap Recording**: Track split times and total times
        - **Session Tracking**: See how long you've been using the app
        - **Statistics**: Fastest, slowest, and average lap times
        
        ### 🎮 **How to Use:**
        1. **Start**: Click ▶️ to begin timing
        2. **Lap**: Click 📍 while running to record lap times
        3. **Stop**: Click ⏸️ to pause the timer
        4. **Reset**: Click 🔄 to clear all times
        5. **Refresh**: Click 🔄 to update the display
        
        ### 💡 **Pro Tips:**
        - Use lap times for interval training
        - Record multiple activities in one session
        - The timer continues running in the background
        - Use preset timers for quick timing sessions
        
        ### 🏃 **Perfect for:**
        - Sports training and workouts
        - Cooking and baking times
        - Study sessions (Pomodoro technique)
        - Meeting and presentation timing
        - Racing and competition events
        """)

def display_export_options():
    """Display options to export lap times"""
    if st.session_state.lap_times:
        st.markdown("### 📥 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create CSV data
            csv_data = "Lap Number,Split Time,Total Time,Recorded At\n"
            for lap in st.session_state.lap_times:
                csv_data += f"{lap['lap_number']},{format_time(lap['split_time'])},{format_time(lap['total_time'])},{lap['timestamp']}\n"
            
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"lap_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Create text summary
            summary = f"Stopwatch Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            summary += "="*50 + "\n\n"
            summary += f"Total Time: {format_time(get_current_elapsed_time())}\n"
            summary += f"Total Laps: {len(st.session_state.lap_times)}\n\n"
            summary += "Lap Times:\n"
            summary += "-"*30 + "\n"
            
            for lap in st.session_state.lap_times:
                summary += f"Lap {lap['lap_number']:2d}: {format_time(lap['split_time'])} (Total: {format_time(lap['total_time'])})\n"
            
            st.download_button(
                label="📄 Download Summary",
                data=summary,
                file_name=f"stopwatch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

def auto_refresh():
    """Auto-refresh the timer display"""
    if st.session_state.is_running:
        # Use a placeholder for auto-updating
        time.sleep(0.01)  # Small delay to prevent too frequent updates
        st.rerun()

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Stopwatch Timer",
        page_icon="⏱️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Main title
    st.title("⏱️ Digital Stopwatch Timer")
    st.markdown("*Precision timing for all your needs!*")
    st.markdown("---")
    
    # Main timer display
    display_main_timer()
    
    # Control buttons
    display_control_buttons()
    
    # Status information
    st.markdown("---")
    display_status()
    
    # Main content layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Lap times table
        st.markdown("---")
        display_lap_times()
    
    with col2:
        # Quick preset timers
        st.markdown("---")
        display_preset_timers()
        
        # Export options
        if st.session_state.lap_times:
            st.markdown("---")
            display_export_options()
    
    # Additional features
    st.markdown("---")
    display_timer_features()
    
    # Sidebar information
    with st.sidebar:
        st.markdown("## ⏰ Timer Info")
        
        # Current time
        current_elapsed = get_current_elapsed_time()
        st.metric("⏱️ Current Time", format_time(current_elapsed))
        
        # Real-time clock
        st.markdown(f"🕐 **Current Time:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Session info
        st.markdown("---")
        st.markdown("### 📊 Session Stats")
        
        if st.session_state.lap_times:
            total_splits = sum(lap['split_time'] for lap in st.session_state.lap_times)
            st.metric("⚡ Total Split Time", format_time(total_splits))
            
            if len(st.session_state.lap_times) > 0:
                avg_split = total_splits / len(st.session_state.lap_times)
                st.metric("📊 Average Split", format_time(avg_split))
        
        # Auto-refresh toggle
        st.markdown("---")
        auto_refresh_enabled = st.checkbox("🔄 Auto Refresh", value=True)
        
        if auto_refresh_enabled and st.session_state.is_running:
            time.sleep(0.1)
            st.rerun()
        
        # Quick actions
        st.markdown("---")
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("🏁 Clear All Data", use_container_width=True):
            reset_stopwatch()
            st.success("✅ All data cleared!")
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "⏱️ Built with Streamlit | Perfect timing every time! ⏱️"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()