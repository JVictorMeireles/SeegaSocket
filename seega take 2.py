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

#ao terminar a fase de posicionamento, o tabuleiro verifica se há alguma peça
#com movimentação obrigatória, ou seja, se ela puder fazer um movimento de captura
#peças com movimentação obrigatória devem ser destacadas
#ao clicar em uma peça, serão exibidos os movimentos possíveis

class SeegaGame:
#funções de setup/interface
	def __init__(self, root):
		self.root = root

		jogadores = [JOGADOR1, JOGADOR2]

		self.label_turno = tk.Label(root, text="")
		self.label_turno.pack()

		#funções de inicialização do jogo
		self.set_jogo(jogadores)
		self.cria_widgets(root)

	def set_jogo(self,jogadores): #inicializa o jogo
		#inicializa o tabuleiro 5x5 vazio
		self.tabuleiro = [[None for _ in range(TAMANHO)] for _ in range(TAMANHO)]

		self.fase_posicionamento = True
		self.jogador_atual = rd.choice(jogadores)

		#variáveis de jogo
		self.qtd_pecas_posicionadas = {JOGADOR1: 0, JOGADOR2: 0}
		self.qtd_pecas_jogador_capturou = {JOGADOR1: 0, JOGADOR2:0}
		self.peca_selecionada = None
		self.pecas_pos_p_turno = 0
		self.continua_movimento = False
		self.destinos_validos = []
		self.origens_destacadas = []

	def cria_widgets(self,root): #estrutura da interface
		#cria o canvas do tabuleiro
		width = TAMANHO*TAMANHO_CASA
		height = TAMANHO*TAMANHO_CASA
		self.canvas = tk.Canvas(root, width=width, height=height)
		self.canvas.pack()
		#associa a ação de clique com a função
		self.canvas.bind("<Button-1>", self.clique)

		#exibe o tabuleiro
		self.desenha_tabuleiro()

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
					cor = COR_P1 if peca == JOGADOR1 else COR_P2
					self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill=cor)
		if not self.fase_posicionamento and not self.continua_movimento:
			jogadas_obrigatorias = self.get_jogadas_obrigatorias()
			for x,y in self.origens_destacadas:
				self.highlight_peca((x,y))
			for x, y in self.destinos_validos: #destaca movimentos válidos (TODO verificar)
				x1, y1 = x * TAMANHO_CASA + 20, y * TAMANHO_CASA + 20
				x2, y2 = x1 + 20, y1 + 20
				self.canvas.create_oval(x1, y1, x2, y2, fill="black")
		elif not self.fase_posicionamento and self.continua_movimento:
			self.highlight_peca(self.peca_selecionada)
			# self.highlight_captura()

	def highlight_peca(self, origem):
		(x, y) = origem
		x1, y1 = x * TAMANHO_CASA, y * TAMANHO_CASA
		x2, y2 = x1 + TAMANHO_CASA, y1 + TAMANHO_CASA
		self.canvas.create_oval(x1+9, y1+9, x2-9, y2-9, outline=COR_DESTAQUE, width=3)

#handlers
	def clique(self, evento):
		x = evento.x//TAMANHO_CASA
		y = evento.y//TAMANHO_CASA

		if self.fase_posicionamento:
			self.handle_posicionamento(x, y)
		else:
			self.handle_movimento(x, y) #TODO!!!!!!!!!!!!!!!!!!!!

	def handle_posicionamento(self, x, y):
		#ao clicar, verifica se a casa está vazia e não é a do meio
		#em caso positivo, posiciona a peça do jogador
		#além disso, cada jogador pode colocar duas peças por turno

		#espaço vazio que não seja o meio
		if self.tabuleiro[y][x] is None and not (x == 2 and y == 2):
			self.tabuleiro[y][x] = self.jogador_atual
			self.qtd_pecas_posicionadas[self.jogador_atual] += 1
			self.pecas_pos_p_turno += 1 #varíavel para posicionar 2 peças por turno
			if all(qtd == 12 for qtd in self.qtd_pecas_posicionadas.values()):
				self.fase_posicionamento = False
				self.att_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
			else:
				if self.pecas_pos_p_turno == 2:
					self.pecas_pos_p_turno = 0
					self.troca_jogador()
					self.att_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
			self.att_cont_pecas()
			self.desenha_tabuleiro()

	def handle_movimento(self, x, y):
		#primeiro, verifica se a peça clicada é uma cujo movimento é obrigatório
		#caso não seja, faz a movimentação

		#verifica se há jogadas obrigatórias para aquele jogador
		jogadas_obrigatorias = self.get_jogadas_obrigatorias()
		if self.peca_selecionada:
			sx, sy = self.peca_selecionada
			origem = (sx, sy)
			destino = (x, y)
			if destino in self.destinos_validos:
				capturou = self.move_peca(origem, destino)
				self.trata_captura(capturou, destino)
		elif self.tabuleiro[y][x] == self.jogador_atual:
			if jogadas_obrigatorias:
				jogadas_validas = [j for j in jogadas_obrigatorias if j[0] == (x, y)]
				if jogadas_validas:
					self.peca_selecionada = (x, y)
					self.destinos_validos = [dest for _, dest in jogadas_validas]
			elif not self.continua_movimento or self.peca_selecionada == (x, y):
				jogadas_disponiveis = self.get_jogadas_disponiveis()
				jogadas_validas = [j for j in jogadas_disponiveis if j[0] == (x, y)]
				if jogadas_validas:
					self.peca_selecionada = (x, y)
					self.destinos_validos = [dest for _, dest in jogadas_validas]
			else:
				# lógica normal de jogo sem jogadas obrigatórias
				if self.adjacente(sx, sy, x, y) and self.tabuleiro[y][x] is None:
					capturou = self.move_peca(origem, destino)
					self.trata_captura(capturou, destino)
				else:
					self.peca_selecionada = None
					self.continua_movimento = False
					self.att_status("Movimento inválido. Tente novamente.")
		self.desenha_tabuleiro()

	def move_peca(self, origem, destino):
		x1, y1 = origem
		x2, y2 = destino
		jogador = self.tabuleiro[y1][x1]
		self.tabuleiro[y1][x1] = None
		self.tabuleiro[y2][x2] = jogador
		return self.checa_captura(destino)

	def trata_captura(self, capturou, destino):
		x, y = destino
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

#coletores
	def get_jogadas_obrigatorias(self):
		#verifica se, das jogadas disponíveis, quais resultam em captura
		#retorna uma lista de jogadas obrigatórias em formato [((Xor,Yor),(Xdest,Ydest))]
		#ex: jogadas = [((3,2),(2,2)),((2,3),(2,2))]

		jogadas = []
		self.origens_destacadas = []
		if self.continua_movimento:
			x, y = self.peca_selecionada
			for destino in self.get_destinos_validos(x, y):
				if self.eh_captura(destino):
					self.origens_destacadas = self.peca_selecionada
					jogadas.append((self.peca_selecionada, destino))
		else:
			for x in range(TAMANHO):
				for y in range(TAMANHO):
					if self.tabuleiro[y][x] == self.jogador_atual:
						for destino in self.get_destinos_validos(x, y):
							if self.eh_captura(destino):
								self.origens_destacadas.append((x,y))
								jogadas.append(((x, y), destino))
		return jogadas

	def get_jogadas_disponiveis(self):
		jogadas = []
		for x in range(TAMANHO):
			for y in range(TAMANHO):
				if self.tabuleiro[y][x] == self.jogador_atual:
					for destino in self.get_destinos_validos(x, y):
						jogadas.append(((x, y), destino))
		return jogadas

	#TODO usar essa função para destacar movimentos possíveis de uma peça
	def get_destinos_validos(self, x, y):
		#verifica se um destino para uma peça está disponível
		#retorna uma lista de destinos no formato [(x,y)]
		#ex: movimentos = [(2,2),(0,1)]
		movimentos = []
		for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]: #esquerda direita cima baixo
			nx, ny = x + dx, y + dy
			if self.eh_valido(nx, ny) and self.tabuleiro[ny][nx] is None:
				movimentos.append((nx,ny))
		return movimentos

#checadores
	def eh_valido(self, x, y):
		#checa se está dentro do limite do tabuleiro
		return 0 <= x < TAMANHO and 0 <= y < TAMANHO

	def eh_captura(self, destino):
		oponente = JOGADOR2 if self.jogador_atual == JOGADOR1 else JOGADOR1
		x_dest, y_dest = destino
		return self.pode_capturar(x_dest, y_dest)

	def pode_capturar(self, x, y):
		oponente = JOGADOR2 if self.jogador_atual == JOGADOR1 else JOGADOR1
		direcoes = [(-1,0),(1,0),(0,-1),(0,1)] #cima baixo esquerda direita
		for dx, dy in direcoes:
			nx1, ny1 = x + dx, y + dy
			nx2, ny2 = x + 2*dx, y + 2*dy
			if self.eh_valido(nx1, ny1) and self.tabuleiro[ny1][nx1] == oponente:
				if self.eh_valido(nx2, ny2) and self.tabuleiro[ny2][nx2] == self.jogador_atual:
					return True
		return False

	def checa_captura(self, destino):
		x, y = destino
		capturou = False
		oponente = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
		directions = [(-1,0), (1,0), (0,-1), (0,1)]

		for dx, dy in directions:
			nx1, ny1 = x + dx, y + dy
			nx2, ny2 = x + 2*dx, y + 2*dy
			if self.eh_valido(nx2, ny2):
				if self.tabuleiro[ny1][nx1] == oponente and self.tabuleiro[ny2][nx2] == self.jogador_atual:
					self.tabuleiro[ny1][nx1] = None
					capturou = True
					self.qtd_pecas_jogador_capturou[self.jogador_atual]+=1
		return capturou

	def adjacente(self, x1, y1, x2, y2):
		return abs(x1 - x2) + abs(y1 - y2) == 1
#atualizadores
	def att_status(self, message):
		self.label_status.config(text=message)

	def att_cont_pecas(self):
		#faz a contagem de todas as peças do tabuleiro e a quem pertencem
		p1 = sum(row.count(JOGADOR1) for row in self.tabuleiro)
		p2 = sum(row.count(JOGADOR2) for row in self.tabuleiro)

		#peças restantes a serem colocadas
		if self.fase_posicionamento:
			self.label_cont_pecas.config(text=f"Peças restantes - X: {PECAS_TOTAIS-p1} | O: {PECAS_TOTAIS-p2}")
		#peças restantes do jogador
		else:
			self.label_cont_pecas.config(text=f"Peças restantes - X: {p1} | O: {p2}")
			#sempre que houver uma atualização do tabuleiro, há a checagem de vitória
			# self.checa_vitoria(p1, p2)

	def troca_jogador(self):
		self.jogador_atual = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
		self.selecionado = None
		self.continua_movimento = False
		# self.origens_destacadas = self.origens_c_capturas_disp()

#final do jogo
	def desistencia(self):
		#TODO Rever esse trecho de código depois
		#(o botão de desistência considera o jogador atual como
		#desistente, para socket isso é errado)
		confirma = tkmsg.askquestion("Desistir", "Você tem certeza que deseja desistir?")
		if confirma == "yes":
			vencedor = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
			self.att_status(f"Jogador {vencedor} venceu por desistência!")
			self.popup_game_over(f"Jogador {vencedor} venceu por desistência!")

	def encerra_jogo(self):
		#TODO a mensagem de confirmação vai para o outro jogador
		confirma = tkmsg.askquestion("Encerrar jogo", "Você tem certeza que deseja encerrar o jogo?")
		if confirma == "yes":
			j1 = self.qtd_pecas_jogador_capturou[JOGADOR1]
			j2 = self.qtd_pecas_jogador_capturou[JOGADOR2]
			if j1 > j2:
				vencedor = JOGADOR1
			elif j2 > j1:
				vencedor = JOGADOR2
			else:
				self.popup_game_over("Empate (mesmo número de peças capturadas)!")
				return
			self.popup_game_over(f"Jogador {vencedor} venceu (grande vitória)!")

	def popup_game_over(self, mensagem):
		if tkmsg.askyesno("Reiniciar", f"{mensagem} Deseja jogar novamente?"):
			self.reinicia_jogo()
		else:
			self.root.destroy()

	def reinicia_jogo(self):
		self.set_jogo((JOGADOR1, JOGADOR2))
		self.att_status(f"Fase de colocação - Jogador: {self.jogador_atual}")
		self.att_cont_pecas()
		self.desenha_tabuleiro()

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Seega")
	game = SeegaGame(root)
	root.mainloop()