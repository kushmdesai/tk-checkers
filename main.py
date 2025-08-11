import tkinter as tk

BOARD_SIZE = 8
SQUARE_SIZE = 60

class CheckersApp:
    def __init__(self, root):
        # turn_text = root.render(f"Turn: {self.turn}", True, (255,255,255))
        # screen.blit(turn_text, (10, 10))
        self.root = root
        self.root.title("Checkers Game")

        self.canvas = tk.Canvas(root, width=BOARD_SIZE * SQUARE_SIZE, height=BOARD_SIZE * SQUARE_SIZE)
        self.canvas.pack()

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
                    self.pieces[(row, col)] = "black"

        for row in range(5,8):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.pieces[(row, col)] = "red"

        self.redraw()

    def draw_piece(self, row, col, color):
        x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        radius = SQUARE_SIZE // 2 - 8
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline="black", width=2, tags="pieces"
        )
    def is_valid_move(self, from_pos, to_pos):
        if to_pos in self.pieces:
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        if abs(to_col - from_col) != 1:
            return False
        
        piece_color = self.pieces[from_pos]

        if piece_color == "red":
            if to_row != from_row - 1:
                return False
        else:
            if to_row != from_row + 1:
                return False
            
        return True
    
    def onclick(self, event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        print(f"Clicked row: {row}, col: {col}")

        if (row, col) in self.pieces and self.pieces[(row,col)] != self.turn:
            print(f"It's {self.turn}'s turn, you can't move {self.pieces[(row, col)]}'s piece.") # <-- Added a more descriptive message
            return

        if self.selected_piece:
            if self.selected_piece == (row, col):
                self.selected_piece = None
                self.redraw()
            elif self.is_valid_move(self.selected_piece, (row, col)):
                self.move_piece(self.selected_piece, (row, col))
                self.selected_piece = None
                self.turn = "black" if self.turn == "red" else "red"
                self.redraw()
                self.display_turn_text()
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
        for (row, col), color in self.pieces.items():
            self.draw_piece(row, col, color)
        self.highlight_selected_piece()
        self.display_turn_text()

    def display_turn_text(self):
        self.canvas.delete("turn_text")

        text_id = self.canvas.create_text(
            10,10,
            text=f'Turn: {self.turn.capitalize()}',
            anchor="nw",
            font=("Arial", 16),
            fill="black",
            tags="turn_text"
        )
        self.canvas.tag_raise(text_id)
if __name__ == "__main__":
    root = tk.Tk()
    app = CheckersApp(root)
    root.mainloop()