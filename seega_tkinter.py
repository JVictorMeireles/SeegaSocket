# import socket
import tkinter as tk
import tkinter.messagebox as tkmsg
import random as rd
import numpy as np

# Constantes
TAMANHO = 5
TAMANHO_CASA = 60
JOGADOR1 = "Verde"
JOGADOR2 = "Roxo"
PECAS_TOTAIS = 12

# Cores
COR_TABULEIRO = "#DDB88C"
COR_LINHA = "#000000"
COR_PECAS = {JOGADOR1: "green", JOGADOR2: "purple"}
COR_P1 = "green"
COR_P2 = "purple"
COR_DESTAQUE = "yellow"

class SeegaGame:
#funções de setup
	def __init__(self, root):
		self.root = root

		self.jogadores = [JOGADOR1, JOGADOR2]

		self.label_turno = tk.Label(root, text="")
		self.label_turno.pack()

		#funções de inicialização do jogo
		self.set_jogo()
		self.cria_widgets(root)

	def set_jogo(self): #inicializa o jogo
		#inicializa o tabuleiro 5x5 vazio
		self.tabuleiro = [[None for _ in range(TAMANHO)] for _ in range(TAMANHO)]

		#self.botoes = [[None for _ in range(TAMANHO)] for _ in range(TAMANHO)]

		self.fase = "posicionamento"  #as fases do jogo serão de posicionamento ou movimento
		self.jogador_atual = rd.choice(self.jogadores) #escolhe o primeiro jogador aleatoriamente

		#variáveis de jogo
		self.posicionado = {JOGADOR1: 0, JOGADOR2: 0} #quantas peças foram posicionadas
		self.capturou = {JOGADOR1: 0, JOGADOR2:0} #quantas peças foram capturadas
		self.peca_selecionada = None  #para armazenar a peça clicada na fase de movimento
		self.pecas_pos_p_turno = 0  #contador de peças posicionadas no turno
		self.continua_movimento = False  #flag para capturas consecutivas
		self.destinos_validos = [] #lista de destinos válidos para movimentação da peça
		self.origens_destacadas = []

	def cria_widgets(self,root): #estrutura da interface
		#cria o canvas do tabuleiro
		width = TAMANHO*TAMANHO_CASA
		height = TAMANHO*TAMANHO_CASA
		self.canvas = tk.Canvas(root, width=width, height=height)
		self.canvas.pack()
		self.canvas.bind("<Button-1>", self.clique) #associa a ação de clique com a função

		self.desenha_tabuleiro() #exibe o tabuleiro

		#texto de informação do estado do jogo
		self.label_status = tk.Label(root, text="", font=("Arial", 14))
		self.label_status.pack(pady=10)
		self.att_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
		self.label_cont_pecas = tk.Label(root, text="", font=("Arial", 12))
		self.label_cont_pecas.pack()
		self.att_cont_pecas()

		#TODO arranjar alguma forma de colocar os botões lado a lado
		#botão de desistência
		self.bt_desistencia = tk.Button(root, text="Desistir", command=self.desistencia)
		self.bt_desistencia.pack()

		#botão de encerramento do jogo
		self.bt_encerrar_jogo = tk.Button(root, text="Encerrar", command=self.encerra_jogo)
		self.bt_encerrar_jogo.pack()

		#função de chat aqui

	def desenha_tabuleiro(self):
		self.canvas.delete("all") #limpa o tabuleiro
		for x in range(TAMANHO):
			for y in range(TAMANHO):
				x1, y1 = x * TAMANHO_CASA, y * TAMANHO_CASA
				x2, y2 = x1 + TAMANHO_CASA, y1 + TAMANHO_CASA
				self.canvas.create_rectangle(x1, y1, x2, y2, fill=COR_TABULEIRO, outline=COR_LINHA)
				peca = self.tabuleiro[y][x]
				if peca:
					cor = COR_P1 if peca == "Verde" else COR_P2
					self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill=cor)
		if self.fase == "movimento":
			for x, y in self.destinos_validos: #TODO destaca movimentos válidos (verificar)
				x1, y1 = x * TAMANHO_CASA + 20, y * TAMANHO_CASA + 20
				x2, y2 = x1 + 20, y1 + 20
				self.canvas.create_oval(x1, y1, x2, y2, fill="black")
			self.highlight_captura()
			# jogadas_obrigatorias = self.get_jogadas_obrigatorias(self.jogador_atual)

	def reinicia_jogo(self):
    # Redefine todas as variáveis
		self.set_jogo()

		self.att_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
		self.att_cont_pecas()
		self.desenha_tabuleiro()
		# self.configura_botoes(self.frame)
		# self.habilita()

	# def configura_botoes(self, frame):
	# 	for y in range(TAMANHO):
	# 		for x in range(TAMANHO):
	# 			btn = tk.Button(
	# 				frame, text="", width=4, height=2,
	# 				command=lambda x=x, y=y: self.on_click(x, y))
	# 			btn.grid(row=y, column=x)
	# 			self.botoes[y][x] = btn


	def att_status(self, message):
		self.label_status.config(text=message)

	def clique(self, evento):
		coluna = evento.x//TAMANHO_CASA
		linha = evento.y//TAMANHO_CASA
		if self.fase == "posicionamento":
			self.handle_posicionamento(coluna, linha)
		elif self.fase == "movimento":
			self.handle_movimento(coluna, linha)

	def handle_posicionamento(self, x, y):
		if self.tabuleiro[y][x] is None and not (x == 2 and y == 2): #espaço vazio que não seja o meio
			self.tabuleiro[y][x] = self.jogador_atual
			self.posicionado[self.jogador_atual] += 1
			self.pecas_pos_p_turno += 1 #varíavel para posicionar 2 peças por turno
			if all(qtd == 12 for qtd in self.posicionado.values()):
				self.fase = "movimento"
				self.att_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
			else:
				if self.pecas_pos_p_turno == 2:
					self.pecas_pos_p_turno = 0
					self.troca_jogador()
					self.att_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
			self.att_cont_pecas()
			self.desenha_tabuleiro()

	def handle_movimento(self, x, y):
		#verifica se há jogadas obrigatórias para aquele jogador
		jogadas_obrigatorias = self.get_jogadas_obrigatorias(self.jogador_atual)
		if self.peca_selecionada:
			sx, sy = self.peca_selecionada
			origem = (sx, sy)
			destino = (x, y)
			if destino in self.destinos_validos:
				capturou = self.mover_peca(origem, destino)
				self.trata_captura(capturou)
				self.peca_selecionada = None
				self.destinos_validos = []
				self.jogador_atual = JOGADOR2 if self.jogador_atual == JOGADOR1 else JOGADOR2
		elif self.tabuleiro[y][x] == self.jogador_atual:
				if jogadas_obrigatorias:
					jogadas_validas = [j for j in jogadas_obrigatorias if j[0] == (y, x)]
					if jogadas_validas:
						self.peca_selecionada = (x, y)
						self.destinos_validos = [dest for _, dest in jogadas_validas]
				elif not self.continua_movimento or self.peca_selecionada == (x, y):
					self.peca_selecionada = (x, y)
				else:
					# lógica normal de jogo sem jogadas obrigatórias
					if self.adjacente(sx, sy, x, y) and self.tabuleiro[y][x] is None:
						capturou = self.mover_peca(origem, destino)
						self.trata_captura(capturou)
					else:
						self.peca_selecionada = None
						self.continua_movimento = False
						self.att_status("Movimento inválido. Tente novamente.")
		self.desenha_tabuleiro()

	def trata_captura(self, capturou):
		if capturou:
			self.peca_selecionada = (x, y)  # Mantém a peça selecionada
			self.continua_movimento = True
			self.att_status(f"Captura! {self.jogador_atual} pode mover novamente.")
		else:
			self.peca_selecionada = None
			self.continua_movimento = False
			self.troca_jogador()
			self.att_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
		self.att_cont_pecas()

	def mover_peca(self, origem, destino):
		x1, y1 = origem
		x2, y2 = destino
		jogador = self.tabuleiro[y1][x1]
		self.tabuleiro[y1][x1] = None
		self.tabuleiro[y2][x2] = jogador
		return self.checa_captura(destino)

	def get_origens_obrigatorias(self, jogador):
		origens = []
		for y in range(TAMANHO):
			for x in range(TAMANHO):
				if self.tabuleiro[y][x] == self.jogador_atual and self.pode_capturar(x, y, self.jogador_atual):
					origens.append((x,y))
		return origens

	def get_jogadas_obrigatorias(self, jogador):
		#verifica se, das jogadas disponíveis, quais resultam em captura
		jogadas = []
		for x in range(TAMANHO):
			for y in range(TAMANHO):
				if self.tabuleiro[y][x] == jogador:
					# print((x,y))
					for destino in self.get_movimentos_validos(x, y):
						if self.eh_captura((x, y), destino, jogador):
							jogadas.append(((x, y), destino))
		return jogadas

	def get_movimentos_validos(self, x, y):
		movimentos = []
		for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]: #esquerda direita cima baixo
			nx, ny = x + dx, y + dy
			if self.valido(nx, ny) and self.tabuleiro[ny][nx] is None:
				movimentos.append((nx,ny))
		# print(f"posição {(x,y)}, movimentos: {movimentos}")
		return movimentos

	def eh_captura(self, origem, destino, jogador):
		adversario = JOGADOR2 if jogador == JOGADOR1 else JOGADOR1
		x_dest, y_dest = destino
		return self.pode_capturar(x_dest, y_dest, jogador)

	def adjacente(self, x1, y1, x2, y2):
		return abs(x1 - x2) + abs(y1 - y2) == 1

	def troca_jogador(self):
		self.jogador_atual = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
		self.selecionado = None
		self.continua_movimento = False
		self.origens_destacadas = self.origens_c_capturas_disp()
		# self.atualizar_label_turno()

	def checa_captura(self, x, y):
		capturou = False
		oponente = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
		directions = [(-1,0), (1,0), (0,-1), (0,1)]

		for dx, dy in directions:
			nx1, ny1 = x + dx, y + dy
			nx2, ny2 = x + 2*dx, y + 2*dy
			if self.valido(nx2, ny2):
				if self.tabuleiro[ny1][nx1] == oponente and self.tabuleiro[ny2][nx2] == self.jogador_atual:
					self.tabuleiro[ny1][nx1] = None
					# self.botoes[ny1][nx1].config(text="")
					capturou = True
					self.capturou[self.jogador_atual]+=1
		return capturou

	def valido(self, x, y):
		return 0 <= x < TAMANHO and 0 <= y < TAMANHO

	def att_cont_pecas(self):
		#faz a contagem de todas as peças do tabuleiro e a quem pertencem
		p1 = sum(row.count(JOGADOR1) for row in self.tabuleiro)
		p2 = sum(row.count(JOGADOR2) for row in self.tabuleiro)
		if(self.fase=="posicionamento"): #peças restantes a serem colocadas
			self.label_cont_pecas.config(text=f"Peças restantes - X: {PECAS_TOTAIS-p1} | O: {PECAS_TOTAIS-p2}")
		else: #peças restantes do jogador
			self.label_cont_pecas.config(text=f"Peças restantes - X: {p1} | O: {p2}")

		#sempre que houver uma atualização do tabuleiro, há a checagem de vitória
		if self.fase == "movimento":
			self.checa_vitoria(p1, p2)

	def checa_vitoria(self, p1, p2):
		peq_vitoria, vencedor = self.pequena_vitoria()
		if p2 == 0: #Jogador 1 capturou todas as peças
			# self.desabilita()
			self.popup_game_over(f"Jogador {JOGADOR1} venceu!")
		elif p1 == 0: #Jogador 2 capturou todas as peças
			# self.desabilita()
			self.popup_game_over(f"Jogador {JOGADOR2} venceu!")
		elif not self.tem_movimentos(self.jogador_atual): #Vitória por bloqueio
			vencedor = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
			# self.desabilita()
			self.popup_game_over(f"Jogador {vencedor} venceu! ({self.jogador_atual} sem movimentos)")
		elif peq_vitoria:
			# self.desabilita()
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
			for i in range(1, TAMANHO-1):
				if len(set(matriz[i])) == 1 and set(matriz[i]) != None:
					cores_por_linha = [None for _ in range(TAMANHO)]
					for j in range(TAMANHO):
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
		for y in range(TAMANHO):
			for x in range(TAMANHO):
				if self.tabuleiro[y][x] == JOGADOR:
					for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
						nx, ny = x + dx, y + dy
						if self.valido(nx, ny) and self.tabuleiro[ny][nx] is None:
							return True
		return False

	def capturas_possiveis(self):
		for y in range(TAMANHO):
			for x in range(TAMANHO):
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
			if self.valido(nx2, ny2):
				if self.tabuleiro[ny1][nx1] == oponente and self.tabuleiro[ny2][nx2] == jogador:
					# print("pode capturar")
					return True
		# print("não pode capturar")
		return False

	def highlight_captura(self):
		self.origens_destacadas = self.get_origens_obrigatorias(self.jogador_atual)
		# print(f"origens destacadas: {self.origens_destacadas}")
		for x, y in self.origens_destacadas:
			x1, y1 = x * TAMANHO_CASA, y * TAMANHO_CASA
			x2, y2 = x1 + TAMANHO_CASA, y1 + TAMANHO_CASA
			self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, outline=COR_DESTAQUE, width=3)

	def handle_selecao(self, x, y):
		if self.fase != "movement":
			return

		if self.tabuleiro[y][x] != self.jogador_atual:
			return  # só pode selecionar sua própria peça

		if self.captura_disponivel():
			# Existem capturas obrigatórias
			if not self.pode_capturar(x, y, self.jogador_atual):
				return  # Não pode selecionar uma peça que não captura

	def origens_c_capturas_disp(self):
		origens = []
		for y in range(5):
			for x in range(5):
				if self.tabuleiro[y][x] == self.jogador_atual:
					if self.pode_capturar(x, y, self.jogador_atual):
						origens.append((x,y))
		return origens

	# def desabilita(self):
	# 	for row in self.botoes:
	# 		for btn in row:
	# 			btn.config(state="disabled")

	# def habilita(self):
	# 	for row in self.botoes:
	# 		for btn in row:
	# 			btn.config(state="normal")

	def desistencia(self):
		#TODO Rever esse trecho de código depois
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
		if confirma == "yes":
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
	root.title("Seega")
	game = SeegaGame(root)
	root.mainloop()