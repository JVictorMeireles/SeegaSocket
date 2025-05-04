import socket
import tkinter as tk
import tkinter.messagebox as tkmsg
import random as rd
import numpy as np
import threading

# Constantes
TAMANHO = 5
TAMANHO_CASA = 60
JOGADOR1 = "Verde"
JOGADOR2 = "Roxo"
PECAS_TOTAIS = 12
HOST = "localhost"
PORT = 12345

# Cores
COR_TABULEIRO = "#DDB88C"
COR_LINHA = "#000000"
COR_PECAS = {JOGADOR1: "green", JOGADOR2: "purple"}
COR_P1 = "green"
COR_P2 = "purple"
COR_DESTAQUE = "yellow"

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
		self.chat = Chat(root)

	def set_jogo(self,jogadores): #inicializa o jogo
		#inicializa o tabuleiro 5x5 vazio
		self.tabuleiro = [[None for _ in range(TAMANHO)] for _ in range(TAMANHO)]

		self.bloqueia = False
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
		self.canvas.pack(side='left', padx=5, pady=5)
		self.canvas.config(bg=COR_TABULEIRO)
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

		#botão de desistência
		self.bt_desistencia = tk.Button(root, text="Desistir", command=self.desistencia)
		self.bt_desistencia.pack()

		#botão de encerramento do jogo
		self.bt_encerrar_jogo = tk.Button(root, text="Encerrar", command=self.encerra_jogo)
		self.bt_encerrar_jogo.pack()

		#função de chat
		self.chat_frame = tk.Frame(root)
		self.chat_frame.pack(side='right', padx=5, pady=5)

		#conexão com o servidor
		self.cria_conexao_socket()

	def cria_conexao_socket(self):
		try:
			cliente = Cliente(HOST,	PORT)
			cliente.start()
		except ConnectionRefusedError:
			servidor = Servidor(HOST, PORT)
			servidor.start()

	def aguarda_conexao(self):
		# Aguarda a conexão de um cliente
		self.conexao, self.endereco_conectado = self.socket.accept()
		print(f"Conexão estabelecida com {self.endereco_conectado}")

		# Inicia uma thread para receber mensagens do cliente
		self.thread_receber = threading.Thread(target=self.receber_mensagens, daemon=True)
		self.thread_receber.start()

	def receber_mensagens(self):
		while True:
			try:
				# Recebe dados do cliente
				dados = self.conexao.recv(1024)
				if not dados:
					break
				mensagem = dados.decode()
				# Processa os dados recebidos (exibe no console)
				print(f"Recebido: {dados.decode()}")
			except Exception as e:
				print(f"Erro ao receber dados: {e}")
				break

	def enviar_mensagem(self, mensagem: str):
		if self.conexao:
			try:
				self.conexao.sendall(mensagem.encode())
			except Exception as e:
				print(f"Erro ao enviar mensagem: {e}")

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

	def checa_vitoria(self, p1, p2):
		peq_vitoria, vencedor = self.pequena_vitoria()
		if p2 == 0: #Jogador 1 capturou todas as peças
			self.bloqueia = True
			self.popup_game_over(f"Jogador {JOGADOR1} venceu!")
		elif p1 == 0: #Jogador 2 capturou todas as peças
			self.bloqueia = True
			self.popup_game_over(f"Jogador {JOGADOR2} venceu!")
		elif not self.tem_movimentos(self.jogador_atual): #Vitória por bloqueio
			vencedor = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
			self.bloqueia = True
			self.popup_game_over(f"Jogador {vencedor} venceu! ({self.jogador_atual} sem movimentos)")
		elif peq_vitoria:
			self.bloqueia = True
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
						if self.eh_valido(nx, ny) and self.tabuleiro[ny][nx] is None:
							return True
		return False

#atualizadores
	def att_status(self, message):
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
			self.checa_vitoria(p1, p2)

	def troca_jogador(self):
		self.jogador_atual = JOGADOR1 if self.jogador_atual == JOGADOR2 else JOGADOR2
		self.peca_selecionada = None
		self.continua_movimento = False
		#envia a mensagem de troca de jogador para o servidor

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

class Chat:
	#TODO implementar o chat
	def __init__(self, root):
		self.root = root
		self.chat_frame = tk.Frame(root)
		self.chat_frame.pack()

		self.chat_text = tk.Text(self.chat_frame, width=50, height=10, state='disabled')
		self.chat_text.pack()

		self.chat_entry = tk.Entry(self.chat_frame, width=50)
		self.chat_entry.bind("<Return>", self.enviar_mensagem)
		self.chat_entry.pack()

		self.send_button = tk.Button(self.chat_frame, text="Enviar", command=self.enviar_mensagem)
		self.send_button.pack()

	def desenha_chat(self):
		#área de mensagens
		self.chat_text = tk.Text(self.chat_frame, width=50, height=10)
		self.chat_text.pack()

		#desenha um retângulo para a entrada de mensagens
		self.chat_entry = tk.Entry(self.chat_frame, width=50)

	def enviar_mensagem(self, event=None):
		mensagem = self.chat_entry.get()
		if mensagem.strip():
			self.chat_text.config(state='normal')
			self.chat_text.insert(tk.END, f"Você: {mensagem}\n")
			self.chat_text.config(state='disabled')
			self.chat_text.see(tk.END)
			self.chat_entry.delete(0, tk.END)

class Cliente(threading.Thread):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.name = None #TODO definir o nome do jogador
		self.messages = None

	def iniciar(self):
		self.sock.connect((self.host, self.port))
		print(f"Conectado ao servidor {self.host}:{self.port}")

		# Inicia a thread de envio de mensagens
		enviar = Envia(self.sock, self.host, self.port)
		enviar.start()

		# Inicia a thread de recebimento de mensagens
		receber = Recebe(self.sock, self.name)
		receber.start()
		return receber

class Envia(threading.Thread):
	def __init__(self, sock, host, port):
		super().__init__()
		self.sock = sock
		self.host = host
		self.port = port

	def run(self):
		while True:
			mensagem = input("Digite sua mensagem: ")
			if mensagem.lower() == "sair":
				break
			self.sock.sendall(mensagem.encode())
		self.sock.close()

class Recebe(threading.Thread):
	def __init__(self, sock, name):
		super().__init__()
		self.sock = sock
		self.name = name
		self.messages = None

	def run(self):
		while True:
			mensagem = self.sock.recv(1024).decode('utf-8')
			if not mensagem:
				break
			print(f"{nome}: {mensagem}")
		self.sock.close()

class Servidor(threading.Thread):
	def __init__(self, host, port):
		super().__init__()
		self.conexao = None
		self.host = host
		self.port = port

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((self.host, self.port))

		sock.listen(1)
		print(f"Servidor rodando em {self.host}:{self.port}")
		while True:
			conexao, endereco = sock.accept()
			print(f"Conexão estabelecida com {endereco}")

			#cria um thread para tratar o cliente
			server_socket = ServerSocket(conexao, endereco, self)
			#inicia uma thread para receber mensagens do cliente
			server_socket.start()
			#adiciona o thread à lista de conexões
			self.connections = server_socket

	def broadcast(self, mensagem, origem):
		for connection in self.connections:
			if connection.sockname != origem:
				connection.send(mensagem)

	def remove_conexao(self, conexao):
		self.connections.remove(conexao)

class ServerSocket(threading.Thread):
	def __init__(self, conexao, sockname, servidor):
		super().__init__()
		self.conexao = conexao
		self.sockname = sockname
		self.servidor = servidor

	def run(self):
		while True:
			mensagem = self.conexao.recv(1024).decode('ascii')
			if mensagem:
				print(f"{self.sockname} diz: {mensagem}")
				self.servidor.broadcast(mensagem, self.sockname)
			else:
				print(f"{self.sockname} fechou a conexão")
				self.conexao.close()
				self.servidor.remove_conexao(self)
				return

	def enviar(self, mensagem):
		if self.conexao:
			try:
				self.conexao.sendall(mensagem.encode())
			except Exception as e:
				print(f"Erro ao enviar mensagem: {e}")

def sair(servidor):
	while True:
		comando = input("Digite 'sair' para encerrar o servidor: ")
		if comando.lower() == "sair":
			servidor.conexao.close()
			break

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Seega")
	game = SeegaGame(root)
	root.mainloop()

	parser = argparse.ArgumentParser(description="Chatroom Server")
	parser.add_argument("host", help="Interface the server listens to")
	parser.add_argument("-p", metavar='PORT', type=int, default=12345, help="TCP port (default: 12345)")

	args = parser.parse_args()

	exit = threading.Thread(target=exit, args=(server,))
	exit.start()