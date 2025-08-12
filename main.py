import tkinter as tk

BOARD_SIZE = 8
SQUARE_SIZE = 60
SIDEBAR_WIDTH = 200

class CheckersApp:
    def __init__(self, root):
        # turn_text = root.render(f"Turn: {self.turn}", True, (255,255,255))
        # screen.blit(turn_text, (10, 10))
        # turn_text = root.render(f"Turn: {self.turn}", True, (255,255,255))
        # screen.blit(turn_text, (10, 10))
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

        self.selected_piece = None
        self.pieces = {}
        self.turn = "red"

        self.draw_board()
        self.place_pieces()
        print("Initial pieces:", self.pieces.keys())
        self.canvas.bind("<Button-1>", self.onclick)
        self.display_turn_text()

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
                if  (row + col) % 2 == 1:
                    self.pieces[(row, col)] = {"color": "black", "is_king": False}

        for row in range(5,8):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.pieces[(row, col)] = {"color":"red", "is_king": False}

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
            fill=color, outline="black", width=2, tags="pieces"
        )

        if is_king:
            radius = SQUARE_SIZE // 2-20
            x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            self.canvas.create_oval(
                x - radius, y-radius, x + radius, y + radius,
                fill="gold", outline="black", width=1, tags="pieces"
            )
    def is_valid_move(self, from_pos, to_pos):
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

        if not is_king:
            if piece_color == "red" and to_row == from_row - 1 and abs(to_col - from_col) == 1:
                return True
            elif piece_color == "black" and to_row == from_row + 1 and abs(to_col - from_col) == 1:
                return True
        
        if is_king:
            if col_diff == 1 and abs(row_diff) == 1:
                return True
        
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
        print(f"Clicked row: {row}, col: {col}")

        if (row, col) in self.pieces and self.pieces[(row,col)]["color"] != self.turn:
            print(f"It's {self.turn}'s turn, you can't move {self.pieces[(row, col)]}'s piece.") # <-- Added a more descriptive message
            return

        if self.selected_piece:
            if self.selected_piece == (row, col):
                self.selected_piece = None
                self.redraw()
            elif self.is_valid_move(self.selected_piece, (row, col)):
                self.move_piece(self.selected_piece, (row, col))
                self.check_for_king(to_pos=(row, col))
                self.selected_piece = None
                self.turn = "black" if self.turn == "red" else "red"
                self.redraw()
                self.display_turn_text()
                self.updtade_piece_counts()
                self.check_for_winner()
            else:
                print("Invalid move. Deslecting piece")
                self.selected_piece = None
                self.redraw()
        else:
            if (row, col) in self.pieces:
                self.selected_piece = (row, col)
                self.highlight_selected_piece()
            else:
                print("Clicked empty square, no piece selected")
    
    def move_piece(self, from_pos, to_pos):
        print(f"Moving pieace from {from_pos} to {to_pos}")
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        row_diff = abs(to_row - from_row)

        if row_diff == 2:
            captured_row = (from_row + to_row) // 2
            captured_col = (from_col + to_col) // 2
            captured_pos = (captured_row, captured_col)

            if captured_pos in self.pieces:
                del self.pieces[captured_pos]
                print(f"Captured piece at {captured_pos}")
        self.pieces[to_pos] = self.pieces.pop(from_pos)

    def highlight_selected_piece(self):
        if self.selected_piece:
            row, col = self.selected_piece
            x1 = col * SQUARE_SIZE
            y1 = row * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=4, tags="highlight")
            self.canvas.tag_raise("pieces")

    def redraw(self):
        self.canvas.delete("all")
        self.draw_board()
        for (row, col), piece_data in self.pieces.items():
            self.draw_piece(row, col, piece_data)
        self.highlight_selected_piece()
        self.display_turn_text()

    def display_turn_text(self):
        self.turn_label.config(text=f"Turn: {self.turn.capitalize()}")

    def check_for_winner(self):
        red_pieces = sum(1 for color in self.pieces.values() if color == "red")
        black_pieces = sum(1 for color in self.pieces.values() if color == "black")

        if red_pieces == 0:
            self.display_win_screen("black")
        elif black_pieces == 0:
            self.display_win_screen("red")

    def display_win_screen(self, winner):
        self.canvas.delete("all")
        winner_color = winner.capitalize()
        text = f"{winner_color} Wins!"

        self.main_frame.destroy()

        self.win_screen_canvas = tk.Canvas(self.root, width=BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH + 20, height=BOARD_SIZE * SQUARE_SIZE + 20, bg="lightgray")
        self.win_screen_canvas.pack(fill=tk.BOTH, expand=True)

        self.win_screen_canvas.create_text(
            (BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH + 20)/ 2,
            (BOARD_SIZE * SQUARE_SIZE + 20) / 2,
            text=text,
            font=("Arial", 48, "bold"),
            fill=winner,
            tags="win_screen"
        )

        play_again_button = tk.Button(self.win_screen_canvas, text="Play Again", font=("Arial", 20), command=self.reset_game)
        self.win_screen_canvas.create_window(
            (BOARD_SIZE * SQUARE_SIZE + SIDEBAR_WIDTH + 20) / 2,
            (BOARD_SIZE * SQUARE_SIZE + 20) /2 + 80,
            window=play_again_button
        )
    def reset_game(self):

        self.win_screen_canvas.destroy()

        self.__init__(self.root)

    def updtade_piece_counts(self):
        red_count = sum(1 for color in self.pieces.values() if color == "red")
        black_count = sum(1 for color in self.pieces.values() if color == "black")
        self.red_pieces_label.config(text=f"Red Pieces: {red_count}")
        self.black_pieces_label.config(text=f"Black Pieces: {black_count}")

    def check_for_king(self, to_pos):
        row, col = to_pos
        piece = self.pieces[to_pos]

        if piece["color"] == "red" and row == 0:
            if not piece["is_king"]:
                piece["is_king"] = True
                print("Red piece is now king")

        if piece["color"] == "black" and row == BOARD_SIZE - 1:
            if not piece["is_king"]:
                piece["is_king"] = True
                print("Black piece is now king")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = CheckersApp(root)
    root.mainloop()