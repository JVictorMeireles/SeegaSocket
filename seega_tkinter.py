# import socket
import tkinter as tk
import tkinter.messagebox as tkmsg
import random as rd
import numpy as np

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
		self.tamanho = 5
		self.tabuleiro = [[None for _ in range(self.tamanho)] for _ in range(self.tamanho)]
		self.botoes = [[None for _ in range(self.tamanho)] for _ in range(self.tamanho)]
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
		self.bt_encerrar_jogo = tk.Button(self.root, text="Encerrar", command=self.encerra_jogo)
		self.bt_encerrar_jogo.pack(pady=10)

	def reinicia_jogo(self):
    # Redefine todas as variáveis
		self.set_jogo()

		self.att_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
		self.att_cont_pecas()
		self.configura_botoes(self.frame)
		self.habilita()

	def configura_botoes(self, frame):
		for y in range(self.tamanho):
			for x in range(self.tamanho):
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
		meio = (self.tamanho-self.tamanho%2)//2
		if self.tabuleiro[y][x] is not None or (x == meio and y == meio):
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
			if self.adjacente(sx, sy, x, y) and self.tabuleiro[y][x] is None:
				jogadas_obrigatorias = self.get_jogadas_obrigatorias(self.jogador_atual)
				if jogadas_obrigatorias:
					pecas_ativas = [origem for origem, _ in jogadas_obrigatorias]
					if (linha, coluna) in pecas_ativas:
						# permitir seleção da peça
						pecas_destino_validas = [destino for origem, destino in jogadas_obrigatorias if origem == (linha, coluna)]
						# armazenar essas opções para o próximo clique
				else:
					# lógica normal de jogo sem jogadas obrigatórias
					# movimentar a peça
					self.tabuleiro[y][x] = self.jogador_atual
					self.tabuleiro[sy][sx] = None
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

	def get_jogadas_obrigatorias(self, jogador):
		jogadas = []
		for x in range(self.tamanho):
			for y in range(self.tamanho):
				if self.tabuleiro[y][x] == jogador:
					movimentos_possiveis = self.get_movimentos_validos(x, y)
					for destino in movimentos_possiveis:
						if self.eh_captura((x, y), destino):
							jogadas.append(((x, y), destino))
		return jogadas

	def get_movimentos_validos(self, x, y):
		jogador = self.tabuleiro[y][x]
		movimentos = []
		for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
			nx, ny = x + dx, y + dy
			if self.valido(nx, ny) and self.tabuleiro[ny][nx] is None:
				movimentos.append(((x,y),(nx,ny)))
		return movimentos

	def eh_captura(self, origem, destino):
		adversario = JOGADOR2 if self.jogador_atual == JOGADOR1 else JOGADOR1
		x_dest, y_dest = destino

		# Simula o movimento
		tabuleiro_simulado = [linha[:] for linha in self.tabuleiro]
		tabuleiro_simulado[origem[0]][origem[1]] = None
		tabuleiro_simulado[x_dest][y_dest] = self.jogador_atual

		return self.pode_capturar(x_dest, y_dest, self.jogador_atual)

	def adjacente(self, x1, y1, x2, y2):
		return abs(x1 - x2) + abs(y1 - y2) == 1

	def troca_jogador(self):
		self.jogador_atual = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2

	def checa_captura(self, x, y):
		capturou = False
		oponente = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
		directions = [(-1,0), (1,0), (0,-1), (0,1)]

		for dx, dy in directions:
			nx1, ny1 = x + dx, y + dy
			nx2, ny2 = x + 2*dx, y + 2*dy
			if self.valido(nx1, ny1) and self.valido(nx2, ny2):
				if self.tabuleiro[ny1][nx1] == oponente and self.tabuleiro[ny2][nx2] == self.jogador_atual:
					self.tabuleiro[ny1][nx1] = None
					self.botoes[ny1][nx1].config(text="")
					capturou = True
					self.capturou[self.jogador_atual]+=1
		return capturou

	def valido(self, x, y):
		return 0 <= x < self.tamanho and 0 <= y < self.tamanho

	def att_cont_pecas(self):
		p1 = sum(row.count(JOGADOR1) for row in self.tabuleiro)
		p2 = sum(row.count(JOGADOR2) for row in self.tabuleiro)
		if(self.fase=="posicionamento"):
			self.label_cont_pecas.config(text=f"Peças restantes - X: {self.pecas_totais-p1} | O: {self.pecas_totais-p2}")
		else:
			self.label_cont_pecas.config(text=f"Peças restantes - X: {p1} | O: {p2}")

		if self.fase == "movimento":
			self.checa_vitoria(p1, p2)

	def checa_vitoria(self, p1, p2):
		peq_vitoria, vencedor = self.pequena_vitoria()
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
		elif peq_vitoria:
			self.desabilita()
			self.popup_game_over(f"Jogador {vencedor} venceu! (pequena vitória)")

	def pequena_vitoria(self):
		def verifica_divisao(cores_por_linha):
			index_zero = cores_por_linha.index(0)
			esquerda = [x for x in cores_por_linha[:index_zero] if x != 0]
			direita = [x for x in cores_por_linha[index_zero+1:] if x != 0]
			return ((set(esquerda) == {JOGADOR1} and set(direita) == {JOGADOR2}) or (set(esquerda) == {JOGADOR2} and set(direita) == {JOGADOR1}))
		matriz = np.array(self.tabuleiro)
		for t in range(2):
			matriz = matriz.T if t == 1 else matriz
			for i in range(1, self.tamanho-1):
				if len(set(matriz[i])) == 1 and set(matriz[i]) != None:
					cores_por_linha = [None for _ in range(self.tamanho)]
					for j in range(self.tamanho):
						if i == j:
							cores_por_linha[j] = 0
							continue
						set_linha = set([x for x in matriz[j] if x != None])
						if len(set_linha) > 1:
							return (0, None)
						elif len(set_linha) == 1:
							cores_por_linha[j] = list(set_linha)[0]
					if verifica_divisao(cores_por_linha):
						return (1, JOGADOR1) if matriz[i][0] == JOGADOR1 else (1, JOGADOR2)
		return (0, None)

	def tem_movimentos(self, JOGADOR):
		for y in range(self.tamanho):
			for x in range(self.tamanho):
				if self.tabuleiro[y][x] == JOGADOR:
					for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
						nx, ny = x + dx, y + dy
						if self.valido(nx, ny) and self.tabuleiro[ny][nx] is None:
							return True
		return False

	def capturas_possiveis(self):
		for y in range(self.tamanho):
			for x in range(self.tamanho):
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

	def highlight_captura(self):
    # limpa todos os destaques
		for y in range(5):
			for x in range(5):
				self.botoes[y][x].config(bg="SystemButtonFace")

    # destaca as peças que podem capturar
		for y in range(5):
			for x in range(5):
				if self.tabuleiro[y][x] == self.jogador_atual:
					if self.pode_capturar(x, y, self.jogador_atual):
						self.botoes[y][x].config(bg="yellow")

	def handle_selecao(self, x, y):
		if self.fase != "movement":
			return

		if self.tabuleiro[y][x] != self.jogador_atual:
			return  # só pode selecionar sua própria peça

		if self.captura_disponivel():
			# Existem capturas obrigatórias
			if not self.pode_capturar(x, y, self.jogador_atual):
				return  # Não pode selecionar uma peça que não captura

	def captura_disponivel(self):
		for y in range(5):
			for x in range(5):
				if self.tabuleiro[y][x] == self.jogador_atual:
					if self.pode_capturar(x, y, self.jogador_atual):
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

	def desistencia(self):
		#Rever esse trecho de código
		#(o botão de desistência considera o jogador atual como
		#desistente, para socket isso é errado)
		confirma = tkmsg.askquestion("Desistir", "Você tem certeza que deseja desistir?")
		if confirma == "yes":
			vencedor = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
			self.att_status(f"Jogador {vencedor} venceu por desistência!")
			self.desabilita()
			self.popup_game_over(f"Jogador {vencedor} venceu por desistência!")

	def encerra_jogo(self):
		confirma = tkmsg.askquestion("Encerrar jogo", "Você tem certeza que deseja encerrar o jogo?")
		if confirma:
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

	def popup_game_over(self, mensagem):
		# tkmsg.showinfo("Fim de Jogo", mensagem)
		if tkmsg.askyesno("Reiniciar", f"{mensagem} Deseja jogar novamente?"):
			self.reinicia_jogo()
		else:
			self.root.destroy()

if __name__ == "__main__":
	root = tk.Tk()
	game = SeegaGame(root)
	root.mainloop()