import streamlit as st
import random
import time

# Game Configuration
GRID_SIZE = 15

def initialize_session_state():
    """Initialize game state"""
    if 'snake' not in st.session_state:
        # Start snake in center
        center = GRID_SIZE // 2
        st.session_state.snake = [(center, center), (center-1, center), (center-2, center)]
    
    if 'direction' not in st.session_state:
        st.session_state.direction = 'RIGHT'
    
    if 'food' not in st.session_state:
        st.session_state.food = generate_food()
    
    if 'score' not in st.session_state:
        st.session_state.score = 0
    
    if 'high_score' not in st.session_state:
        st.session_state.high_score = 0
    
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    
    if 'auto_play' not in st.session_state:
        st.session_state.auto_play = False

def generate_food():
    """Generate random food position"""
    while True:
        x = random.randint(0, GRID_SIZE-1)
        y = random.randint(0, GRID_SIZE-1)
        if (x, y) not in getattr(st.session_state, 'snake', []):
            return (x, y)

def move_snake():
    """Move snake and check collisions"""
    if st.session_state.game_over:
        return
    
    head_x, head_y = st.session_state.snake[0]
    
    # Calculate new head position
    if st.session_state.direction == 'UP':
        new_head = (head_x, head_y - 1)
    elif st.session_state.direction == 'DOWN':
        new_head = (head_x, head_y + 1)
    elif st.session_state.direction == 'LEFT':
        new_head = (head_x - 1, head_y)
    else:  # RIGHT
        new_head = (head_x + 1, head_y)
    
    # Check wall collision
    if (new_head[0] < 0 or new_head[0] >= GRID_SIZE or 
        new_head[1] < 0 or new_head[1] >= GRID_SIZE):
        st.session_state.game_over = True
        return
    
    # Check self collision
    if new_head in st.session_state.snake:
        st.session_state.game_over = True
        return
    
    # Add new head
    st.session_state.snake.insert(0, new_head)
    
    # Check if food eaten
    if new_head == st.session_state.food:
        st.session_state.score += 10
        if st.session_state.score > st.session_state.high_score:
            st.session_state.high_score = st.session_state.score
        st.session_state.food = generate_food()
    else:
        # Remove tail
        st.session_state.snake.pop()

def change_direction(new_dir):
    """Change direction with validation"""
    opposites = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
    
    if new_dir != opposites.get(st.session_state.direction):
        st.session_state.direction = new_dir
        
    if not st.session_state.game_started:
        st.session_state.game_started = True

def restart_game():
    """Restart the game"""
    center = GRID_SIZE // 2
    st.session_state.snake = [(center, center), (center-1, center), (center-2, center)]
    st.session_state.direction = 'RIGHT'
    st.session_state.food = generate_food()
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.game_started = False
    st.session_state.auto_play = False

def create_grid():
    """Create the game grid using emojis"""
    grid_html = '<div style="font-family: monospace; line-height: 1.2; font-size: 20px; text-align: center; background-color: #2c3e50; padding: 15px; border-radius: 10px; display: inline-block;">'
    
    for y in range(GRID_SIZE):
        row_html = '<div>'
        for x in range(GRID_SIZE):
            if (x, y) == st.session_state.snake[0]:
                # Snake head
                row_html += '<span style="color: #e74c3c;">🟥</span>'
            elif (x, y) in st.session_state.snake:
                # Snake body
                row_html += '<span style="color: #2ecc71;">🟩</span>'
            elif (x, y) == st.session_state.food:
                # Food
                row_html += '<span style="color: #f39c12;">🟨</span>'
            else:
                # Empty space
                row_html += '<span style="color: #95a5a6;">⬜</span>'
        row_html += '</div>'
        grid_html += row_html
    
    grid_html += '</div>'
    return grid_html

def main():
    st.set_page_config(page_title="Snake Game", page_icon="🐍", layout="wide")
    
    initialize_session_state()
    
    st.title("🐍 Snake Game")
    
    # Top scores
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 Score", st.session_state.score)
    with col2:
        st.metric("🏆 High Score", st.session_state.high_score)
    with col3:
        st.metric("🐍 Length", len(st.session_state.snake))
    with col4:
        if st.session_state.game_over:
            st.error("Game Over!")
        elif st.session_state.game_started:
            st.success("Playing")
        else:
            st.info("Ready")
    
    st.markdown("---")
    
    # Main game layout
    game_col, control_col = st.columns([2, 1])
    
    with game_col:
        st.markdown("### 🎮 Game Board")
        
        # Display the grid
        grid_html = create_grid()
        st.markdown(grid_html, unsafe_allow_html=True)
        
        if st.session_state.game_over:
            st.error("💀 **GAME OVER!** Snake crashed!")
            if st.session_state.score == st.session_state.high_score and st.session_state.score > 0:
                st.balloons()
                st.success("🎉 **NEW HIGH SCORE!**")
    
    with control_col:
        st.markdown("### 🕹️ Game Controls")
        
        # Direction buttons
        _, up_col, _ = st.columns([1, 1, 1])
        with up_col:
            if st.button("⬆️ UP", key="up", use_container_width=True):
                change_direction('UP')
                if st.session_state.game_started and not st.session_state.game_over:
                    move_snake()
                st.rerun()
        
        left_col, _, right_col = st.columns([1, 1, 1])
        with left_col:
            if st.button("⬅️ LEFT", key="left", use_container_width=True):
                change_direction('LEFT')
                if st.session_state.game_started and not st.session_state.game_over:
                    move_snake()
                st.rerun()
        
        with right_col:
            if st.button("➡️ RIGHT", key="right", use_container_width=True):
                change_direction('RIGHT')
                if st.session_state.game_started and not st.session_state.game_over:
                    move_snake()
                st.rerun()
        
        _, down_col, _ = st.columns([1, 1, 1])
        with down_col:
            if st.button("⬇️ DOWN", key="down", use_container_width=True):
                change_direction('DOWN')
                if st.session_state.game_started and not st.session_state.game_over:
                    move_snake()
                st.rerun()
        
        st.markdown("---")
        
        # Game controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎮 Move", use_container_width=True, disabled=st.session_state.game_over):
                if st.session_state.game_started:
                    move_snake()
                    st.rerun()
        
        with col2:
            if st.button("🔄 New Game", use_container_width=True):
                restart_game()
                st.rerun()
        
        # Auto play toggle
        auto_play = st.checkbox("🤖 Auto Play")
        if auto_play != st.session_state.auto_play:
            st.session_state.auto_play = auto_play
        
        st.markdown("---")
        
        st.markdown("### 📊 Game Status")
        st.write(f"**Direction:** {st.session_state.direction}")
        st.write(f"**Snake Head:** {st.session_state.snake[0]}")
        st.write(f"**Food:** {st.session_state.food}")
    
    # Auto play functionality
    if (st.session_state.auto_play and 
        st.session_state.game_started and 
        not st.session_state.game_over):
        time.sleep(0.5)
        move_snake()
        st.rerun()
    
    # Instructions
    st.markdown("---")
    with st.expander("📋 How to Play"):
        st.markdown("""
        ### 🎯 **How to Play:**
        1. **Start**: Click any arrow button to start the game
        2. **Move**: Use arrow buttons to change direction
        3. **Eat**: Guide the snake (🟥🟩) to the food (🟨)
        4. **Grow**: Each food eaten increases length and score
        5. **Avoid**: Don't hit walls or yourself!
        
        ### 🎮 **Controls:**
        - **Arrow Buttons**: Change direction and move
        - **Move Button**: Advance one step manually
        - **Auto Play**: Enable for continuous movement
        - **New Game**: Restart when game over
        
        ### 🏆 **Scoring:**
        - Each food = +10 points
        - Try to beat your high score!
        
        ### 📱 **Legend:**
        - 🟥 = Snake Head
        - 🟩 = Snake Body  
        - 🟨 = Food
        - ⬜ = Empty Space
        """)

if __name__ == "__main__":
    main()