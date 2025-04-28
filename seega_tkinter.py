# import socket
import tkinter as tk
import tkinter.messagebox as tkmsg
import random as rd

TAM_TABULEIRO = 5
VAZIO = None
JOGADOR1 = "X"
JOGADOR2 = "O"

class SeegaGame:
#funções de setup
	def __init__(self, root):
		self.pecas_totais = 12

		self.root = root
		self.root.title("Seega")
		self.jogadores = [JOGADOR1, JOGADOR2]

		self.set_jogo()
		self.cria_widgets()

	def set_jogo(self):
		self.tabuleiro = [[VAZIO for _ in range(TAM_TABULEIRO)] for _ in range(TAM_TABULEIRO)]
		self.botoes = [[None for _ in range(TAM_TABULEIRO)] for _ in range(TAM_TABULEIRO)]
		self.fase = "posicionamento"  # posicionamento ou movimento
		self.jogador_atual = rd.choice(self.jogadores) #escolhe jogador aleatoriamente
		self.posicionado = {JOGADOR1: 0, JOGADOR2: 0}
		self.capturou = {JOGADOR1: 0, JOGADOR2:0}
		self.selecionado = None  # para armazenar a peça clicada na fase de movimento
		self.pos_turno = 0  # contador de peças por turno
		self.movimento_continuado = False  # flag para capturas consecutivas

	def cria_widgets(self): #estrutura da interface
		self.frame = tk.Frame(self.root)
		self.frame.pack()

		self.configura_botoes(self.frame)

		self.label_status = tk.Label(self.root, text="", font=("Arial", 14))
		self.label_status.pack(pady=10)
		self.att_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
		self.label_cont_pecas = tk.Label(self.root, text="", font=("Arial", 12))
		self.label_cont_pecas.pack()
		self.att_cont_pecas()
		self.bt_desistencia = tk.Button(self.root, text="Desistir", command=self.desistencia)
		self.bt_desistencia.pack(pady=10)

	def reinicia_jogo(self):
    # Redefine todas as variáveis
		self.set_jogo()

		self.att_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
		self.att_cont_pecas()
		self.configura_botoes(self.frame)
		self.habilita()

	def configura_botoes(self, frame):
		for y in range(TAM_TABULEIRO):
			for x in range(TAM_TABULEIRO):
				btn = tk.Button(
					frame, text="", width=4, height=2,
					command=lambda x=x, y=y: self.on_click(x, y))
				btn.grid(row=y, column=x)
				self.botoes[y][x] = btn
#fim funções de setup

	def att_status(self, message):
		self.label_status.config(text=message)

	def on_click(self, x, y):
		if self.fase == "posicionamento":
			self.handle_posicionamento(x, y)
		elif self.fase == "movimento":
			self.handle_movimento(x, y)

	def handle_posicionamento(self, x, y):
		meio = (TAM_TABULEIRO-TAM_TABULEIRO%2)/2
		if self.tabuleiro[y][x] is not VAZIO or (x == meio and y == meio):
			return

		self.tabuleiro[y][x] = self.jogador_atual
		self.botoes[y][x].config(text=self.jogador_atual)
		self.posicionado[self.jogador_atual] += 1
		self.pos_turno += 1

		if self.posicionado[JOGADOR1] == self.pecas_totais and self.posicionado[JOGADOR2] == self.pecas_totais:
			self.fase = "movimento"
			self.att_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
		else:
			if self.pos_turno == 2:
				self.pos_turno = 0
				self.troca_jogador()
				self.att_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
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
					self.att_status(f"Captura! {self.jogador_atual} pode mover novamente.")
				else:
					self.selecionado = None
					self.movimento_continuado = False
					self.troca_jogador()
					self.att_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
				self.att_cont_pecas()
			else:
				self.selecionado = None
				self.movimento_continuado = False
				self.att_status("Movimento inválido. Tente novamente.")
		else:
			if self.tabuleiro[y][x] == self.jogador_atual:
				if not self.movimento_continuado or self.selecionado == (x, y):
					self.selecionado = (x, y)
		# self.att_cont_pecas()

	# def grande_vitoria(self):
		# j1_capturas = self.capturou[PLAYER1]
		# j2_capturas = self.capturou[PLAYER2]

		# if j1_capturas > j2_capturas:
		# 	self.show_winner_popup("Jogador X venceu (grande vitória)!")
		# elif j2_capturas > j1_capturas:
		# 	self.show_winner_popup("Jogador O venceu (grande vitória)!")
		# else:
		# 	self.show_winner_popup("Empate (mesmo número de peças capturadas)!")

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
					self.capturou[self.jogador_atual]+=1
		return capturou

	def valido(self, x, y):
		return 0 <= x < TAM_TABULEIRO and 0 <= y < TAM_TABULEIRO

	def att_cont_pecas(self):
		p1 = sum(row.count(JOGADOR1) for row in self.tabuleiro)
		p2 = sum(row.count(JOGADOR2) for row in self.tabuleiro)
		if(self.fase=="posicionamento"):
			self.label_cont_pecas.config(text=f"Peças restantes - X: {self.pecas_totais-p1} | O: {self.pecas_totais-p2}")
		else:
			self.label_cont_pecas.config(text=f"Peças restantes - X: {p1} | O: {p2}")

		if self.fase == "movimento":
			self.vitoria(p1, p2)
			# if p1 == 0:
			# 	self.att_status("Jogador O venceu!")
			# 	self.desabilita()
			# 	self.popup_game_over(JOGADOR2)
			# elif p2 == 0:
			# 	self.att_status("Jogador X venceu!")
			# 	self.desabilita()
			# 	self.popup_game_over(JOGADOR1)
			# elif not self.tem_movimentos(self.jogador_atual):
			# 	vencedor = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
			# 	self.att_status(f"Jogador {vencedor} venceu! ({self.jogador_atual} sem movimentos)")
			# 	self.desabilita()
			# 	self.popup_game_over(vencedor)
	
	def vitoria(self, p1, p2):
		if p2 == 0: #Jogador 1 capturou todas as peças
			self.desabilita()
			self.popup_game_over(f"Jogador {JOGADOR1} venceu!")
		elif p1 == 0: #Jogador 2 capturou todas as peças
			self.desabilita()
			self.popup_game_over(f"Jogador {JOGADOR2} venceu!")
		elif not self.tem_movimentos(self.jogador_atual): #Vitória por bloqueio
			vencedor = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
			self.desabilita()
			self.popup_game_over(f"Jogador {vencedor} venceu! ({self.jogador_atual} sem movimentos)")
		elif not self.capturas_possiveis(): #Sem mais capturas possíveis (ganha quem capturou mais)
			j1_capturas = self.capturou[JOGADOR1]
			j2_capturas = self.capturou[JOGADOR2]
			if j1_capturas > j2_capturas:
				vencedor = JOGADOR1
			elif j2_capturas > j1_capturas:
				vencedor = JOGADOR2
			else:
				self.popup_game_over("Empate (mesmo número de peças capturadas)!")
				return
			self.popup_game_over(f"Jogador {vencedor} venceu (grande vitória)!")

	def tem_movimentos(self, JOGADOR):
		for y in range(TAM_TABULEIRO):
			for x in range(TAM_TABULEIRO):
				if self.tabuleiro[y][x] == JOGADOR:
					for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
						nx, ny = x + dx, y + dy
						if self.valido(nx, ny) and self.tabuleiro[ny][nx] is VAZIO:
							return True
		return False
	
	def desabilita(self):
		for row in self.botoes:
			for btn in row:
				btn.config(state="disabled")

	def habilita(self):
		for row in self.botoes:
			for btn in row:
				btn.config(state="normal")

	def capturas_possiveis(self):
		for y in range(TAM_TABULEIRO):
			for x in range(TAM_TABULEIRO):
				jogador = self.tabuleiro[y][x]
				if jogador in (JOGADOR1, JOGADOR2) and self.pode_capturar(x,y,jogador):
					return True
		return False

	def pode_capturar(self, x, y, jogador):
		oponente = JOGADOR1 if jogador == JOGADOR2 else JOGADOR2
		direcoes = [(-1,0),(1,0),(0,-1),(0,1)] #cima baixo esquerda direita
		for dx, dy in direcoes:
			nx1, ny1 = x + dx, y + dy
			nx2, ny2 = x + 2*dx, y + 2*dy
			if self.valido(nx1, ny1) and self.valido(nx2, ny2):
				if self.tabuleiro[ny1][nx1] == oponente and self.tabuleiro[ny2][nx2] == jogador:
					return True
		return False

	def desistencia(self):
		#Rever esse trecho de código
		#(o botão de desistência considera o jogador atual como
		#desistente, para socket isso é errado)
		confirma = tkmsg.askquestion("Desistir", "Você tem certeza que deseja desistir?")
		if confirma:
			vencedor = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
			self.att_status(f"Jogador {vencedor} venceu por desistência!")
			self.desabilita()
			self.popup_game_over(f"Jogador {vencedor} venceu por desistência!")

	def popup_game_over(self, mensagem):
		popup = tk.Toplevel(self.root)
		popup.title("Fim de Jogo")

		label = tk.Label(popup, text=mensagem, font=("Arial", 14))
		label.pack(padx=20, pady=10)

		bt_reinicia = tk.Button(popup, text="Jogar Novamente", command=lambda: [popup.destroy(), self.reinicia_jogo()])
		bt_reinicia.pack(pady=10)

if __name__ == "__main__":
	root = tk.Tk()
	game = SeegaGame(root)
	root.mainloop()