from typing import Set, Tuple, List

# Literal: (Sinal, Entidade, X, Y) ex: (True, 'P', 1, 2) -> verdadeiro tem poço em 1,2
Literal = Tuple[bool, str, int, int]
# Clausula: Representação de ORs. Frozenset garante imutabilidade e hash O(1).
Clausula = frozenset

class BaseConhecimento:
    def __init__(self):
        self.clausulas: Set[Clausula] = set()
        self.casas_mapeadas: set = set()
        
    def tell(self, clausula: Clausula):
        # injeta uma cláusula CNF bruta
        if clausula not in self.clausulas:
            self.clausulas.add(clausula)

    def tell_fato(self, literal: Literal):
        # Atalho para injetar um fato
        self.tell(frozenset([literal]))

    def registrar_leis_da_casa(self, x: int, y: int, vizinhos: List[Tuple[int, int]]):
        """
        Gera as regras físicas (Brisa e Fedor) estritamente para a vizinhança atual.
        A lista de vizinhos válidos é agora injetada pelo Agente/Ambiente, 
        removendo a dependência de mapas 4x4.
        """
        if (x, y) in self.casas_mapeadas:
            return
                    
        # leis da Brisa (B = Poço)
        clausula_brisa = [(False, 'B', x, y)]
        for nx, ny in vizinhos:
            clausula_brisa.append((True, 'P', nx, ny))
            self.tell(frozenset([(False, 'P', nx, ny), (True, 'B', x, y)]))
        self.tell(frozenset(clausula_brisa))

        # leis do Fedor (F = Wumpus)
        clausula_fedor = [(False, 'F', x, y)]
        for nx, ny in vizinhos:
            clausula_fedor.append((True, 'W', nx, ny))
            self.tell(frozenset([(False, 'W', nx, ny), (True, 'F', x, y)]))
        self.tell(frozenset(clausula_fedor))
        
        self.casas_mapeadas.add((x, y))

    def _resolver_duas_clausulas(self, c1: Clausula, c2: Clausula) -> set:
        # junta duas cláusulas ao encontrar literais complementares e bloqueia tautologias
        novas_clausulas_resolvidas = set()
        
        for literal_a in c1:
            complementar = (not literal_a[0], literal_a[1], literal_a[2], literal_a[3])
            
            if complementar in c2:
                nova_clausula = set(c1) | set(c2)
                nova_clausula.remove(literal_a)
                nova_clausula.remove(complementar)
                
                # bloqueio de Tautologia
                tautologia = False
                for lit in nova_clausula:
                    oposto_interno = (not lit[0], lit[1], lit[2], lit[3])
                    if oposto_interno in nova_clausula:
                        tautologia = True
                        break
                        
                if not tautologia:
                    novas_clausulas_resolvidas.add(frozenset(nova_clausula))
                    
        return novas_clausulas_resolvidas

    def ask(self, pergunta: Literal) -> bool:
        # executa a inferência por resolução matemática e retorna True se a pergunta for 100% provada pelas leis e factos da base
        pergunta_negada = (not pergunta[0], pergunta[1], pergunta[2], pergunta[3])
        clausulas_temporarias = set(self.clausulas)
        clausulas_temporarias.add(frozenset([pergunta_negada]))
        
        while True:
            novas_desta_rodada = set()
            lista_clausulas = list(clausulas_temporarias)
            tamanho = len(lista_clausulas)
            
            for i in range(tamanho):
                for j in range(i + 1, tamanho):
                    resolvidas = self._resolver_duas_clausulas(lista_clausulas[i], lista_clausulas[j])
                    
                    if frozenset() in resolvidas:
                        return True
                        
                    for nova in resolvidas:
                        util = True
                        for existente in clausulas_temporarias:
                            if existente.issubset(nova):
                                util = False
                                break
                        if util:
                            novas_desta_rodada.add(nova)
            
            if novas_desta_rodada.issubset(clausulas_temporarias):
                return False
                
            clausulas_temporarias.update(novas_desta_rodada)