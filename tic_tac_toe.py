import streamlit as st
import random
import math

# -------------------
# Utility Functions
# -------------------
def create_board():
    return [" "] * 9

def check_winner(board, player):
    win_combos = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    return any(all(board[i] == player for i in combo) for combo in win_combos)

def is_full(board):
    return " " not in board

# --- AI modes ---
def easy_ai(board, ai_symbol):
    empty = [i for i in range(9) if board[i] == " "]
    if empty: board[random.choice(empty)] = ai_symbol

def intermediate_ai(board, ai_symbol, player_symbol):
    for i in range(9):  # win
        if board[i] == " ":
            board[i] = ai_symbol
            if check_winner(board, ai_symbol): return
            board[i] = " "
    for i in range(9):  # block
        if board[i] == " ":
            board[i] = player_symbol
            if check_winner(board, player_symbol):
                board[i] = ai_symbol; return
            board[i] = " "
    easy_ai(board, ai_symbol)

def minimax(board, maximizing, ai, player):
    if check_winner(board, ai): return 1
    if check_winner(board, player): return -1
    if is_full(board): return 0

    if maximizing:
        best = -math.inf
        for i in range(9):
            if board[i] == " ":
                board[i] = ai
                best = max(best, minimax(board, False, ai, player))
                board[i] = " "
        return best
    else:
        best = math.inf
        for i in range(9):
            if board[i] == " ":
                board[i] = player
                best = min(best, minimax(board, True, ai, player))
                board[i] = " "
        return best

def hard_ai(board, ai, player):
    best, move = -math.inf, None
    for i in range(9):
        if board[i] == " ":
            board[i] = ai
            score = minimax(board, False, ai, player)
            board[i] = " "
            if score > best:
                best, move = score, i
    if move is not None: board[move] = ai

# -------------------
# Game Renderer
# -------------------
def play_game(mode):
    st.subheader(f"Mode: {mode}")

    # Symbol selection
    if not st.session_state.symbol_chosen:
        st.session_state.player_symbol = st.radio("Choose your symbol:", ["X", "O"], horizontal=True)
        st.session_state.ai_symbol = "O" if st.session_state.player_symbol == "X" else "X"
        if st.button("Start Game"):
            st.session_state.symbol_chosen = True
            st.session_state.board = create_board()
            st.session_state.game_over = False
            st.session_state.pending_ai = False
            # If AI starts
            if st.session_state.player_symbol == "O":
                st.session_state.pending_ai = True
        if st.button("Back to Home"):
            st.session_state.page = "home"
        return

    # If AI move is pending → play it
    if "pending_ai" in st.session_state and st.session_state.pending_ai and not st.session_state.game_over:
        if mode == "Easy":
            easy_ai(st.session_state.board, st.session_state.ai_symbol)
        elif mode == "Intermediate":
            intermediate_ai(st.session_state.board, st.session_state.ai_symbol, st.session_state.player_symbol)
        else:
            hard_ai(st.session_state.board, st.session_state.ai_symbol, st.session_state.player_symbol)
        if check_winner(st.session_state.board, st.session_state.ai_symbol):
            st.write("AI wins!")
            st.session_state.game_over = True
        elif is_full(st.session_state.board):
            st.write("It's a tie!")
            st.session_state.game_over = True
        st.session_state.pending_ai = False

    # Render board
    cols = st.columns(3)
    board = st.session_state.board

    for i in range(9):
        display = board[i] if board[i] != " " else " "
        if board[i] == " " and not st.session_state.game_over:
            if cols[i % 3].button(" ", key=f"cell{i}"):
                board[i] = st.session_state.player_symbol
                if check_winner(board, st.session_state.player_symbol):
                    st.write("You win!")
                    st.session_state.game_over = True
                elif is_full(board):
                    st.write("It's a tie!")
                    st.session_state.game_over = True
                else:
                    # AI will move on the NEXT rerun
                    st.session_state.pending_ai = True
                st.rerun()  # Force refresh to display immediately
        else:
            cols[i % 3].button(display, key=f"cell{i}", disabled=True)

    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.session_state.symbol_chosen = False
        st.session_state.board = create_board()
        st.session_state.game_over = False

# -------------------
# Main App
# -------------------
st.set_page_config(page_title="Tic Tac Toe", layout="centered")
st.title("Tic Tac Toe")

# Init session vars
if "page" not in st.session_state:
    st.session_state.page = "home"
if "board" not in st.session_state:
    st.session_state.board = create_board()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "symbol_chosen" not in st.session_state:
    st.session_state.symbol_chosen = False

# Routing
if st.session_state.page == "home":
    st.header("Game Rules")
    st.markdown("""
    1. The game is played on a 3x3 grid.  
    2. Players take turns to mark a cell.  
    3. The first to align 3 marks wins.  
    4. If all cells are filled without a winner, it's a draw.  
    5. Have fun!
    """)

    st.write("Select Mode")
    col1, col2, col3 = st.columns(3)
    if col1.button("Easy"): 
        st.session_state.page = "easy"; st.session_state.symbol_chosen = False
    if col2.button("Intermediate"): 
        st.session_state.page = "intermediate"; st.session_state.symbol_chosen = False
    if col3.button("Hard"): 
        st.session_state.page = "hard"; st.session_state.symbol_chosen = False

elif st.session_state.page == "easy":
    play_game("Easy")
elif st.session_state.page == "intermediate":
    play_game("Intermediate")
elif st.session_state.page == "hard":
    play_game("Hard")
