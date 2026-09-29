"""AGENTE C — Lógico + objetivo, com planejamento por BFS (Aulas 3, 4 e 6).  [0,6 ponto]

Reaproveita o Agente B para saber ONDE é seguro e usa busca em largura (BFS)
para planejar COMO chegar lá. Máquina de estados sugerida (slide 10):

  EXPLORAR  → BFS até a casa segura não visitada mais próxima
  AGARRAR   → quando houver brilho na casa atual
  VOLTAR    → BFS até (1,1) passando apenas por casas provadas seguras
  SAIR      → chegou em (1,1) com o ouro

Decisão aberta — o dilema do risco: sem casa segura e sem ouro, o agente deve
sair, atirar a flecha (−10) ou arriscar uma casa incerta? Decidam por utilidade
esperada e justifiquem no relatório.

A função acoes_para_vizinho() (em wumpus) transforma cada passo do caminho da BFS
em giros + AVANCAR. A BFS em si é implementação do grupo.
"""

import random
from collections import deque
from wumpus import Agente, Acao, Direcao, Percepcao
from wumpus.ambiente import vizinhos, acoes_para_vizinho
from agentes.motor_inferencia import BaseConhecimento

class AgenteObjetivo(Agente):
    nome = "Agente C (Objetivo)"

    def __init__(self):
        super().__init__()
        self.base = BaseConhecimento()
        
        # bussola
        self.x = 1
        self.y = 1
        self.direcao = Direcao.LESTE
        self.pegou_ouro = False
        
        # memoria
        self.visitadas = set()
        self.casas_seguras = set([(1, 1)])
        
        # piloto 
        self.caminho_atual = []
        self.fila_acoes = []
        
        # rastreamento
        self.ultima_acao = None
        self.tentativa_x = 1
        self.tentativa_y = 1

    def _atualizar_posicao_interna(self, percepcao: Percepcao):
        #atualiza a bussola interna
        if self.ultima_acao == Acao.AVANCAR:
            if percepcao.baque:
                # rota impedida = limpa o plano
                self.tentativa_x = self.x
                self.tentativa_y = self.y
                self.caminho_atual.clear()
                self.fila_acoes.clear()
            else:
                self.x = self.tentativa_x
                self.y = self.tentativa_y
                
        elif self.ultima_acao == Acao.VIRAR_ESQUERDA:
            giros = {Direcao.NORTE: Direcao.OESTE, Direcao.OESTE: Direcao.SUL, 
                     Direcao.SUL: Direcao.LESTE, Direcao.LESTE: Direcao.NORTE}
            self.direcao = giros[self.direcao]
            
        elif self.ultima_acao == Acao.VIRAR_DIREITA:
            giros = {Direcao.NORTE: Direcao.LESTE, Direcao.LESTE: Direcao.SUL, 
                     Direcao.SUL: Direcao.OESTE, Direcao.OESTE: Direcao.NORTE}
            self.direcao = giros[self.direcao]

    def _projetar_avanco(self):
        if self.direcao == Direcao.NORTE: return self.x, self.y + 1
        if self.direcao == Direcao.SUL:   return self.x, self.y - 1
        if self.direcao == Direcao.LESTE: return self.x + 1, self.y
        if self.direcao == Direcao.OESTE: return self.x - 1, self.y

    def _calcular_rota_bfs(self, origem, destino):
        #busca de voltar pra casa
        if origem == destino: return []
            
        fila = deque([(origem, [])])
        visitados_bfs = set([origem])
        direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        while fila:
            atual, caminho = fila.popleft()
            x, y = atual
            
            for dx, dy in direcoes:
                vizinho = (x + dx, y + dy)
                if vizinho == destino:
                    return caminho + [vizinho]
                    
                if vizinho in self.casas_seguras and vizinho not in visitados_bfs:
                    visitados_bfs.add(vizinho)
                    fila.append((vizinho, caminho + [vizinho]))
        return []

    def _definir_destino(self, pos_atual):
        #tomada de decisão
        if self.pegou_ouro:
            return (1, 1)

        candidatas = self.casas_seguras - self.visitadas
        if not candidatas:
            return (1, 1) # cenário de "sobrevivência": mapa isolado, foge.

        rota_mais_curta = None
        melhor_destino = None

        for candidata in candidatas:
            rota = self._calcular_rota_bfs(pos_atual, candidata)
            if rota:
                if rota_mais_curta is None or len(rota) < len(rota_mais_curta):
                    rota_mais_curta = rota
                    melhor_destino = candidata
                    
        return melhor_destino if melhor_destino else (1, 1)

    def agir(self, percepcao: Percepcao) -> Acao:
        self._atualizar_posicao_interna(percepcao)
        pos_atual = (self.x, self.y)
        
        # ouro
        if percepcao.brilho and not self.pegou_ouro:
            self.pegou_ouro = True
            self.ultima_acao = Acao.AGARRAR
            # limpa a fila pra forçar a voltar pra casa
            self.caminho_atual.clear()
            self.fila_acoes.clear()
            return Acao.AGARRAR
            
        if self.pegou_ouro and pos_atual == (1, 1):
            self.ultima_acao = Acao.SAIR
            return Acao.SAIR

        # minimapa
        if pos_atual not in self.visitadas:
            self.visitadas.add(pos_atual)
            self.base.tell_fato((False, 'P', self.x, self.y))
            self.base.tell_fato((False, 'W', self.x, self.y))
            self.base.tell_fato((percepcao.brisa, 'B', self.x, self.y))
            self.base.tell_fato((percepcao.fedor, 'F', self.x, self.y))
            self.base.registrar_leis_da_casa(self.x, self.y, vizinhos(pos_atual))

        # analisar por casas seguras
        for nx, ny in vizinhos(pos_atual):
            vizinho = (nx, ny)
            if vizinho not in self.casas_seguras:
                provado_sem_poco = self.base.ask((False, 'P', nx, ny))
                provado_sem_wumpus = self.base.ask((False, 'W', nx, ny))
                if provado_sem_poco and provado_sem_wumpus:
                    self.casas_seguras.add(vizinho)

        # micro gerenciamento: giros e avanços
        if self.fila_acoes:
            acao = self.fila_acoes.pop(0)
            if acao == Acao.AVANCAR:
                self.tentativa_x, self.tentativa_y = self._projetar_avanco()
            self.ultima_acao = acao
            return acao

        # passa para a próxima casa
        if self.caminho_atual:
            proximo_passo = self.caminho_atual.pop(0)
            self.fila_acoes = acoes_para_vizinho(pos_atual, self.direcao, proximo_passo)
            acao = self.fila_acoes.pop(0)
            if acao == Acao.AVANCAR:
                self.tentativa_x, self.tentativa_y = self._projetar_avanco()
            self.ultima_acao = acao
            return acao

        # plano sem rota-definir alvo e rodar BFS
        destino = self._definir_destino(pos_atual)
        
        if destino == pos_atual and destino == (1, 1):
            self.ultima_acao = Acao.SAIR
            return Acao.SAIR
            
        rota = self._calcular_rota_bfs(pos_atual, destino)
        if rota:
            self.caminho_atual = rota  
            proximo_passo = self.caminho_atual.pop(0)
            self.fila_acoes = acoes_para_vizinho(pos_atual, self.direcao, proximo_passo)
            
            acao = self.fila_acoes.pop(0)
            if acao == Acao.AVANCAR:
                self.tentativa_x, self.tentativa_y = self._projetar_avanco()
            self.ultima_acao = acao
            return acao

        # fallback contra "travamentos" não previstos
        self.ultima_acao = Acao.SAIR
        return Acao.SAIR