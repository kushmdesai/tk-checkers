import tkinter as tk

BOARD_SIZE = 8
SQUARE_SIZE = 60

class CheckersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Checkers Game")

        self.canvas = tk.Canvas(root, width=BOARD_SIZE * SQUARE_SIZE, height=BOARD_SIZE * SQUARE_SIZE)
        self.canvas.pack()

        self.selected_piece = None

        self.draw_board()
        self.place_pieces()
        
        self.canvas.bind("<Button-1>", self.onclick)

    def draw_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = "white" if (row + col) % 2 == 0 else "sienna"
                x1 = col * SQUARE_SIZE
                y1 = row * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    def place_pieces(self):
        self.pieces = {}
        for row in range(3):
            for col in range(BOARD_SIZE):
                if  (row + col) % 2 == 1:
                    self.draw_piece(row, col, "black")
                    self.pieces[(row, col)] = "black"

        for row in range(5,8):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.draw_piece(row, col, "red")
                    self.pieces[(row, col)] = "red"

    def draw_piece(self, row, col, color):
        x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        radius = SQUARE_SIZE // 2 - 8
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline="black", width=2
        )
    def onclick(self, event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE

        if (row, col) in self.pieces:
            self.selected_piece = (row, col)
            self.highlight_selected_piece()
        else:
            self.selected_piece = None
            self.draw_board()
            self.redraw_pieces()
    
    def highlight_selected_piece(self):
        self.draw_board()
        self.redraw_pieces()
        if self.selected_piece:
            row, col = self.selected_piece
            x1 = col * SQUARE_SIZE
            y1 = row * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=4)

    def redraw_pieces(self):
        for (row, col), color in self.pieces.items():
            self.draw_piece(row, col, color)

if __name__ == "__main__":
    root = tk.Tk()
    app = CheckersApp(root)
    root.mainloop()