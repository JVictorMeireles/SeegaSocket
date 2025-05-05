import argparse
import json
import numpy as np
import random as rd
import socket
import threading
import tkinter as tk
import tkinter.messagebox as tkmsg
import time

# Constantes
TAMANHO = 5
TAMANHO_CASA = 60
JOGADOR1 = "Verde"
JOGADOR2 = "Roxo"
PECAS_TOTAIS = 12
HOST = "localhost"
PORT = 5555
BUFFER = 8192

# Cores
COR_TABULEIRO = "#DDB88C"
COR_LINHA = "#000000"
COR_PECAS = {JOGADOR1: "green", JOGADOR2: "purple"}
COR_P1 = "green"
COR_P2 = "purple"
COR_DESTAQUE = "yellow"

class JogoSeega:
#funções de setup/interface
	def __init__(self):
		self.rede = GerenciadorSocket(self.att_jogo_com_dados)
		self.root = tk.Tk()
		tipo_conexao = "Servidor" if self.rede.is_servidor else "Cliente"
		self.root.title("Seega de " + tipo_conexao)

		self.quer_desistencia,self.quer_encerrar = None, None
		self.mensagens_chat = []

		# self.rodadas = 0
		# self.pos_anterior

		jogadores = [JOGADOR1, JOGADOR2]

		#funções de inicialização do jogo
		self.set_jogo(jogadores)
		self.cria_widgets(self.root)

		# if self.rede.is_servidor:
		self.bloquear_botoes_tabuleiro()
		self.root.mainloop()

	def set_jogo(self,jogadores): #inicializa o jogo
		#inicializa o tabuleiro 5x5 vazio
		self.tabuleiro = [[None for _ in range(TAMANHO)] for _ in range(TAMANHO)]

		self.bloqueia = False
		self.fase_posicionamento = True
		self.jogador_servidor = JOGADOR1 #rd.choice(jogadores)
		self.jogador_cliente = JOGADOR2 #JOGADOR1 if self.jogador_servidor == JOGADOR2 else JOGADOR2
		self.jogador_atual = self.jogador_servidor
		self.jogo_parado = False

		#variáveis de jogo
		self.qtd_pecas_posicionadas = {JOGADOR1: 0, JOGADOR2: 0}
		self.qtd_pecas_jogador_capturou = {JOGADOR1: 0, JOGADOR2:0}
		self.peca_selecionada = None
		self.pecas_pos_p_turno = 0
		self.continua_movimento = False
		self.destinos_validos = []
		self.origens_destacadas = []

	def cria_widgets(self,root): #estrutura da interface
		#cria a interface do chat
		self.interface_chat = tk.Canvas(root)
		self.interface_chat.pack(side='right', fill='y', padx=10, pady=5)

		#texto de informação do estado do jogo
			#informa qual a cor do jogador
		label_informando_cor=tk.Label(root,text=f"Você joga de {self.jogador_servidor if self.rede.is_servidor else self.jogador_cliente}.",font=("Arial",16,"bold"))
		label_informando_cor.pack(pady=10)
			#informa o estado do jogo
		self.label_status = tk.Label(root, text="", font=("Arial", 14))
		self.label_status.pack(pady=10)

		#cria a interface do jogo
		width = TAMANHO*TAMANHO_CASA
		height = TAMANHO*TAMANHO_CASA
		self.canvas = tk.Canvas(root, width=width, height=height)
		self.canvas.pack(pady=10, padx=50)
		self.canvas.config(bg=COR_TABULEIRO)
		#exibe o tabuleiro
		self.desenha_tabuleiro()
		#associa a ação de clique com a função
		self.canvas.bind("<Button-1>", self.clique)
		
		#informa o número de peças restantes
		self.label_cont_pecas = tk.Label(root, text="", font=("Arial", 12))
		self.label_cont_pecas.pack(pady=10)
		self.att_cont_pecas()

		self.cria_botoes_inferiores()
		
		#cria a interface do chat
		self.chat_text = tk.Text(self.interface_chat, width=50, state='disabled')
		self.chat_text.pack(fill='y', padx=5, pady=5)

		self.chat_entry = tk.Entry(self.interface_chat, width=50)
		self.chat_entry.bind("<Return>", self.enviar_mensagem_chat)
		self.chat_entry.pack()

		self.send_button = tk.Button(self.interface_chat, text="Enviar", command=self.enviar_mensagem_chat)
		self.send_button.pack()

	def cria_botoes_inferiores(self):
		bt = [
			["Desistir", self.desistencia],
			["Encerrar", self.encerra_jogo],
		]
		# self.frame_inferior = tk.Frame(self.canvas)
		# self.frame_inferior.pack(pady=10)
		# i = 0
		for texto, comando in bt:
			botao = tk.Button(self.root, text=texto, command=comando)
			botao.pack(side='left', padx=5)
			# i+=1

	def desenha_tabuleiro(self):
		self.canvas.delete("all") #limpa o tabuleiro
		#cria o tabuleiro
		for x in range(TAMANHO):
			for y in range(TAMANHO):
				x1, y1 = x * TAMANHO_CASA, y * TAMANHO_CASA
				x2, y2 = x1 + TAMANHO_CASA, y1 + TAMANHO_CASA
				self.canvas.create_rectangle(x1, y1, x2, y2, outline=COR_LINHA)#, fill=COR_TABULEIRO)

				peca = self.tabuleiro[y][x]
				#desenha as peças
				if peca:
					cor = COR_P1 if peca == JOGADOR1 else COR_P2
					self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill=cor)
		
		#fase de movimento
		if not self.fase_posicionamento:
			jogadas_obrigatorias = self.get_jogadas_obrigatorias()
			jogadas_obrigatorias_peca = [j for j in jogadas_obrigatorias if j[0] == self.peca_selecionada]
			if not self.continua_movimento and jogadas_obrigatorias:
				for x,y in self.origens_destacadas:
					self.highlight_peca((x,y))
				for (x, y) in self.destinos_validos: #destaca movimentos válidos
					x1, y1 = x * TAMANHO_CASA + 20, y * TAMANHO_CASA + 20
					x2, y2 = x1 + 20, y1 + 20
					self.canvas.create_oval(x1, y1, x2, y2, fill="black")
			elif not jogadas_obrigatorias and self.peca_selecionada or self.continua_movimento and not jogadas_obrigatorias_peca:
				self.highlight_peca(self.peca_selecionada)
				(xori, yori) = self.peca_selecionada
				for (x, y) in self.get_destinos_validos(xori, yori): #destaca movimentos válidos
					x1, y1 = x * TAMANHO_CASA + 20, y * TAMANHO_CASA + 20
					x2, y2 = x1 + 20, y1 + 20
					self.canvas.create_oval(x1, y1, x2, y2, fill="black")
			elif self.continua_movimento and jogadas_obrigatorias_peca:
				self.highlight_peca(self.peca_selecionada)
				(xori, yori) = self.peca_selecionada
				destinos_obrigatorios = [dest for _, dest in jogadas_obrigatorias_peca if _ == self.peca_selecionada]
				for (x, y) in destinos_obrigatorios: #destaca movimentos válidos
					x1, y1 = x * TAMANHO_CASA + 20, y * TAMANHO_CASA + 20
					x2, y2 = x1 + 20, y1 + 20
					self.canvas.create_oval(x1, y1, x2, y2, fill="black")

	def highlight_peca(self, origem):
		(x, y) = origem
		x1, y1 = x * TAMANHO_CASA, y * TAMANHO_CASA
		x2, y2 = x1 + TAMANHO_CASA, y1 + TAMANHO_CASA
		self.canvas.create_oval(x1+9, y1+9, x2-9, y2-9, outline=COR_DESTAQUE, width=3)

#handlers
	def clique(self, evento):
		x = evento.x//TAMANHO_CASA
		y = evento.y//TAMANHO_CASA

		if not self.bloqueia:
			if self.fase_posicionamento:
				self.handle_posicionamento(x, y)
			else:
				self.handle_movimento(x, y)
		self.att_jogo()

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
				self.enviar_estado_do_jogo(fase_movimento=True)
				self.att_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
			else:
				if self.pecas_pos_p_turno == 2:
					self.pecas_pos_p_turno = 0
					self.troca_jogador()
			self.att_cont_pecas()
			self.desenha_tabuleiro()

	def handle_movimento(self, x, y):
		jogadas_obrigatorias = self.get_jogadas_obrigatorias()
		jogadas_disponiveis = self.get_jogadas_disponiveis()
		#selecionando uma peça do jogador atual
		if self.tabuleiro[y][x] == self.jogador_atual:
			#se houver jogadas obrigatórias, seleciona uma peça que realize tal jogada
			if jogadas_obrigatorias:# and not self.continua_movimento:
				jogadas_validas = [j for j in jogadas_obrigatorias if j[0] == (x, y)]
				if jogadas_validas:
					self.peca_selecionada = (x, y)
					self.destinos_validos = [dest for _, dest in jogadas_validas]
			#se não houver jogadas obrigatórias, seleciona uma peça qualquer do jogador atual
			elif not self.continua_movimento or self.peca_selecionada == (x, y):
				self.peca_selecionada = (x, y)
				jogadas_disponiveis = self.get_jogadas_disponiveis()
				jogadas_validas = [j for j in jogadas_disponiveis if j[0] == (x, y)]
				if jogadas_validas:
					self.destinos_validos = [dest for _, dest in jogadas_validas]
		elif self.continua_movimento and self.tabuleiro[y][x] == None:
			jogadas_obrigatorias_peca = [j for j in jogadas_obrigatorias if j[0] == self.peca_selecionada]
			if jogadas_obrigatorias_peca:
				jogadas_validas = jogadas_obrigatorias_peca
			else:
				jogadas_validas = [j for j in jogadas_disponiveis if j[0] == self.peca_selecionada]
			sx, sy = self.peca_selecionada
			origem = (sx, sy)
			destino = (x, y)
			if (origem, destino) in jogadas_validas:
				self.peca_selecionada = destino
				self.destinos_validos = [dest for _, dest in jogadas_validas]
				if destino in self.destinos_validos and self.adjacente(sx, sy, x, y):
					capturou = self.move_peca(origem, destino)
					self.trata_captura(capturou, destino)

		#se a peça selecionada  anteriormente é uma peça do jogador atual
		#e a jogada é válida, faz a movimentação
		elif self.peca_selecionada:
			sx, sy = self.peca_selecionada
			origem = (sx, sy)
			destino = (x, y)
			if destino in self.destinos_validos and self.adjacente(sx, sy, x, y):
				capturou = self.move_peca(origem, destino)
				self.trata_captura(capturou, destino)
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
			self.destinos_validos = []
			self.troca_jogador()
			self.att_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
		self.att_cont_pecas()

#coletores
	def get_jogadas_obrigatorias(self):
		#verifica se, das jogadas disponíveis, quais resultam em captura
		#retorna uma lista de jogadas obrigatórias em formato [((Xor,Yor),(Xdest,Ydest))]
		#ex: jogadas = [((3,2),(2,2)),((2,3),(2,2))]

		jogadas = []
		jogadas.clear()
		self.origens_destacadas = []
		for x in range(TAMANHO):
			for y in range(TAMANHO):
				if self.tabuleiro[y][x] == self.jogador_atual:
					for destino in self.get_destinos_validos(x, y):
						if self.eh_captura(destino):
							self.origens_destacadas.append((x,y))
							jogadas.append(((x, y), destino))
		return jogadas

	def get_jogadas_disponiveis(self):
		#retorna uma lista de jogadas disponíveis em formato [((Xor,Yor),(Xdest,Ydest))]
		#ex: jogadas = (3,2) para (2,2) e (2,3) para (2,2) = [((3,2),(2,2)),((2,3),(2,2))]
		jogadas = []
		jogadas.clear()
		for x in range(TAMANHO):
			for y in range(TAMANHO):
				if self.tabuleiro[y][x] == self.jogador_atual:
					for destino in self.get_destinos_validos(x, y):
						jogadas.append(((x, y), destino))
		return jogadas

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
		direcoes = [(-1,0), (1,0), (0,-1), (0,1)]

		for dx, dy in direcoes:
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

	def checa_vitoria(self, adversario_desiste = False, eu_desisto = False, encerrar_jogo = False):
		peq_vitoria, vencedor = self.pequena_vitoria()
		capturas_j1 = self.qtd_pecas_jogador_capturou[JOGADOR1]
		capturas_j2 = self.qtd_pecas_jogador_capturou[JOGADOR2]

		if eu_desisto or adversario_desiste:
			if eu_desisto == True:
				vencedor = JOGADOR2 if self.rede.is_servidor else JOGADOR1
			if adversario_desiste == True:
				vencedor = JOGADOR1 if self.rede.is_servidor else JOGADOR2
			self.popup_game_over(f"Jogador {vencedor} venceu por desistência do oponente!")
		if capturas_j1 == PECAS_TOTAIS: #Jogador 1 capturou todas as peças
			self.bloqueia = True
			vencedor = JOGADOR1
			self.popup_game_over(f"Jogador {vencedor} venceu por capturar todas as peças do oponente!")
		elif capturas_j2 == PECAS_TOTAIS: #Jogador 2 capturou todas as peças
			self.bloqueia = True
			vencedor = JOGADOR2
			self.popup_game_over(f"Jogador {vencedor} venceu por capturar todas as peças do oponente!")
		elif not self.tem_movimentos(self.jogador_atual) and not self.fase_posicionamento: #Vitória por bloqueio
			vencedor = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
			self.bloqueia = True
			self.popup_game_over(f"Jogador {vencedor} venceu! ({self.jogador_atual} sem movimentos)")
		elif peq_vitoria:
			self.bloqueia = True
			self.popup_game_over(f"Jogador {vencedor} venceu! (pequena vitória)")
		elif encerrar_jogo:
			self.bloqueia = True
			if capturas_j1 > capturas_j2:
				vencedor = JOGADOR1
			elif capturas_j2 > capturas_j1:
				vencedor = JOGADOR2
			else:
				self.popup_game_over("Empate (mesmo número de peças capturadas)!")
				return
			self.popup_game_over(f"Jogador {vencedor} venceu por capturar mais que o oponente!")

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
						if self.eh_valido(nx, ny) and self.tabuleiro[ny][nx] is None:
							return True
		return False

#atualizadores
	def att_status(self, message):
		if message != None:
			self.label_status.config(text=message)

	def att_cont_pecas(self):
		#faz a contagem de todas as peças do tabuleiro e a quem pertencem
		p1 = sum(row.count(JOGADOR1) for row in self.tabuleiro)
		p2 = sum(row.count(JOGADOR2) for row in self.tabuleiro)

		#peças restantes a serem colocadas
		if self.fase_posicionamento:
			self.label_cont_pecas.config(text=f"Peças restantes - {JOGADOR1}: {PECAS_TOTAIS-p1} | {JOGADOR2}: {PECAS_TOTAIS-p2}")
		#peças restantes do jogador
		else:
			self.label_cont_pecas.config(text=f"Peças restantes - {JOGADOR1}: {p1} | {JOGADOR2}: {p2}")
			#sempre que houver uma atualização do tabuleiro, há a checagem de vitória
			self.checa_vitoria()

	def troca_jogador(self):
		self.jogador_atual = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
		self.peca_selecionada = None
		self.continua_movimento = False
		self.bloquear_botoes_tabuleiro()
		self.enviar_estado_do_jogo()
		#envia a mensagem de troca de jogador para o servidor

	def bloquear_botoes_tabuleiro(self, primeira_rodada = False):
		def bloqueia_tabuleiro():
			bloqueia_servidor = self.jogador_cliente == self.jogador_atual and self.rede.is_servidor
			bloqueia_cliente = self.jogador_servidor == self.jogador_atual and not self.rede.is_servidor
			if bloqueia_servidor or bloqueia_cliente:
				self.bloqueia = True
				self.att_status(f"Esperando o jogador {self.jogador_atual} jogar...")
		def libera_tabuleiro():
			libera_servidor = self.jogador_servidor == self.jogador_atual and self.rede.is_servidor
			libera_cliente = self.jogador_cliente == self.jogador_atual and not self.rede.is_servidor
			if libera_servidor or libera_cliente:
				self.bloqueia = False
				self.att_status(f"Fase de posicionamento - Jogador: {self.jogador_atual}")
		vez_servidor = self.jogador_servidor == self.jogador_atual and self.rede.is_servidor
		vez_cliente = self.jogador_cliente == self.jogador_atual and not self.rede.is_servidor
		if self.fase_posicionamento:
			bloqueia_tabuleiro()
			libera_tabuleiro()
		else:
			if vez_servidor or vez_cliente:
				self.bloqueia = False
				self.att_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
			else:
				self.bloqueia = True
				self.att_status(f"Esperando o jogador {self.jogador_atual} jogar...")

	def att_jogo(self, enviar=True, message=None):
		if enviar:
			self.enviar_estado_do_jogo()
		if not self.jogo_parado:
			self.bloquear_botoes_tabuleiro()
		self.att_status(message)
		self.checa_vitoria()

	def enviar_estado_do_jogo(
		self,
		eu_desisto = None,
		encerrar_jogo = False,
		mensagem_chat_para_enviar = None,
		desligar = False,
		reiniciar = False,
		fase_movimento = False
		):
		# Envia o estado do jogo para o outro jogador
		mensagem_para_enviar = json.dumps({
			"tabuleiro": self.tabuleiro,
			"jogador_atual": self.jogador_atual,
			"pecas_capturadas": self.qtd_pecas_jogador_capturou,
			"encerra_jogo": encerrar_jogo,
			"desistencia": eu_desisto,
			"mensagem_chat": mensagem_chat_para_enviar,
			"desligar": desligar,
			"reiniciar": reiniciar,
			"fase_movimento": fase_movimento
		})
		self.rede.enviar(mensagem_para_enviar)

	def att_jogo_com_dados(self, dados):
		dados = json.loads(dados)

		# for widget in self.frame_inferior.winfo_children():
		# 	if isinstance(widget, tk.Button):
		# 		widget.config(state='disabled')

		#atualiza o estado do jogo com base nos dados recebidos
		self.tabuleiro = dados["tabuleiro"]
		self.jogador_atual = dados["jogador_atual"]
		self.qtd_pecas_jogador_capturou = dados["pecas_capturadas"]

		self.desenha_tabuleiro()
		self.att_cont_pecas()

		oponente = JOGADOR2 if self.rede.is_servidor else JOGADOR1
		if dados["mensagem_chat"]!=None:
			self.exibir_mensagem_chat(f"{oponente}: {dados['mensagem_chat']}")
		if dados["desistencia"] == True:
			self.checa_vitoria(adversario_desiste = True)
		if dados["encerra_jogo"] == True:
			self.quer_encerrar = True if tkmsg.askquestion("Encerrar jogo", f"{oponente} quer encerrar o jogo. Aceitar?") == 'yes' else False
			if self.quer_encerrar:
				self.att_jogo(enviar=False)
				self.enviar_estado_do_jogo(encerrar_jogo=self.quer_encerrar)
				self.checa_vitoria(encerrar_jogo=True)
			else:
				self.att_status(f"Fase de movimento - Jogador: {self.jogador_atual}")
		if dados["desligar"] == True:
			self.att_status("Encerrando o jogo...")
			time.sleep(5)
			self.root.destroy()
		if dados["fase_movimento"] == True:
			self.fase_posicionamento = False
		# for widget in self.frame_inferior.winfo_children():
		# 	if isinstance(widget, tk.Button):
		# 		if self.jogo_parado and widget['text']=='Pedir para reiniciar o jogo':
		# 			widget.config(state="normal")
		# 		elif not self.jogo_parado:
		# 			widget.config(state="normal")
		self.att_jogo(enviar=False)
	
	def exibir_mensagem_chat(self, mensagem):
		remetente = self.jogador_servidor if not self.rede.is_servidor else self.jogador_cliente
		self.chat_text.config(state='normal')
		self.chat_text.insert(tk.END, f"{mensagem}\n")
		self.chat_text.config(state='disabled')
		self.chat_text.see(tk.END)
		self.chat_entry.delete(0, tk.END)
	
	def enviar_mensagem_chat(self, event=None):
		remetente = self.jogador_servidor if self.rede.is_servidor else self.jogador_cliente
		mensagem = self.chat_entry.get()
		if mensagem.strip():
			self.chat_text.config(state='normal')
			self.chat_text.insert(tk.END, f"{remetente}: {mensagem}\n")
			self.chat_text.config(state='disabled')
			self.chat_text.see(tk.END)
			self.chat_entry.delete(0, tk.END)
		self.enviar_estado_do_jogo(mensagem_chat_para_enviar=mensagem)

#final do jogo
	def desistencia(self):
		confirma = tkmsg.askquestion("Desistir", "Você tem certeza que deseja desistir?")
		if confirma == "yes":
			self.enviar_estado_do_jogo(eu_desisto=True)
			self.checa_vitoria(eu_desisto=True)

	def encerra_jogo(self):
		self.quer_encerrar = True
		confirma = tkmsg.askquestion("Encerrar jogo", "Você tem certeza que deseja encerrar o jogo?")
		if confirma == "yes":
			self.att_jogo(enviar=True)
			self.enviar_estado_do_jogo(encerrar_jogo=True)
			self.checa_vitoria(encerrar_jogo=True)

	def popup_game_over(self, mensagem):
		if tkmsg.askyesno("Reiniciar", f"{mensagem} Deseja jogar novamente?"):
			self.reinicia_jogo()
		else:
			self.enviar_estado_do_jogo(mensagem_chat_para_enviar="Encerrando o jogo...")
			self.att_status("Encerrando o jogo...")
			self.enviar_estado_do_jogo(desligar = True)
			time.sleep(5)
			self.root.destroy()

	def reinicia_jogo(self):
		self.set_jogo((JOGADOR1, JOGADOR2))
		self.att_cont_pecas()
		self.enviar_estado_do_jogo(reiniciar = True)
		self.desenha_tabuleiro()

class GerenciadorSocket:
	def __init__(self,att_jogo_com_dados):
		self.conexao = None
		self.is_servidor = False
		self.att_jogo_com_dados = att_jogo_com_dados

		try:
			#cria um socket e tenta se conectar ao servidor como cliente
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.connect((HOST, PORT))
			self.conexao = self.socket
			print(f"Conectado ao servidor como CLIENTE")
		except:
			#se não conseguir, cria um socket e aguarda conexão como servidor
			self.socket.close()
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.bind((HOST, PORT))
			self.socket.listen(1)
			print(f"Aguardando conexão como SERVIDOR em {HOST}:{PORT}")
			self.conexao, endereco = self.socket.accept()
			print(f"Conectado ao cliente {endereco}")
			self.is_servidor = True
			print("Cliente conectado.")
		#Threads para ter mais de uma aplicalção com o mesmo código
		threading.Thread(target=self.receber, daemon=True).start()

	def enviar(self, mensagem):
		# Envia a mensagem para o outro jogador
		if self.conexao:
			self.conexao.sendall(mensagem.encode())

	def receber(self):
		# Recebe mensagens do outro jogador
		while True:
			try:
				dados = self.conexao.recv(BUFFER).decode()
				if dados:
					self.att_jogo_com_dados(dados)
			except Exception as e:
				print(f"Erro ao receber dados: {e}")
				break
# class Chat:
# 	def __init__(self, root):
# 		self.root = root
# 		self.chat_frame = tk.Frame(root)
# 		self.chat_frame.pack()

# 		self.chat_text = tk.Text(self.chat_frame, width=50, height=10, state='disabled')
# 		self.chat_text.pack()

# 		self.chat_entry = tk.Entry(self.chat_frame, width=50)
# 		self.chat_entry.bind("<Return>", self.enviar_mensagem_chat)
# 		self.chat_entry.pack()

# 		self.send_button = tk.Button(self.chat_frame, text="Enviar", command=self.enviar_mensagem_chat)
# 		self.send_button.pack()

# 	def enviar_mensagem_chat(self, event=None):
# 		mensagem = self.chat_entry.get()
# 		if mensagem.strip():
# 			self.chat_text.config(state='normal')
# 			self.chat_text.insert(tk.END, f"Você: {mensagem}\n")
# 			self.chat_text.config(state='disabled')
# 			self.chat_text.see(tk.END)
# 			self.chat_entry.delete(0, tk.END)

# class Cliente(threading.Thread):
# 	def __init__(self, host, port):
# 		self.host = host
# 		self.port = port
# 		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 		self.nome = None #TODO definir o nome do jogador
# 		self.messages = []

# 	def iniciar(self):
# 		self.sock.connect((self.host, self.port))
# 		print(f"Conectado ao servidor {self.host}:{self.port}")

# 		# Inicia a thread de envio de mensagens
# 		enviar = Envia(self.sock, self.host, self.port)
# 		enviar.start()

# 		# Inicia a thread de recebimento de mensagens
# 		receber = Recebe(self.sock, self.nome)
# 		receber.start()
# 		return receber

# class Envia(threading.Thread):
# 	def __init__(self, sock, host, port):
# 		super().__init__()
# 		self.sock = sock
# 		self.host = host
# 		self.port = port

# 	def run(self):
# 		while True:
# 			mensagem = input("Digite sua mensagem: ") #TODO modificar a variavel para receber a mensagem da caixa de chat
# 			if mensagem.lower() == "sair":
# 				break
# 			self.sock.sendall(mensagem.encode())
# 		self.sock.close()

# class Recebe(threading.Thread):
# 	def __init__(self, sock, name):
# 		super().__init__()
# 		self.sock = sock
# 		self.name = name
# 		self.messagens = None

# 	def run(self):
# 		while True:
# 			mensagem = self.sock.recv(BUFFER).decode('utf-8') #TODO modificar a variavel para exibir a mensagem na caixa de chat
# 			if not mensagem:
# 				break
# 			print(f"{nome}: {mensagem}")
# 		self.sock.close()

# class Servidor(threading.Thread):
# 	def __init__(self, host, port):
# 		super().__init__()
# 		self.conexao = [] #lista de conexões ativas
# 		self.host = host
# 		self.port = port
# 		self.nome = None #TODO definir o nome do jogador

# 	def run(self):
# 		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 		sock.bind((self.host, self.port))

# 		sock.listen(1) #limite de conexões simultâneas
# 		print(f"Servidor rodando em {self.host}:{self.port}")
# 		while True:
# 			conexao, endereco = sock.accept()
# 			print(f"Conexão estabelecida com {endereco}")

# 			#cria um thread para tratar o cliente
# 			server_socket = ServerSocket(conexao, endereco, self)
# 			#inicia uma thread para receber mensagens do cliente
# 			server_socket.start()
# 			#adiciona o thread à lista de conexões
# 			self.connections = server_socket

# 	def broadcast(self, mensagem, origem):
# 		for connection in self.connections:
# 			if connection.sockname != origem:
# 				connection.send(mensagem)

# 	def remove_conexao(self, conexao):
# 		self.connections.remove(conexao)

# class ServerSocket(threading.Thread):
# 	def __init__(self, conexao, sockname, servidor):
# 		super().__init__()
# 		self.conexao = conexao
# 		self.sockname = sockname
# 		self.servidor = servidor

# 	def run(self):
# 		while True:
# 			mensagem = self.conexao.recv(BUFFER).decode('ascii')
# 			if mensagem:
# 				print(f"{self.sockname} diz: {mensagem}")
# 				self.servidor.broadcast(mensagem, self.sockname)
# 			else:
# 				print(f"{self.sockname} fechou a conexão")
# 				self.conexao.close()
# 				self.servidor.remove_conexao(self)
# 				return

# 	def enviar(self, mensagem):
# 		if self.conexao:
# 			try:
# 				self.conexao.sendall(mensagem.encode())
# 			except Exception as e:
# 				print(f"Erro ao enviar mensagem: {e}")

# def sair(servidor):
# 	while True:
# 		comando = input("Digite 'sair' para encerrar o servidor: ")
# 		if comando.lower() == "sair":
# 			servidor.conexao.close()
# 			break

if __name__ == "__main__":
	JogoSeega()
	

	# parser = argparse.ArgumentParser(description="Chatroom Server")
	# parser.add_argument("host", help="Interface the server listens to")
	# parser.add_argument("-p", metavar='PORT', type=int, default=12345, help="TCP port (default: 12345)")

	# args = parser.parse_args()

	# exit = threading.Thread(target=exit, args=(server,))
	# exit.start()