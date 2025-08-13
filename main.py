import tkinter as tk
import webbrowser
from tkinter import messagebox

BOARD_SIZE = 8
SQUARE_SIZE = 60
SIDEBAR_WIDTH = 200

class CheckersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Checkers Game")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, width=BOARD_SIZE * SQUARE_SIZE, height=BOARD_SIZE * SQUARE_SIZE)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        self.sidebar_frame = tk.Frame(self.main_frame, width=SIDEBAR_WIDTH, bg="lightgray", padx=10, pady=10)
        self.sidebar_frame.grid(row=0, column=1, sticky="nswe")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.turn_label = tk.Label(self.sidebar_frame, text="Turn:", font=("Arial", 18, "bold"), bg="lightgray")
        self.turn_label.pack(pady=(20, 10))

        self.red_pieces_label = tk.Label(self.sidebar_frame, text="Red Pieces:", font=("Arial", 14), bg="lightgray")
        self.red_pieces_label.pack(pady=5)

        self.black_pieces_label = tk.Label(self.sidebar_frame, text="Black Pieces", font=("Arial", 14), bg="lightgray")
        self.black_pieces_label.pack(pady=5)

        self.message_label =  tk.Label(self.sidebar_frame, text="", font=("Arial", 12), bg="lightgray", fg="red", wraplength=SIDEBAR_WIDTH-20)
        self.message_label.pack(pady=(10, 20))

        self.reset_button = tk.Button(self.sidebar_frame, text="End Game", font=("Arial", 14, "bold"), command=self.display_draw_screen)
        self.reset_button.pack(pady=(10, 20))

        self.rules_button = tk.Button(
            self.sidebar_frame, text="Checkers Rules", font=("Arial", 14, "bold"),
            command=self.show_rules_popup
        )
        self.rules_button.pack(pady=(10,20))

        self.selected_piece = None
        self.pieces = {}
        self.turn = "red"
        self.multi_jump_piece = None

        self.draw_board()
        self.place_pieces()
        self.canvas.bind("<Button-1>", self.onclick)
        self.display_turn_text()
        self.update_piece_counts()

    def draw_board(self):
        self.canvas.delete("board_squares")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = "white" if (row + col) % 2 == 0 else "sienna"
                x1 = col * SQUARE_SIZE
                y1 = row * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="board_squares")

    def place_pieces(self):
        for row in range(3):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.pieces[(row, col)] = {"color": "black", "is_king": False}

        for row in range(5, 8):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.pieces[(row, col)] = {"color": "red", "is_king": False}

        self.redraw()

    def draw_piece(self, row, col, piece_data):
        color = piece_data["color"]
        is_king = piece_data["is_king"]

        x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        radius = SQUARE_SIZE // 2 - 8
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline="black", width=2, tags="pieces"
        )

        if is_king:
            radius = SQUARE_SIZE // 2 - 20
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill="gold", outline="black", width=1, tags="pieces"
            )

    def is_valid_move(self, from_pos, to_pos, forced_capture_required=False):
        if to_pos in self.pieces:
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        piece_data = self.pieces[from_pos]
        piece_color = piece_data["color"]
        is_king = piece_data["is_king"]
        opponent_color = "black" if piece_color == "red" else "red"

        row_diff = to_row - from_row
        col_diff = abs(to_col - from_col)

        if forced_capture_required and abs(row_diff) != 2:
            return False

        # Normal move and capture logic for non-king pieces
        # Corrected: Combined the logic to be more concise
        if not is_king:
            if piece_color == "red" and row_diff == -1 and col_diff == 1 and not forced_capture_required:
                return True
            elif piece_color == "black" and row_diff == 1 and col_diff == 1 and not forced_capture_required:
                return True
        
        # Logic for king moves (can move forward or backward)
        # Corrected: Kings can make any diagonal single move
        if is_king and abs(row_diff) == 1 and col_diff == 1:
            return True
            
        # Capture move logic (applies to both normal and king pieces)
        if abs(row_diff) == 2 and col_diff == 2:
            jump_row = (from_row + to_row) // 2
            jump_col = (from_col + to_col) // 2
            jumped_piece_pos = (jump_row, jump_col)

            if jumped_piece_pos in self.pieces and self.pieces[jumped_piece_pos]["color"] == opponent_color:
                return True
            
        return False
    
    def onclick(self, event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE

        if self.multi_jump_piece:
            from_pos = self.multi_jump_piece
            if not (self.is_valid_move(from_pos, (row, col)) and abs(row - from_pos[0]) == 2):
                self.show_message("You must continue jumping with the same piece")
                return
            else:
                self.clear_message()
        # Corrected: Accessing the color from the dictionary

        if not self.selected_piece and not self.multi_jump_piece:
            forced_capture_pieces = self.has_forced_capture(self.turn)
            if forced_capture_pieces and (row, col) not in  forced_capture_pieces:
                self.show_message("You must select a piece that can capture")
                return
            else:
                self.clear_message()
        
        forced_capture_pieces =  self.has_forced_capture(self.turn)
        forced_capture_required = len(forced_capture_pieces) > 0

        if self.selected_piece:
            if self.selected_piece == (row, col):
                if not self.multi_jump_piece:
                    self.selected_piece = None
                    self.redraw()
                    self.clear_message()
                else:
                    self.show_message("You must continue jumping with this piece")
                    return
            elif self.is_valid_move(self.selected_piece, (row, col), forced_capture_required):
                self.move_piece(self.selected_piece, (row, col))
                self.redraw()
                self.display_turn_text()
                self.update_piece_counts() # Corrected typo
                self.check_for_winner()
                self.clear_message()
            else:
                self.show_message("Invalid move.")
                if not self.multi_jump_piece:
                    self.selected_piece = None
                    self.redraw()
        else:
            if (row, col) in self.pieces and self.pieces[row,col]["color"] == self.turn:
                if self.multi_jump_piece and (row, col) != self.multi_jump_piece:
                    self.show_message("Must continue jumping with same piece")
                    return
                self.selected_piece = (row, col)
                # Corrected: Redraw everything to show the highlight, no need for highlight_selected_piece()
                self.redraw() 
                self.clear_message()
            else:
                self.show_message("Clicked empty square, no piece selected.")
    
    def move_piece(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        row_diff = abs(to_row - from_row)
        captured = False
        if row_diff == 2:
            captured_row = (from_row + to_row) // 2
            captured_col = (from_col + to_col) // 2
            captured_pos = (captured_row, captured_col)

            if captured_pos in self.pieces:
                del self.pieces[captured_pos]
                captured = True
        
        self.pieces[to_pos] = self.pieces.pop(from_pos)
        self.check_for_king(to_pos) # Check for king after move

        if captured and self.can_capture(to_pos):
            self.selected_piece = to_pos
            self.multi_jump_piece = to_pos
        else:
            self.selected_piece = None
            self.multi_jump_piece = None
            self.turn = "black" if self.turn == "red" else "red"

    def redraw(self):
        self.canvas.delete("all")
        self.draw_board()
        # Corrected: Iterating and passing the full piece_data dictionary
        for (row, col), piece_data in self.pieces.items():
            self.draw_piece(row, col, piece_data)
            
        if self.selected_piece:
            row, col = self.selected_piece
            x1 = col * SQUARE_SIZE
            y1 = row * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=4, tags="highlight")
            self.canvas.tag_raise("pieces")

            valid_moves = self.get_valid_moves(self.selected_piece)
            for move_row, move_col in valid_moves:
                cx = move_col * SQUARE_SIZE + SQUARE_SIZE // 2
                cy = move_row * SQUARE_SIZE + SQUARE_SIZE // 2
                radius = 10
                self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="yellow", outline="", tags="move_highlight")

        self.display_turn_text()
        self.update_piece_counts()

    def display_turn_text(self):
        self.turn_label.config(text=f"Turn: {self.turn.capitalize()}")

    def update_piece_counts(self):
        # Corrected: Summing up based on the color key in the piece dictionaries
        red_count = sum(1 for piece in self.pieces.values() if piece["color"] == "red")
        black_count = sum(1 for piece in self.pieces.values() if piece["color"] == "black")
        self.red_pieces_label.config(text=f"Red Pieces: {red_count}")
        self.black_pieces_label.config(text=f"Black Pieces: {black_count}")

    def check_for_winner(self):
        red_pieces = sum(1 for piece in self.pieces.values() if piece["color"] == "red")
        black_pieces = sum(1 for piece in self.pieces.values() if piece["color"] == "black")

        if red_pieces == 0:
            self.display_win_screen("black")
        elif black_pieces == 0:
            self.display_win_screen("red")

        red_moves = self.has_any_valid_moves("red")
        black_moves = self.has_any_valid_moves("black")

        if not red_moves and black_moves:
            self.display_draw_screen()
            return
        elif not black_moves and red_moves:
            self.display_draw_screen()
            return
        elif not red_moves and not black_moves:
            self.display_draw_screen()
            return
    
    def has_any_valid_moves(self, color):
        
        for from_pos, piece_data in self.pieces.items():
            if piece_data["color"] != color:
                continue
            
            for dr in [-1,1]:
                for dc in [-1,1]:
                    for step in [1,2]:
                        to_row = from_pos[0] + dr * step
                        to_col = from_pos[1] + dc * step
                        to_pos = (to_row, to_col)

                        if 0 <= to_row < BOARD_SIZE and 0 <= to_col < BOARD_SIZE:
                            forced_capture_required = len(self.has_forced_capture(color)) > 0
                            if self.is_valid_move(from_pos, to_pos, forced_capture_required):
                                return True
        return False
    def display_win_screen(self, winner):
        self.canvas.delete("all")
        winner_color = winner.capitalize()
        text = f"{winner_color} Wins!"

        self.main_frame.destroy()

        self.win_screen_canvas = tk.Canvas(self.root, width=BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH + 20, height=BOARD_SIZE * SQUARE_SIZE + 20, bg="lightgray")
        self.win_screen_canvas.pack(fill=tk.BOTH, expand=True)

        self.win_screen_canvas.create_text(
            (BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH + 20) / 2,
            (BOARD_SIZE * SQUARE_SIZE + 20) / 2,
            text=text,
            font=("Arial", 48, "bold"),
            fill=winner,
            tags="win_screen"
        )

        play_again_button = tk.Button(self.win_screen_canvas, text="Play Again", font=("Arial", 20), command=self.reset_game)
        self.win_screen_canvas.create_window(
            (BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH + 20) / 2,
            (BOARD_SIZE * SQUARE_SIZE + 20) / 2 + 80,
            window=play_again_button
        )
    
    def reset_game(self):
        self.win_screen_canvas.destroy()
        self.__init__(self.root)

    def reset_game_draw(self):
        self.draw_screen_canvas.destroy()
        self.__init__(self.root)

    def check_for_king(self, to_pos):
        row, col = to_pos
        # Check if the piece still exists at to_pos after a potential capture in a multi-jump
        if to_pos not in self.pieces:
            return

        piece = self.pieces[to_pos]

        if piece["color"] == "red" and row == 0:
            if not piece["is_king"]:
                piece["is_king"] = True
        
        if piece["color"] == "black" and row == BOARD_SIZE - 1:
            if not piece["is_king"]:
                piece["is_king"] = True
    def can_capture(self, pos):
        if pos not in self.pieces:
            return False
        
        row, col = pos
        piece = self.pieces[pos]
        color = piece["color"]
        opponent_color = "black" if color == "red" else "red"
        is_king = piece["is_king"]

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            if not is_king:
                if color == "red" and dr != -1:
                    continue
                if color == "black" and dr != 1:
                    continue
            mid_row = row + dr
            mid_col = col + dc
            jump_row = row + 2 * dr
            jump_col = col + 2 * dc

            if (0 <= mid_row < BOARD_SIZE and 0 <= mid_col < BOARD_SIZE and
                0 <= jump_row < BOARD_SIZE and 0 <= jump_col < BOARD_SIZE):
                
                mid_pos = (mid_row, mid_col)
                jump_pos = (jump_row, jump_col)

                if (mid_pos in self.pieces and
                    self.pieces[mid_pos]["color"] == opponent_color and
                    jump_pos not in self.pieces):
                    return True
        return False
    def has_forced_capture(self, color):
        forced_pieces = []
        for pos, piece_dadta in self.pieces.items():
            if piece_dadta["color"] == color and self.can_capture(pos):
                if self.can_capture(pos):
                    forced_pieces.append(pos)
        return forced_pieces

    def display_draw_screen(self):
        self.canvas.delete("all")
        self.main_frame.destroy()

        self.draw_screen_canvas = tk.Canvas(self.root, width=BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH + 20,
                                            height=BOARD_SIZE * SQUARE_SIZE + 20, bg="lightgray")
        self.draw_screen_canvas.pack(fill=tk.BOTH, expand=True)

        self.draw_screen_canvas.create_text(
            (BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH + 20) / 2,
            (BOARD_SIZE * SQUARE_SIZE + 20) / 2,
            text="Draw!",
            font=("Arial", 48, "bold"),
            fill="gray",
            tags="draw_screen"
        )

        play_again_button = tk.Button(self.draw_screen_canvas, text="Play Again", font=("Arial", 20), command=self.reset_game_draw)
        self.draw_screen_canvas.create_window(
            (BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH + 20) /2,
            (BOARD_SIZE * SQUARE_SIZE + 20)  / 2 + 80,
            window=play_again_button
        )

    def show_message(self, text):
        self.message_label.config(text=text)

    def clear_message(self):
        self.message_label.config(text="")

    def get_valid_moves(self, from_pos):
        forced_capture_pieces = self.has_forced_capture(self.turn)
        forced_capture_required = len(forced_capture_pieces) > 0
        moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                to_pos = (row, col)
                if self.is_valid_move(from_pos, to_pos, forced_capture_required):
                    moves.append(to_pos)
        return moves

    def show_rules_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Checkers Rules")

        label = tk.Label(
            popup,
            text="Don't know the rules for checkers?\n Learn the official Checkers rules by visiting\n\n"
                 "https://officialgamerules.org/game-rules/checkers/",
            font=("Arial", 12), justify="center", padx=20, pady=20
        )
        label.pack()

        def open_link():
            webbrowser.open("https://officialgamerules.org/game-rules/checkers/")
            
        open_link_button = tk.Button(popup, text="Open Rules Website", command=open_link)
        open_link_button.pack(pady=(0,20))
                              
        close_button = tk.Button(popup, text="Close", command=popup.destroy, fg="red")
        close_button.pack(pady=(0, 20))

    # Testing
    def setup_draw_scenario(self):
        # Clear all pieces
        self.pieces.clear()
        # Place a few pieces for both players stuck blocking each other
        # Example blocking layout:
        # Black pieces at (2,1), (2,3)
        # Red pieces at (3,0), (3,2)
        self.pieces[(1,0)] = {"color": "black", "is_king": False}
        self.pieces[(3,0)] = {"color": "red", "is_king": False}
        self.pieces[(3,2)] = {"color": "red", "is_king": False}
        self.pieces[(5,2)] = {"color": "red", "is_king" : False}

        self.turn = "red"
        self.redraw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CheckersApp(root)
    root.mainloop()