"""AGENTE B — Agente lógico baseado em conhecimento (Aula 6).        [1,3 ponto]

Ciclo: PERCEPÇÃO → TELL → BC → ASK (resolução) → AÇÃO

Critérios de avaliação (slide 08):
  1. Axiomas gerados por código para as casas (nada escrito à mão casa a casa):
        ¬P(1,1)   ¬W(1,1)
        B(x,y) ⇔ P(vizinhos)   em disjunção
        F(x,y) ⇔ W(vizinhos)   em disjunção
  2. Percepções entram na BC SOMENTE via tell().
  3. A segurança de uma casa é decidida SOMENTE via ask(), por resolução por
     refutação: BC ∧ ¬α ⊢ □ (cláusula vazia)  ⇒  BC ⊨ α.
  4. Nada de "if brisa: evitar vizinhos" escondido no código.

Regras do jogo (slide 13):
  - A conversão para CNF e a resolução são implementadas pelo grupo.
  - sympy, pysat e z3 NÃO podem ser usados aqui; só em testes, para conferir resultados.

Dica de engenharia (slide 09): instancie as regras B e F apenas para as casas já
visitadas e guarde em cache as respostas de ask(). A BC enxuta é o que torna a
resolução tratável.

Liberdade de projeto: a representação de sentenças, literais e cláusulas é do grupo.
Uma sugestão simples é literal = (simbolo, positivo), por exemplo ("P13", False)
para ¬P(1,3), e cláusula = frozenset de literais. Justifique a escolha no relatório.
"""

import random
from wumpus import Agente, Acao, Direcao, Percepcao
from wumpus.ambiente import vizinhos, acoes_para_vizinho
from agentes.motor_inferencia import BaseConhecimento

class AgenteLogico(Agente):
    nome = "Agente B (Logico)"

    def __init__(self):
        super().__init__()
        self.base = BaseConhecimento()
        
        # bussola e Estado Interno
        self.x = 1
        self.y = 1
        self.direcao = Direcao.LESTE
        self.pegou_ouro = False
        
        self.visitadas = set()
        self.fila_acoes = []
        
        # variáveis de log de movimento
        self.ultima_acao = None
        self.tentativa_x = 1
        self.tentativa_y = 1

    def _atualizar_posicao_interna(self, percepcao: Percepcao):
        # atualiza a bussola interna lidando com bonk e giros
        if self.ultima_acao == Acao.AVANCAR:
            if percepcao.baque:
                # bateu na parede, troca a coordenada
                self.tentativa_x = self.x
                self.tentativa_y = self.y
            else:
                # avanço 
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
        # calcula qual será o X e Y se o agente usar AVANCAR agora
        if self.direcao == Direcao.NORTE: return self.x, self.y + 1
        if self.direcao == Direcao.SUL:   return self.x, self.y - 1
        if self.direcao == Direcao.LESTE: return self.x + 1, self.y
        if self.direcao == Direcao.OESTE: return self.x - 1, self.y

    def agir(self, percepcao: Percepcao) -> Acao:
        self._atualizar_posicao_interna(percepcao)
        pos_atual = (self.x, self.y)
        
        # OBJETIVOS IMEDIATOS
        if percepcao.brilho and not self.pegou_ouro:
            self.pegou_ouro = True
            self.ultima_acao = Acao.AGARRAR
            return Acao.AGARRAR
            
        if self.pegou_ouro and pos_atual == (1, 1):
            self.ultima_acao = Acao.SAIR
            return Acao.SAIR

        # se houver ações pendentes na fila (tipo giros), faz
        if self.fila_acoes:
            acao = self.fila_acoes.pop(0)
            if acao == Acao.AVANCAR:
                self.tentativa_x, self.tentativa_y = self._projetar_avanco()
            self.ultima_acao = acao
            return acao

        # ATUALIZAÇÃO DA BASE DE CONHECIMENTO
        vizinhos_reais = vizinhos(pos_atual)
        
        if pos_atual not in self.visitadas:
            self.visitadas.add(pos_atual)
            
            # fatos Se estou vivo aqui é pq não morri (não tem poço nem wumpus)
            self.base.tell_fato((False, 'P', self.x, self.y))
            self.base.tell_fato((False, 'W', self.x, self.y))
            
            # fatos sensoriais do turno
            self.base.tell_fato((percepcao.brisa, 'B', self.x, self.y))
            self.base.tell_fato((percepcao.fedor, 'F', self.x, self.y))
            
            # registrar as regras lógicas para os vizinhos baseadas no X, Y atual
            self.base.registrar_leis_da_casa(self.x, self.y, vizinhos_reais)

        # INFERÊNCIA E ESCOLHA DE ROTA
        casas_seguras_nao_visitadas = []
        casas_seguras_visitadas = []

        for nx, ny in vizinhos_reais:
            vizinho = (nx, ny)
            if vizinho in self.visitadas:
                casas_seguras_visitadas.append(vizinho)
                continue
                
            # núcleo Agente B: Resolução por Refutação
            provado_sem_poco = self.base.ask((False, 'P', nx, ny))
            provado_sem_wumpus = self.base.ask((False, 'W', nx, ny))
            
            if provado_sem_poco and provado_sem_wumpus:
                casas_seguras_nao_visitadas.append(vizinho)

        # DECISÃO DE MOVIMENTO
        destino = None
        if casas_seguras_nao_visitadas:
            # prioriza expandir o mapa de forma segura
            destino = random.choice(casas_seguras_nao_visitadas)
        elif casas_seguras_visitadas:
            # fallback: Recua para evitar soft-lock se as adjacências forem perigosas ou incertas
            destino = random.choice(casas_seguras_visitadas)
            
        if destino:
            # delega ao método geração da rota (Giro + Avanço)
            self.fila_acoes = acoes_para_vizinho(pos_atual, self.direcao, destino)
            acao = self.fila_acoes.pop(0)
            
            if acao == Acao.AVANCAR:
                self.tentativa_x, self.tentativa_y = self._projetar_avanco()
            self.ultima_acao = acao
            return acao

        # mundo impossivel ex: cercado por perigo na casa (1,1) ou preso.
        # sai da caverna para garantir os pontos de fuga e evitar a morte.
        self.ultima_acao = Acao.SAIR
        return Acao.SAIR