import streamlit as st
import random
import time

# Game Configuration
EMPTY = ""
PLAYER_X = "❌"
PLAYER_O = "⭕"

def initialize_session_state():
    """Initialize session state variables"""
    if 'board' not in st.session_state:
        st.session_state.board = [["" for _ in range(3)] for _ in range(3)]
    if 'current_player' not in st.session_state:
        st.session_state.current_player = PLAYER_X
    if 'game_mode' not in st.session_state:
        st.session_state.game_mode = "Two Player"
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'winner' not in st.session_state:
        st.session_state.winner = None
    if 'winning_line' not in st.session_state:
        st.session_state.winning_line = []
    if 'scores' not in st.session_state:
        st.session_state.scores = {"X": 0, "O": 0, "Draw": 0}
    if 'computer_thinking' not in st.session_state:
        st.session_state.computer_thinking = False

def reset_board():
    """Reset the game board and state"""
    st.session_state.board = [["" for _ in range(3)] for _ in range(3)]
    st.session_state.current_player = PLAYER_X
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.winning_line = []
    st.session_state.computer_thinking = False

def check_winner():
    """Check if there's a winner and return winner and winning line"""
    board = st.session_state.board
    
    # Check rows
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != "":
            return board[i][0], [(i, 0), (i, 1), (i, 2)]
    
    # Check columns
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] != "":
            return board[0][j], [(0, j), (1, j), (2, j)]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0], [(0, 0), (1, 1), (2, 2)]
    
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2], [(0, 2), (1, 1), (2, 0)]
    
    return None, []

def is_board_full():
    """Check if the board is full"""
    for row in st.session_state.board:
        if "" in row:
            return False
    return True

def get_empty_positions():
    """Get list of empty positions on the board"""
    empty_positions = []
    for i in range(3):
        for j in range(3):
            if st.session_state.board[i][j] == "":
                empty_positions.append((i, j))
    return empty_positions

def computer_move():
    """Make a computer move (random for now, but could be enhanced with AI)"""
    empty_positions = get_empty_positions()
    if empty_positions:
        # Simple AI: Try to win first, then block player, then random
        best_move = get_best_move()
        if best_move:
            row, col = best_move
        else:
            row, col = random.choice(empty_positions)
        
        st.session_state.board[row][col] = PLAYER_O
        st.session_state.current_player = PLAYER_X

def get_best_move():
    """Get the best move for computer (simple AI logic)"""
    # Check if computer can win
    for i in range(3):
        for j in range(3):
            if st.session_state.board[i][j] == "":
                st.session_state.board[i][j] = PLAYER_O
                winner, _ = check_winner()
                st.session_state.board[i][j] = ""  # Undo move
                if winner == PLAYER_O:
                    return (i, j)
    
    # Check if computer needs to block player
    for i in range(3):
        for j in range(3):
            if st.session_state.board[i][j] == "":
                st.session_state.board[i][j] = PLAYER_X
                winner, _ = check_winner()
                st.session_state.board[i][j] = ""  # Undo move
                if winner == PLAYER_X:
                    return (i, j)
    
    # Take center if available
    if st.session_state.board[1][1] == "":
        return (1, 1)
    
    # Take corners
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    available_corners = [(i, j) for i, j in corners if st.session_state.board[i][j] == ""]
    if available_corners:
        return random.choice(available_corners)
    
    return None

def make_move(row, col):
    """Make a move at the specified position"""
    if st.session_state.board[row][col] == "" and not st.session_state.game_over:
        st.session_state.board[row][col] = st.session_state.current_player
        
        # Check for winner
        winner, winning_line = check_winner()
        if winner:
            st.session_state.game_over = True
            st.session_state.winner = winner
            st.session_state.winning_line = winning_line
            # Update scores
            if winner == PLAYER_X:
                st.session_state.scores["X"] += 1
            else:
                st.session_state.scores["O"] += 1
        elif is_board_full():
            st.session_state.game_over = True
            st.session_state.winner = "Draw"
            st.session_state.scores["Draw"] += 1
        else:
            # Switch player
            st.session_state.current_player = PLAYER_O if st.session_state.current_player == PLAYER_X else PLAYER_X
            
            # If playing against computer and it's computer's turn
            if (st.session_state.game_mode == "vs Computer" and 
                st.session_state.current_player == PLAYER_O and 
                not st.session_state.game_over):
                st.session_state.computer_thinking = True

def display_board():
    """Display the game board with buttons"""
    st.markdown("### 🎯 Game Board")
    
    # Create 3x3 grid
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            with cols[j]:
                # Determine button style based on winning line
                button_style = ""
                if (i, j) in st.session_state.winning_line:
                    button_style = "🌟"  # Highlight winning positions
                
                # Button content
                button_text = st.session_state.board[i][j] if st.session_state.board[i][j] else "⬜"
                if (i, j) in st.session_state.winning_line:
                    button_text = f"{button_style}{st.session_state.board[i][j]}{button_style}"
                
                # Create button with larger size
                if st.button(
                    button_text,
                    key=f"btn_{i}_{j}",
                    use_container_width=True,
                    disabled=st.session_state.board[i][j] != "" or st.session_state.game_over or st.session_state.computer_thinking
                ):
                    make_move(i, j)
                    st.rerun()

def display_game_info():
    """Display current game information"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not st.session_state.game_over and not st.session_state.computer_thinking:
            st.info(f"Current Player: {st.session_state.current_player}")
        elif st.session_state.computer_thinking:
            st.warning("🤖 Computer is thinking...")
        elif st.session_state.winner == "Draw":
            st.warning("🤝 It's a Draw!")
        else:
            st.success(f"🎉 Winner: {st.session_state.winner}")
    
    with col2:
        st.metric("Game Mode", st.session_state.game_mode)
    
    with col3:
        if st.button("🔄 Reset Board", use_container_width=True):
            reset_board()
            st.rerun()

def display_scoreboard():
    """Display the current scores"""
    st.markdown("### 📊 Scoreboard")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("❌ Player X", st.session_state.scores["X"])
    
    with col2:
        st.metric("⭕ Player O", st.session_state.scores["O"])
    
    with col3:
        st.metric("🤝 Draws", st.session_state.scores["Draw"])

def display_game_controls():
    """Display game mode selection and controls"""
    st.markdown("### ⚙️ Game Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_mode = st.selectbox(
            "Choose Game Mode:",
            ["Two Player", "vs Computer"],
            index=0 if st.session_state.game_mode == "Two Player" else 1
        )
        
        if new_mode != st.session_state.game_mode:
            st.session_state.game_mode = new_mode
            reset_board()
            st.rerun()
    
    with col2:
        if st.button("🆕 New Game", use_container_width=True):
            reset_board()
            st.rerun()

def handle_computer_move():
    """Handle computer move with a slight delay for better UX"""
    if (st.session_state.computer_thinking and 
        st.session_state.game_mode == "vs Computer" and 
        st.session_state.current_player == PLAYER_O and 
        not st.session_state.game_over):
        
        # Add a small delay for better user experience
        time.sleep(0.5)
        computer_move()
        st.session_state.computer_thinking = False
        
        # Check for winner after computer move
        winner, winning_line = check_winner()
        if winner:
            st.session_state.game_over = True
            st.session_state.winner = winner
            st.session_state.winning_line = winning_line
            if winner == PLAYER_O:
                st.session_state.scores["O"] += 1
        elif is_board_full():
            st.session_state.game_over = True
            st.session_state.winner = "Draw"
            st.session_state.scores["Draw"] += 1
        
        st.rerun()

def display_game_rules():
    """Display game rules and instructions"""
    with st.expander("📋 How to Play"):
        st.markdown("""
        **Tic-Tac-Toe Rules:**
        
        🎯 **Objective:** Get three of your marks in a row (horizontally, vertically, or diagonally)
        
        🎮 **How to Play:**
        - Click on any empty square to place your mark
        - Players alternate turns (❌ goes first)
        - First player to get 3 in a row wins!
        - If all squares are filled without a winner, it's a draw
        
        🤖 **vs Computer Mode:**
        - You play as ❌ (X)
        - Computer plays as ⭕ (O)
        - Computer uses basic AI strategy
        
        👥 **Two Player Mode:**
        - Take turns clicking squares
        - ❌ (Player X) always goes first
        
        🌟 **Winning combinations are highlighted with stars!**
        """)

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Tic-Tac-Toe Game",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Main title
    st.title("🎮 Tic-Tac-Toe Game ❌⭕")
    st.markdown("*A classic game for all ages!*")
    st.markdown("---")
    
    # Handle computer move if needed
    if st.session_state.computer_thinking:
        handle_computer_move()
    
    # Main game layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Game board
        display_board()
        
        # Game information
        st.markdown("---")
        display_game_info()
    
    with col2:
        # Game controls
        display_game_controls()
        
        st.markdown("---")
        
        # Scoreboard
        display_scoreboard()
        
        st.markdown("---")
        
        # Reset scores button
        if st.button("🗑️ Reset Scores", use_container_width=True):
            st.session_state.scores = {"X": 0, "O": 0, "Draw": 0}
            st.rerun()
    
    # Game rules
    st.markdown("---")
    display_game_rules()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🎮 Built with Streamlit | Enjoy the game! 🎮"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()