from js import document, localStorage, console
from pyodide.ffi import create_proxy
import json
from matplotlib import pyplot as plt
from pyscript import display

class TicTacToe:
    def __init__(self):
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.status = document.getElementById("status")
        self.graph_output = document.getElementById("graph-output")

        # Inicializa localStorage
        if localStorage.getItem("ultimos_jogos") is None:
            localStorage.setItem("ultimos_jogos", json.dumps([]))

        self.scores = {"X": 0, "O": 0, "Empate": 0}
        self.proxies = []
        self.setup_new_game_button()
        self.create_board()
        self.load_scores_from_history()
        self.update_scoreboard()
        self.update_status()
        self.plot_chart()

    def create_board(self):
        for x in range(3):
            for y in range(3):
                cell = document.getElementById(f"cell{x}{y}")
                cell.textContent = ""
                proxy = create_proxy(lambda e, x=x, y=y: self.click(e, x, y))
                cell.addEventListener("click", proxy)
                self.proxies.append(proxy)

    def click(self, event, x, y):
        if self.board[x][y] == "":
            self.board[x][y] = self.current_player
            cell = document.getElementById(f"cell{x}{y}")
            cell.textContent = self.current_player

        if self.current_player == "X":
            cell.classList.add("x")
        else:
            cell.classList.add("o")

        if self.check_winner():
            self.status.textContent = f"{self.current_player} 🏆 venceu!"
            self.save_result(self.current_player)
            self.load_scores_from_history()
            self.update_scoreboard()
            self.plot_chart()
            return
        elif self.is_draw():
            self.status.textContent = "⚖️ Empate!"
            self.save_result("Empate")
            self.load_scores_from_history()
            self.update_scoreboard()
            self.plot_chart()
            return
        self.current_player = "O" if self.current_player == "X" else "X"
        self.update_status()

    def update_status(self):
        self.status.textContent = f"Vez de {self.current_player}"

    def is_draw(self):
        return all(cell != "" for row in self.board for cell in row)

    def check_winner(self):
        b = self.board
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] != "":
                self.mark_winner_cells([(i, 0), (i, 1), (i, 2)])
                return True
            if b[0][i] == b[1][i] == b[2][i] != "":
                self.mark_winner_cells([(0, i), (1, i), (2, i)])
                return True
        if b[0][0] == b[1][1] == b[2][2] != "":
            self.mark_winner_cells([(0, 0), (1, 1), (2, 2)])
            return True
        if b[0][2] == b[1][1] == b[2][0] != "":
            self.mark_winner_cells([(0, 2), (1, 1), (2, 0)])
            return True
        return False
    
    def mark_winner_cells(self, cells):
        for x, y in cells:
            cell = document.getElementById(f"cell{x}{y}")
            cell.classList.add("win")

    def setup_new_game_button(self):
        btn = document.getElementById("btn-new-game")
        proxy = create_proxy(self.new_game)
        btn.addEventListener("click", proxy)
        self.proxies.append(proxy)

    def new_game(self, *args):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        for x in range(3):
            for y in range(3):
                cell = document.getElementById(f"cell{x}{y}")
                cell.textContent = ""
                cell.classList.remove("x", "o", "win")  
        self.update_status()

    def save_result(self, result):
        raw_data = localStorage.getItem("ultimos_jogos")
        try:
            results = json.loads(raw_data) if raw_data else []
        except json.JSONDecodeError:
            results = []

        results.append(result)

        if len(results) > 3:
            # Reinicia a contagem após 3 partidas
            results = [result]

        localStorage.setItem("ultimos_jogos", json.dumps(results))

    def load_scores_from_history(self):
        raw_data = localStorage.getItem("ultimos_jogos")
        try:
            results = json.loads(raw_data) if raw_data else []
        except json.JSONDecodeError:
            results = []
            localStorage.setItem("ultimos_jogos", json.dumps([]))

        self.scores = {
            "X": results.count("X"),
            "O": results.count("O"),
            "Empate": results.count("Empate")
        }

    def update_scoreboard(self):
        document.getElementById("score-x").textContent = str(self.scores["X"])
        document.getElementById("score-o").textContent = str(self.scores["O"])
        document.getElementById("score-draw").textContent = str(self.scores["Empate"])

    def plot_chart(self):
        while self.graph_output.firstChild:
            self.graph_output.removeChild(self.graph_output.firstChild)

        players = ['X', 'O', 'Empate']
        punctuation = [self.scores["X"], self.scores["O"], self.scores["Empate"]]
        colors = ['#DF2E38', '#0118D8', '#888888']

        fig, ax = plt.subplots(figsize=(4, 3))

        # ax.set_title("Placar: Melhor de 3 jogos")
        ax.set_ylabel("Vitórias")
        ax.set_ylim(0, 3)
        ax.set_yticks(range(4))
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels( players)

        if sum(punctuation) == 0:
            ax.text(1, 1.5, "Nenhum jogo registrado", ha="center", va="center", fontsize=12, color="gray")
        else:
            bars = ax.bar([0, 1, 2], punctuation, color=colors)

            for bar, score in zip(bars, punctuation):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, str(score),
                        ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        display(fig, target="graph-output")

# Inicializa o jogo
GAME = TicTacToe()
