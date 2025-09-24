import streamlit as st
import random
import time
from datetime import datetime

# Game Configuration
CHOICES = {
    "Rock": {"emoji": "🪨", "beats": "Scissors"},
    "Paper": {"emoji": "📄", "beats": "Rock"},
    "Scissors": {"emoji": "✂️", "beats": "Paper"}
}

RESULT_MESSAGES = {
    "win": [
        "🎉 Awesome! You won!",
        "🏆 Great job! Victory is yours!",
        "💪 You crushed it!",
        "⭐ Fantastic win!",
        "🎯 Bulls-eye! You won!"
    ],
    "lose": [
        "😅 Computer got you this time!",
        "🤖 AI strikes back!",
        "😬 Better luck next time!",
        "🎲 Computer's lucky day!",
        "🔄 Ready for revenge?"
    ],
    "draw": [
        "🤝 Great minds think alike!",
        "🎭 Perfect match!",
        "⚖️ Perfectly balanced!",
        "🔄 Try again!",
        "🤷‍♂️ Nobody wins this round!"
    ]
}

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_score' not in st.session_state:
        st.session_state.user_score = 0
    if 'computer_score' not in st.session_state:
        st.session_state.computer_score = 0
    if 'draws' not in st.session_state:
        st.session_state.draws = 0
    if 'total_games' not in st.session_state:
        st.session_state.total_games = 0
    if 'last_user_choice' not in st.session_state:
        st.session_state.last_user_choice = None
    if 'last_computer_choice' not in st.session_state:
        st.session_state.last_computer_choice = None
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None
    if 'game_history' not in st.session_state:
        st.session_state.game_history = []
    if 'streak' not in st.session_state:
        st.session_state.streak = 0
    if 'best_streak' not in st.session_state:
        st.session_state.best_streak = 0
    if 'computer_thinking' not in st.session_state:
        st.session_state.computer_thinking = False

def get_computer_choice():
    """Generate computer's choice"""
    return random.choice(list(CHOICES.keys()))

def determine_winner(user_choice, computer_choice):
    """Determine the winner of the game"""
    if user_choice == computer_choice:
        return "draw"
    elif CHOICES[user_choice]["beats"] == computer_choice:
        return "win"
    else:
        return "lose"

def update_scores(result):
    """Update game scores based on result"""
    st.session_state.total_games += 1
    
    if result == "win":
        st.session_state.user_score += 1
        st.session_state.streak += 1
        if st.session_state.streak > st.session_state.best_streak:
            st.session_state.best_streak = st.session_state.streak
    elif result == "lose":
        st.session_state.computer_score += 1
        st.session_state.streak = 0
    else:  # draw
        st.session_state.draws += 1

def add_to_history(user_choice, computer_choice, result):
    """Add game to history"""
    game_record = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "user_choice": user_choice,
        "computer_choice": computer_choice,
        "result": result
    }
    st.session_state.game_history.append(game_record)
    
    # Keep only last 10 games
    if len(st.session_state.game_history) > 10:
        st.session_state.game_history.pop(0)

def play_game(user_choice):
    """Play a round of the game"""
    # Show computer thinking animation
    st.session_state.computer_thinking = True
    
    # Generate computer choice
    computer_choice = get_computer_choice()
    
    # Determine winner
    result = determine_winner(user_choice, computer_choice)
    
    # Update game state
    st.session_state.last_user_choice = user_choice
    st.session_state.last_computer_choice = computer_choice
    st.session_state.last_result = result
    
    # Update scores and history
    update_scores(result)
    add_to_history(user_choice, computer_choice, result)
    
    st.session_state.computer_thinking = False

def display_game_choices():
    """Display the main game choice buttons"""
    st.markdown("### 🎮 Make Your Choice")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(
            f"{CHOICES['Rock']['emoji']}\n**Rock**",
            key="rock_btn",
            use_container_width=True,
            disabled=st.session_state.computer_thinking
        ):
            play_game("Rock")
            st.rerun()
    
    with col2:
        if st.button(
            f"{CHOICES['Paper']['emoji']}\n**Paper**",
            key="paper_btn",
            use_container_width=True,
            disabled=st.session_state.computer_thinking
        ):
            play_game("Paper")
            st.rerun()
    
    with col3:
        if st.button(
            f"{CHOICES['Scissors']['emoji']}\n**Scissors**",
            key="scissors_btn",
            use_container_width=True,
            disabled=st.session_state.computer_thinking
        ):
            play_game("Scissors")
            st.rerun()

def display_last_round():
    """Display the result of the last round"""
    if st.session_state.last_result is None:
        st.info("👆 Choose Rock, Paper, or Scissors to start playing!")
        return
    
    st.markdown("### 🎯 Last Round Result")
    
    # Create battle display
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown(
            f"<div style='text-align: center; font-size: 3em;'>"
            f"{CHOICES[st.session_state.last_user_choice]['emoji']}"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown(f"<div style='text-align: center;'><b>You</b><br>{st.session_state.last_user_choice}</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(
            f"<div style='text-align: center; font-size: 2em; margin-top: 20px;'>"
            f"🆚"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"<div style='text-align: center; font-size: 3em;'>"
            f"{CHOICES[st.session_state.last_computer_choice]['emoji']}"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown(f"<div style='text-align: center;'><b>Computer</b><br>{st.session_state.last_computer_choice}</div>", unsafe_allow_html=True)
    
    # Display result message
    result_message = random.choice(RESULT_MESSAGES[st.session_state.last_result])
    
    if st.session_state.last_result == "win":
        st.success(result_message)
    elif st.session_state.last_result == "lose":
        st.error(result_message)
    else:
        st.warning(result_message)
    
    # Show game logic
    if st.session_state.last_result != "draw":
        winner_choice = st.session_state.last_user_choice if st.session_state.last_result == "win" else st.session_state.last_computer_choice
        loser_choice = st.session_state.last_computer_choice if st.session_state.last_result == "win" else st.session_state.last_user_choice
        st.caption(f"💡 {winner_choice} beats {loser_choice}")

def display_scoreboard():
    """Display the current scores and statistics"""
    st.markdown("### 📊 Scoreboard")
    
    # Main scores
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏆 Your Wins", st.session_state.user_score)
    
    with col2:
        st.metric("🤖 Computer Wins", st.session_state.computer_score)
    
    with col3:
        st.metric("🤝 Draws", st.session_state.draws)
    
    # Additional statistics
    if st.session_state.total_games > 0:
        win_rate = (st.session_state.user_score / st.session_state.total_games) * 100
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.metric("🎯 Total Games", st.session_state.total_games)
        
        with col5:
            st.metric("📈 Win Rate", f"{win_rate:.1f}%")
        
        with col6:
            st.metric("🔥 Current Streak", st.session_state.streak)
    
    # Best streak
    if st.session_state.best_streak > 0:
        st.metric("🏅 Best Streak", st.session_state.best_streak)

def display_game_history():
    """Display recent game history"""
    if not st.session_state.game_history:
        return
    
    st.markdown("### 📈 Recent Games")
    
    # Create a table of recent games
    history_data = []
    for game in reversed(st.session_state.game_history[-5:]):  # Show last 5 games
        result_emoji = "🏆" if game["result"] == "win" else "❌" if game["result"] == "lose" else "🤝"
        history_data.append({
            "Time": game["timestamp"],
            "You": f"{CHOICES[game['user_choice']]['emoji']} {game['user_choice']}",
            "Computer": f"{CHOICES[game['computer_choice']]['emoji']} {game['computer_choice']}",
            "Result": f"{result_emoji} {game['result'].title()}"
        })
    
    if history_data:
        import pandas as pd
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

def display_game_controls():
    """Display game control buttons"""
    st.markdown("### ⚙️ Game Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 New Game", use_container_width=True):
            # Reset only the current game state, keep scores
            st.session_state.last_user_choice = None
            st.session_state.last_computer_choice = None
            st.session_state.last_result = None
            st.rerun()
    
    with col2:
        if st.button("🗑️ Reset All Scores", use_container_width=True):
            # Reset everything
            st.session_state.user_score = 0
            st.session_state.computer_score = 0
            st.session_state.draws = 0
            st.session_state.total_games = 0
            st.session_state.game_history = []
            st.session_state.streak = 0
            st.session_state.best_streak = 0
            st.session_state.last_user_choice = None
            st.session_state.last_computer_choice = None
            st.session_state.last_result = None
            st.success("🎯 All scores reset!")
            st.rerun()

def display_game_rules():
    """Display game rules and tips"""
    with st.expander("📋 Game Rules & Strategy"):
        st.markdown("""
        ### 🎮 **How to Play:**
        - Choose Rock 🪨, Paper 📄, or Scissors ✂️
        - Computer makes its choice simultaneously
        - Winner is determined by classic rules:
        
        ### 🏆 **Winning Rules:**
        - 🪨 **Rock beats Scissors** (crushes)
        - 📄 **Paper beats Rock** (covers)
        - ✂️ **Scissors beats Paper** (cuts)
        
        ### 🎯 **Strategy Tips:**
        - It's a game of chance - no guaranteed winning strategy!
        - Try to be unpredictable in your choices
        - Watch for patterns (though computer chooses randomly)
        - Keep track of your win rate and streaks
        
        ### 📊 **Scoring:**
        - Win Rate: Your wins ÷ total games
        - Streak: Consecutive wins
        - Best Streak: Your longest winning streak
        """)

def display_computer_thinking():
    """Display computer thinking animation"""
    if st.session_state.computer_thinking:
        st.markdown("### 🤖 Computer is thinking...")
        
        # Simple thinking animation
        thinking_placeholder = st.empty()
        for i in range(3):
            thinking_placeholder.markdown(f"🤔{'.' * (i + 1)}")
            time.sleep(0.3)
        
        thinking_placeholder.empty()

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Rock Paper Scissors",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Main title
    st.title("🎮 Rock, Paper, Scissors")
    st.markdown("*Classic game - You vs Computer!*")
    st.markdown("---")
    
    # Handle computer thinking state
    if st.session_state.computer_thinking:
        display_computer_thinking()
    
    # Main game layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Game choices
        display_game_choices()
        
        st.markdown("---")
        
        # Last round result
        display_last_round()
    
    with col2:
        # Scoreboard
        display_scoreboard()
        
        st.markdown("---")
        
        # Game controls
        display_game_controls()
    
    # Full width sections
    st.markdown("---")
    
    # Game history
    display_game_history()
    
    # Game rules
    st.markdown("---")
    display_game_rules()
    
    # Sidebar information
    with st.sidebar:
        st.markdown("## 🎯 Quick Stats")
        
        if st.session_state.total_games > 0:
            st.metric("Games Played", st.session_state.total_games)
            
            # Win rate pie chart representation
            if st.session_state.user_score > 0 or st.session_state.computer_score > 0:
                user_pct = (st.session_state.user_score / st.session_state.total_games) * 100
                computer_pct = (st.session_state.computer_score / st.session_state.total_games) * 100
                draw_pct = (st.session_state.draws / st.session_state.total_games) * 100
                
                st.markdown("**Performance Breakdown:**")
                st.progress(user_pct / 100, text=f"Your wins: {user_pct:.1f}%")
                st.progress(computer_pct / 100, text=f"Computer wins: {computer_pct:.1f}%")
                st.progress(draw_pct / 100, text=f"Draws: {draw_pct:.1f}%")
        else:
            st.info("Start playing to see stats!")
        
        st.markdown("---")
        st.markdown("### 🎲 Fun Facts")
        st.markdown("""
        - Rock Paper Scissors originated in China
        - Called "Roshambo" in some regions
        - World Championship held annually
        - Used to make important decisions!
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🎮 Built with Streamlit | May the best player win! 🏆"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()