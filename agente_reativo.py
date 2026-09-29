"""AGENTE A — Reativo simples (Aula 4, tipo 1).                      [0,3 ponto]

Regras condição → ação, SEM MEMÓRIA: a decisão depende apenas da percepção atual.
Não guarde nada em self entre chamadas (nada de casas visitadas, "já peguei o ouro"
etc.). É o baseline do experimento e existe para mostrar o limite dos reativos.

Perguntas para guiar o projeto das regras:
  - O que fazer quando há brilho? E quando há brisa ou fedor?
  - Sem memória, como o agente sabe que já está com o ouro? E como volta a (1,1)?
  - O que fazer depois de um baque?
  - Qual regra evita que ele fique girando para sempre?

No relatório, explique quais mundos derrotam este agente e por quê.
"""

import random
from wumpus import Agente, Acao, Percepcao

class AgenteReativo(Agente):
    nome = "Agente A (Reativo)"

    def agir(self, percepcao: Percepcao) -> Acao:
        # pegar o ouro
        if percepcao.brilho:
            return Acao.AGARRAR

        # detectar perigo, entra em modo aleatório em vez de travar
        # ele vai tentar avançar, atirar ou girar para sair do loop
        if percepcao.fedor or percepcao.brisa:
            return random.choice([
                Acao.VIRAR_ESQUERDA, Acao.VIRAR_DIREITA, 
                Acao.AVANCAR, Acao.ATIRAR
            ])

        # comportamento padrão de exploração com peso maior para movimento.
        # Acao.SAIR é inserida na roleta, estatisticamente ent exista a chance de vitória caso ele tenha o ouro na casa inicial.
        return random.choice([
            Acao.AVANCAR, Acao.AVANCAR, Acao.AVANCAR,
            Acao.VIRAR_ESQUERDA, Acao.VIRAR_DIREITA, Acao.SAIR
        ])