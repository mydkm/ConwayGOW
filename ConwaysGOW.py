import argparse
import tkinter as tk


def index_to_letters(index: int) -> str:
    """
    Convert 0 -> A, 1 -> B, ..., 25 -> Z, 26 -> AA, etc.
    """
    result = ""
    index += 1
    while index > 0:
        index -= 1
        result = chr(ord("A") + (index % 26)) + result
        index //= 26
    return result


class GameOfLifeApp:
    def __init__(self, root: tk.Tk, n: int, two_player: bool = False):
        self.root = root
        self.n = n
        self.two_player = two_player
        self.time_step = 0

        # Board state:
        # 0 = dead
        # 1 = player 1
        # 2 = player 2
        self.board = [[0 for _ in range(n)] for _ in range(n)]

        # In two-player mode, mouse clicks place/toggle the selected player
        self.active_player = 1

        # Visual settings
        self.cell_size = max(24, min(60, 520 // max(1, n)))
        self.left_margin = 50
        self.top_margin = 50
        self.grid_width = self.n * self.cell_size
        self.grid_height = self.n * self.cell_size
        self.canvas_width = self.left_margin + self.grid_width + 10
        self.canvas_height = self.top_margin + self.grid_height + 10

        self.dead_color = "white"
        self.player1_color = "crimson"
        self.player2_color = "royalblue"
        self.grid_line_color = "gray40"

        mode_text = "Two-Player" if self.two_player else "Single-Player"
        self.root.title(f"Conway's Game of Life ({self.n}x{self.n}) - {mode_text}")
        self.root.resizable(False, False)

        # UI text variables
        self.time_var = tk.StringVar(value=f"Time Step: {self.time_step}")
        self.mode_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.update_mode_text()
        self.update_status_text()

        self.build_ui()
        self.draw_grid()

        # Key bindings for advancing
        self.root.bind("<Return>", self.advance_from_event)
        self.root.bind("<KeyPress-r>", self.advance_from_event)
        self.root.bind("<KeyPress-R>", self.advance_from_event)

        # Key bindings for player selection in two-player mode
        if self.two_player:
            self.root.bind("<KeyPress-1>", self.select_player_1)
            self.root.bind("<KeyPress-2>", self.select_player_2)

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(padx=10, pady=(10, 4), fill="x")

        time_label = tk.Label(
            top_frame,
            textvariable=self.time_var,
            font=("Arial", 12, "bold")
        )
        time_label.pack(side="left")

        self.advance_button = tk.Button(
            top_frame,
            text="R Enter",
            font=("Arial", 11),
            command=self.advance
        )
        self.advance_button.pack(side="right")

        info_frame = tk.Frame(self.root)
        info_frame.pack(padx=10, pady=(0, 4), fill="x")

        mode_label = tk.Label(
            info_frame,
            textvariable=self.mode_var,
            font=("Arial", 10, "bold"),
            anchor="w",
            justify="left"
        )
        mode_label.pack(side="left")

        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=4)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 10),
            anchor="w",
            justify="left"
        )
        status_label.pack(padx=10, pady=(4, 10), fill="x")

        # Rectangle IDs for quick redraw
        self.rect_ids = [[None for _ in range(self.n)] for _ in range(self.n)]

    def update_mode_text(self):
        if self.two_player:
            player_name = "Player 1" if self.active_player == 1 else "Player 2"
            player_color = "Crimson" if self.active_player == 1 else "Blue"
            self.mode_var.set(
                f"Mode: Two-Player | Active placement: {player_name} ({player_color}) | Keys: 1 / 2"
            )
        else:
            self.mode_var.set("Mode: Single-Player")

    def update_status_text(self):
        if self.two_player:
            self.status_var.set(
                "Click to place/toggle the selected player's cell. "
                "Press 1 for Player 1, 2 for Player 2. Use R or Enter to advance."
            )
        else:
            self.status_var.set(
                "Click cells to toggle them on/off. Use R or Enter to advance."
            )

    def draw_grid(self):
        self.canvas.delete("all")

        # Column labels: 1, 2, 3, ...
        for col in range(self.n):
            x_center = self.left_margin + col * self.cell_size + self.cell_size / 2
            self.canvas.create_text(
                x_center,
                self.top_margin / 2,
                text=str(col + 1),
                font=("Arial", 11, "bold")
            )

        # Row labels: A, B, C, ...
        for row in range(self.n):
            y_center = self.top_margin + row * self.cell_size + self.cell_size / 2
            self.canvas.create_text(
                self.left_margin / 2,
                y_center,
                text=index_to_letters(row),
                font=("Arial", 11, "bold")
            )

        # Grid cells
        for row in range(self.n):
            for col in range(self.n):
                x1 = self.left_margin + col * self.cell_size
                y1 = self.top_margin + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                fill_color = self.owner_to_color(self.board[row][col])

                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill_color,
                    outline=self.grid_line_color,
                    width=1
                )
                self.rect_ids[row][col] = rect_id

    def owner_to_color(self, owner: int) -> str:
        if owner == 1:
            return self.player1_color
        if owner == 2:
            return self.player2_color
        return self.dead_color

    def on_canvas_click(self, event):
        col = (event.x - self.left_margin) // self.cell_size
        row = (event.y - self.top_margin) // self.cell_size

        if not (0 <= row < self.n and 0 <= col < self.n):
            return

        if not self.two_player:
            self.board[row][col] = 0 if self.board[row][col] else 1
        else:
            current = self.board[row][col]

            # Two-player placement logic:
            # dead -> active player
            # own cell -> dead
            # opponent cell -> active player
            if current == self.active_player:
                self.board[row][col] = 0
            else:
                self.board[row][col] = self.active_player

        self.update_cell_visual(row, col)

    def update_cell_visual(self, row: int, col: int):
        fill_color = self.owner_to_color(self.board[row][col])
        self.canvas.itemconfig(self.rect_ids[row][col], fill=fill_color)

    def select_player_1(self, event=None):
        if self.two_player:
            self.active_player = 1
            self.update_mode_text()

    def select_player_2(self, event=None):
        if self.two_player:
            self.active_player = 2
            self.update_mode_text()

    def advance_from_event(self, event):
        self.advance()

    def neighbor_positions(self, row: int, col: int):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr = row + dr
                cc = col + dc
                if 0 <= rr < self.n and 0 <= cc < self.n:
                    yield rr, cc

    def count_live_neighbors(self, row: int, col: int, board=None) -> int:
        if board is None:
            board = self.board
        count = 0
        for rr, cc in self.neighbor_positions(row, col):
            if board[rr][cc] != 0:
                count += 1
        return count

    def count_owner_neighbors(self, row: int, col: int, owner: int, board=None) -> int:
        if board is None:
            board = self.board
        count = 0
        for rr, cc in self.neighbor_positions(row, col):
            if board[rr][cc] == owner:
                count += 1
        return count

    def same_owner_degree(self, row: int, col: int, board=None) -> int:
        """
        Degree of the cell in the graph formed by cells of the same owner,
        with adjacency defined by the 8 neighboring positions.
        """
        if board is None:
            board = self.board

        owner = board[row][col]
        if owner == 0:
            return 0

        degree = 0
        for rr, cc in self.neighbor_positions(row, col):
            if board[rr][cc] == owner:
                degree += 1
        return degree

    def get_birth_owner(self, row: int, col: int, board) -> int:
        """
        Decide who owns a newly born cell.
        Rule used here: majority owner among the 3 live neighbors.
        """
        p1_neighbors = self.count_owner_neighbors(row, col, 1, board)
        p2_neighbors = self.count_owner_neighbors(row, col, 2, board)

        if p1_neighbors > p2_neighbors:
            return 1
        if p2_neighbors > p1_neighbors:
            return 2

        # In standard GOL birth there are exactly 3 neighbors, so an exact tie
        # should not occur with only two players. Leave dead as a safeguard.
        return 0

    def compute_two_player_base_generation(self, board):
        """
        First apply ordinary Conway-style birth/survival,
        treating both players' cells as "live".
        Ownership is preserved on survival and chosen by local majority on birth.
        """
        new_board = [[0 for _ in range(self.n)] for _ in range(self.n)]

        for row in range(self.n):
            for col in range(self.n):
                live_neighbors = self.count_live_neighbors(row, col, board)
                owner = board[row][col]

                if owner != 0:
                    # Survive as the same owner under standard GOL
                    if live_neighbors in (2, 3):
                        new_board[row][col] = owner
                    else:
                        new_board[row][col] = 0
                else:
                    # Birth under standard GOL
                    if live_neighbors == 3:
                        new_board[row][col] = self.get_birth_owner(row, col, board)
                    else:
                        new_board[row][col] = 0

        return new_board

    def compute_takeover_owner(self, row: int, col: int, board):
        """
        Competitive takeover logic for a currently occupied cell.

        Rule 1: Encirclement
            If a player's cell has 5 or more adjacent enemy cells,
            it becomes the enemy next turn.

        Rule 2: Degree duel
            If the cell is adjacent to at least one enemy cell whose same-team
            degree is strictly greater than its own same-team degree,
            it becomes the enemy next turn.

        Returns:
            0 if no takeover,
            1 or 2 if the cell should flip to that player.
        """
        owner = board[row][col]
        if owner == 0:
            return 0

        enemy = 2 if owner == 1 else 1

        # Rule 1: encirclement
        enemy_count = self.count_owner_neighbors(row, col, enemy, board)
        if enemy_count >= 5:
            return enemy

        # Rule 2: degree duel
        my_degree = self.same_owner_degree(row, col, board)
        enemy_degrees = []

        for rr, cc in self.neighbor_positions(row, col):
            if board[rr][cc] == enemy:
                enemy_degrees.append(self.same_owner_degree(rr, cc, board))

        if enemy_degrees and max(enemy_degrees) > my_degree:
            return enemy

        return 0

    def next_generation(self):
        if not self.two_player:
            # Original single-player behavior
            new_board = [[0 for _ in range(self.n)] for _ in range(self.n)]

            for row in range(self.n):
                for col in range(self.n):
                    neighbors = self.count_live_neighbors(row, col)

                    if self.board[row][col] == 1:
                        if neighbors in (2, 3):
                            new_board[row][col] = 1
                        else:
                            new_board[row][col] = 0
                    else:
                        if neighbors == 3:
                            new_board[row][col] = 1
                        else:
                            new_board[row][col] = 0

            self.board = new_board
            return

        # Two-player behavior
        old_board = [row[:] for row in self.board]

        # Step 1: standard Conway-style base update
        new_board = self.compute_two_player_base_generation(old_board)

        # Step 2: apply competitive takeovers based on the old board
        # Takeover overrides the ordinary Conway result for currently occupied cells.
        for row in range(self.n):
            for col in range(self.n):
                if old_board[row][col] != 0:
                    takeover_owner = self.compute_takeover_owner(row, col, old_board)
                    if takeover_owner != 0:
                        new_board[row][col] = takeover_owner

        self.board = new_board

    def advance(self):
        self.next_generation()
        self.time_step += 1

        self.time_var.set(f"Time Step: {self.time_step}")

        # Redraw all cells
        for row in range(self.n):
            for col in range(self.n):
                self.update_cell_visual(row, col)


def parse_args():
    parser = argparse.ArgumentParser(description="Conway's Game of Life GUI")
    parser.add_argument(
        "-n",
        "--size",
        type=int,
        default=8,
        help="Grid size n for an n x n board (default: 8)"
    )
    parser.add_argument(
        "--two-player",
        action="store_true",
        help="Enable two-player mode"
    )
    args = parser.parse_args()

    if args.size <= 0:
        parser.error("Grid size must be a positive integer.")

    return args


def main():
    args = parse_args()
    root = tk.Tk()
    app = GameOfLifeApp(root, args.size, two_player=args.two_player)
    root.mainloop()


if __name__ == "__main__":
    main()