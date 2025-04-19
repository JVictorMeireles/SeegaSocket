# import socket
import tkinter as tk
import random as rd

TAM_TABULEIRO = 5
VAZIO = None
JOGADOR1 = "X"
JOGADOR2 = "O"

#verificar quando houver uma captura: o jogador que a tiver feito pode jogar a peça movimentada de novo

class SeegaGame:
	def __init__(self, root):
		self.jogadores = [JOGADOR1, JOGADOR2]
		self.root = root
		self.root.title("Seega")
		self.tabuleiro = [[VAZIO for _ in range(TAM_TABULEIRO)] for _ in range(TAM_TABULEIRO)]
		self.botoes = [[None for _ in range(TAM_TABULEIRO)] for _ in range(TAM_TABULEIRO)]

		self.fase = "posicionamento"  # posicionamento ou movimento
		self.jogador_atual = rd.choice(self.jogadores) #escolhe jogador aleatoriamente
		self.posicionado = {JOGADOR1: 0, JOGADOR2: 0}
		self.pecas_totais = 12

		self.selecionado = None  # para armazenar a peça clicada na fase de movimento

		self.cria_widgets()
		self.atualizar_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
		self.label_cont_pecas = tk.Label(self.root, text="", font=("Arial", 12))
		self.label_cont_pecas.pack()
		self.att_cont_pecas()
		self.turn_placements = 0  # contador de peças por turno
		self.movimento_continuado = False  # flag para capturas consecutivas

	def cria_widgets(self):
		frame = tk.Frame(self.root)
		frame.pack()

		for y in range(TAM_TABULEIRO):
			for x in range(TAM_TABULEIRO):
				btn = tk.Button(
					frame, text="", width=4, height=2,
					command=lambda x=x, y=y: self.on_click(x, y))
				btn.grid(row=y, column=x)
				self.botoes[y][x] = btn

		self.label_status = tk.Label(self.root, text="", font=("Arial", 14))
		self.label_status.pack(pady=10)

	def atualizar_status(self, message):
		self.label_status.config(text=message)

	def on_click(self, x, y):
		if self.fase == "posicionamento":
			self.handle_posicionamento(x, y)
		elif self.fase == "movimento":
			self.handle_movimento(x, y)

	def handle_posicionamento(self, x, y):
		if self.tabuleiro[y][x] is not VAZIO or (x == 2 and y == 2):
			return

		self.tabuleiro[y][x] = self.jogador_atual
		self.botoes[y][x].config(text=self.jogador_atual)
		self.posicionado[self.jogador_atual] += 1
		self.turn_placements += 1

		if self.posicionado[JOGADOR1] == self.pecas_totais and self.posicionado[JOGADOR2] == self.pecas_totais:
			self.fase = "movimento"
			self.atualizar_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
		else:
			if self.turn_placements == 2:
				self.turn_placements = 0
				self.troca_jogador()
			self.atualizar_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
		self.att_cont_pecas()

	def handle_movimento(self, x, y):
		if self.selecionado:
			sx, sy = self.selecionado
			if self.adjacente(sx, sy, x, y) and self.tabuleiro[y][x] is VAZIO:
				# movimentar a peça
				self.tabuleiro[y][x] = self.jogador_atual
				self.tabuleiro[sy][sx] = VAZIO
				self.botoes[y][x].config(text=self.jogador_atual)
				self.botoes[sy][sx].config(text="")

				capturou = self.checa_captura(x, y)

				if capturou:
					self.selecionado = (x, y)  # Mantém a peça selecionada
					self.movimento_continuado = True
					self.atualizar_status(f"Captura! {self.jogador_atual} pode mover novamente.")
				else:
					self.selecionado = None
					self.movimento_continuado = False
					self.troca_jogador()
					self.atualizar_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
				self.att_cont_pecas()
			else:
				self.selecionado = None
				self.movimento_continuado = False
				self.atualizar_status("Movimento inválido. Tente novamente.")
		else:
			if self.tabuleiro[y][x] == self.jogador_atual:
				if not self.movimento_continuado or self.selecionado == (x, y):
					self.selecionado = (x, y)
		# self.att_cont_pecas()

	def adjacente(self, x1, y1, x2, y2):
		return abs(x1 - x2) + abs(y1 - y2) == 1

	def troca_jogador(self):
		self.jogador_atual = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2

	def checa_captura(self, x, y):
		capturou = False
		oponente = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
		directions = [(-1,0), (1,0), (0,-1), (0,1)]
		# self.att_cont_pecas()

		for dx, dy in directions:
			nx1, ny1 = x + dx, y + dy
			nx2, ny2 = x + 2*dx, y + 2*dy
			if self.valido(nx1, ny1) and self.valido(nx2, ny2):
				if self.tabuleiro[ny1][nx1] == oponente and self.tabuleiro[ny2][nx2] == self.jogador_atual:
					self.tabuleiro[ny1][nx1] = VAZIO
					self.botoes[ny1][nx1].config(text="")
					capturou = True
		return capturou

	def valido(self, x, y):
		return 0 <= x < TAM_TABULEIRO and 0 <= y < TAM_TABULEIRO

	def att_cont_pecas(self):
		p1 = sum(row.count(JOGADOR1) for row in self.tabuleiro)
		p2 = sum(row.count(JOGADOR2) for row in self.tabuleiro)
		self.label_cont_pecas.config(text=f"Peças restantes - X: {p1} | O: {p2}")

		if p1 == 0 and self.fase == "movimento":
			self.atualizar_status("Jogador O venceu!")
			self.disable_all()
		elif p2 == 0 and self.fase == "movimento":
			self.atualizar_status("Jogador X venceu!")
			self.disable_all()
		elif not self.tem_movimentos(self.jogador_atual) and self.fase == "movimento":
			winner = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
			self.atualizar_status(f"Jogador {winner} venceu! ({self.jogador_atual} sem movimentos)")
			self.disable_all()
	
	def tem_movimentos(self, JOGADOR):
		for y in range(TAM_TABULEIRO):
			for x in range(TAM_TABULEIRO):
				if self.tabuleiro[y][x] == JOGADOR:
					for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
						nx, ny = x + dx, y + dy
						if self.valido(nx, ny) and self.tabuleiro[ny][nx] is VAZIO:
							return True
		return False
	
	def disable_all(self):
		for row in self.botoes:
			for btn in row:
				btn.config(state="disabled")


if __name__ == "__main__":
	root = tk.Tk()
	game = SeegaGame(root)
	root.mainloop()