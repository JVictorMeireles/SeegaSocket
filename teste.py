import tkinter as tk

TAMANHO_CASA = 60
LINHAS, COLUNAS = 5, 5
COR_TABULEIRO = "#DDB88C"
COR_LINHAS = "black"
COR_P1 = "black"
COR_P2 = "white"
COR_DESTAQUE = "yellow"

class JogoSeega:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=COLUNAS * TAMANHO_CASA, height=LINHAS * TAMANHO_CASA)
        self.canvas.pack()
        self.estado_inicial()

        self.canvas.bind("<Button-1>", self.clique)
        self.botao_reset = tk.Button(root, text="Reiniciar Jogo", command=self.estado_inicial)
        self.botao_reset.pack()

        self.label_turno = tk.Label(root, text="")
        self.label_turno.pack()

    def estado_inicial(self):
        self.tabuleiro = [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]
        self.jogador_atual = "P1"
        self.fase_colocacao = True
        self.pecas_para_colocar = {"P1": 12, "P2": 12}
        self.selecionado = None
        self.captura_em_andamento = False
        self.origens_destacadas = []
        self.desenhar_tabuleiro()
        self.atualizar_label_turno()

    def desenhar_tabuleiro(self):
        self.canvas.delete("all")

        # Desenha o tabuleiro
        for i in range(LINHAS):
            for j in range(COLUNAS):
                x1, y1 = j * TAMANHO_CASA, i * TAMANHO_CASA
                x2, y2 = x1 + TAMANHO_CASA, y1 + TAMANHO_CASA
                cor = "white"
                if (i == 0 and j == 0) or (i == 0 and j == 4) or (i == 4 and j == 0) or (i == 4 and j == 4) or (i == 2 and j == 2):
                    cor = "gray"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=cor)

                # Desenha as peças
                peca = self.tabuleiro[i][j]
                if peca == "P1":
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill="blue")
                elif peca == "P2":
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill="red")

        # Destaca a origem selecionada
        if self.origem_selecionada:
            i, j = self.origem_selecionada
            x1, y1 = j * TAMANHO_CASA, i * TAMANHO_CASA
            x2, y2 = x1 + TAMANHO_CASA, y1 + TAMANHO_CASA
            self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, outline="green", width=3)

        # Somente chama o destaque se NÃO estivermos na fase de colocação
        if not self.fase_colocacao:
            self.destacar_origens_obrigatorias()


    def posicao_para_indices(self, x, y):
        return y // TAMANHO_CASA, x // TAMANHO_CASA

    def clique(self, evento):
        i, j = self.posicao_para_indices(evento.x, evento.y)

        if self.fase_colocacao:
            if self.tabuleiro[i][j] is None and not (i == 2 and j == 2):
                self.tabuleiro[i][j] = self.jogador_atual
                self.pecas_para_colocar[self.jogador_atual] -= 1
                if all(qtd == 0 for qtd in self.pecas_para_colocar.values()):
                    self.fase_colocacao = False
                else:
                    self.trocar_turno()
                self.desenhar_tabuleiro()
        else:
            if self.selecionado:
                if self.movimento_valido(self.selecionado, (i, j)):
                    self.realizar_movimento(self.selecionado, (i, j))
            elif self.tabuleiro[i][j] == self.jogador_atual:
                if not self.captura_em_andamento and (not self.origens_destacadas or (i, j) in self.origens_destacadas):
                    self.selecionado = (i, j)

    def movimento_valido(self, origem, destino):
        oi, oj = origem
        di, dj = destino
        if not (0 <= di < LINHAS and 0 <= dj < COLUNAS):
            return False
        if self.tabuleiro[di][dj] is not None:
            return False
        if (oi == di and abs(oj - dj) == 1) or (oj == dj and abs(oi - di) == 1):
            return True
        return False

    def realizar_movimento(self, origem, destino):
        oi, oj = origem
        di, dj = destino
        self.tabuleiro[di][dj] = self.tabuleiro[oi][oj]
        self.tabuleiro[oi][oj] = None
        self.selecionado = None

        capturou = self.verificar_captura((di, dj))
        self.desenhar_tabuleiro()

        if capturou:
            self.captura_em_andamento = True
            self.origens_destacadas = [ (di, dj) ] if self.tem_captura((di, dj)) else []
            if not self.origens_destacadas:
                self.captura_em_andamento = False
                self.trocar_turno()
        else:
            if self.captura_em_andamento:
                return
            self.trocar_turno()

        self.desenhar_tabuleiro()

    def trocar_turno(self):
        self.jogador_atual = "P2" if self.jogador_atual == "P1" else "P1"
        self.selecionado = None
        self.captura_em_andamento = False
        self.origens_destacadas = self.obter_origens_com_captura()
        self.atualizar_label_turno()

    def verificar_captura(self, destino):
        di, dj = destino
        oponente = "P2" if self.jogador_atual == "P1" else "P1"
        capturou = False

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = di + dx, dj + dy
            ai, aj = di + 2*dx, dj + 2*dy
            if 0 <= ni < LINHAS and 0 <= nj < COLUNAS and self.tabuleiro[ni][nj] == oponente:
                if 0 <= ai < LINHAS and 0 <= aj < COLUNAS and self.tabuleiro[ai][aj] == self.jogador_atual:
                    self.tabuleiro[ni][nj] = None
                    capturou = True
        return capturou

    def tem_captura(self, origem):
        i, j = origem
        jogador = self.tabuleiro[i][j]
        if jogador != self.jogador_atual:
            return False

        oponente = "P2" if jogador == "P1" else "P1"

        direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in direcoes:
            ni, nj = i + dx, j + dy
            ai, aj = i + 2*dx, j + 2*dy

            if (
                0 <= ni < LINHAS and 0 <= nj < COLUNAS and
                self.tabuleiro[ni][nj] == oponente and
                0 <= ai < LINHAS and 0 <= aj < COLUNAS and
                self.tabuleiro[ai][aj] == jogador
            ):
                return True

        return False

    def obter_origens_com_captura(self):
        origens = []
        for i in range(LINHAS):
            for j in range(COLUNAS):
                if self.tabuleiro[i][j] == self.jogador_atual and self.tem_captura((i,j)):
                    origens.append((i,j))
        return origens

    def destacar_origens_obrigatorias(self):
        self.origens_obrigatorias.clear()

        if self.fase_colocacao:
            return  # Proteção extra

        for i in range(LINHAS):
            for j in range(COLUNAS):
                if self.tabuleiro[i][j] == self.jogador_atual:
                    if self.tem_captura((i, j)):
                        self.origens_obrigatorias.append((i, j))
                        x1, y1 = j * TAMANHO_CASA, i * TAMANHO_CASA
                        x2, y2 = x1 + TAMANHO_CASA, y1 + TAMANHO_CASA
                        self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, outline="yellow", width=3)

    def atualizar_label_turno(self):
        p1_restantes = sum(row.count("P1") for row in self.tabuleiro)
        p2_restantes = sum(row.count("P2") for row in self.tabuleiro)
        self.label_turno.config(text=f"Turno: {self.jogador_atual} | P1: {p1_restantes} peças | P2: {p2_restantes} peças")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Seega")
    jogo = JogoSeega(root)
    root.mainloop()
