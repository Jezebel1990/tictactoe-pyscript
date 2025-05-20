from js import document, window
from pyodide.ffi import create_proxy

class TicTacToe:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.status = document.getElementById("status")
        self.click_proxies = []
        self.update_status()
        self.render_board()
        self.add_event_listeners()

    def update_status(self):
        self.status.innerText = f"Vez de {self.current_player}"

    def render_board(self):
        for x in range(3):
            for y in range(3):
                cell = document.getElementById(f"cell{x}{y}")
                value = self.board[x][y]
                cell.innerText = value
                cell.classList.remove("x", "o", "win")
                cell.style.backgroundColor = ""

                if value == "X":
                    cell.classList.add("x")
                elif value == "O":
                    cell.classList.add("o")

    def add_event_listeners(self):
        for x in range(3):
            for y in range(3):
                cell = document.getElementById(f"cell{x}{y}")
                proxy = create_proxy(self.click)
                self.click_proxies.append(proxy)
                cell.addEventListener("click", proxy)

    def check_winner(self):
        b = self.board
        lines = [
            [(0,0), (0,1), (0,2)],
            [(1,0), (1,1), (1,2)],
            [(2,0), (2,1), (2,2)],
            [(0,0), (1,0), (2,0)],
            [(0,1), (1,1), (2,1)],
            [(0,2), (1,2), (2,2)],
            [(0,0), (1,1), (2,2)],
            [(0,2), (1,1), (2,0)],
        ]
        for line in lines:
            values = [b[x][y] for x, y in line]
            if values[0] != "" and all(val == values[0] for val in values):
                return values[0], line
        return None, None

    def is_draw(self):
        return all(cell != "" for row in self.board for cell in row)

    def click(self, event):
        x = int(event.target.getAttribute("data-x"))
        y = int(event.target.getAttribute("data-y"))

        if self.board[x][y] != "":
            return

        self.board[x][y] = self.current_player
        self.render_board()

        winner, winning_cells = self.check_winner()
        if winner:
            self.status.innerText = f"Vitória de {winner}!"
            for x, y in winning_cells:
                cell = document.getElementById(f"cell{x}{y}")
                cell.classList.add("win")

            def keep_win_effect():
                for x, y in winning_cells:
                    cell = document.getElementById(f"cell{x}{y}")
                    cell.style.backgroundColor = "yellow"

            proxy = create_proxy(keep_win_effect)
            window.setTimeout(proxy, 1000)
            self.click_proxies.append(proxy)
            return

        elif self.is_draw():
            self.status.innerText = "Empate!"
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_status()

    def new_game(self, event=None): 
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.update_status()
        self.render_board()

# Instancia o jogo e exporta no escopo global
GAME = TicTacToe()
window.GAME = GAME