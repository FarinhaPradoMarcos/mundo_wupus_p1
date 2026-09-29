# Mundo Wumpus · Primeira Avaliação de IA (UniAnchieta)

# Projeto Mundo do Wumpus - Agentes Racionais

**Grupo:**  
* Marcos Farinha – RA: 2403541  
* Gustavo Mattioli – RA: 2403394  
* João Casote – RA: 2403652  

---

## 📌 Descrição do Projeto
Este repositório contém a implementação e avaliação experimental de três arquiteturas de agentes autônomos operando no ambiente do **Mundo do Wumpus** sob observabilidade parcial:
1. **Agente A (Reativo Simples):** Baseado estritamente em regras de condição-ação, sem memória de estados passados.
2. **Agente B (Lógico Proposicional):** Mantém uma Base de Conhecimento (BC) em Forma Normal Conjuntiva (CNF), utilizando Inferência por Refutação (`TELL`/`ASK`) para garantir mortalidade zero.
3. **Agente C (Lógico + Planejador BFS):** Integra o motor de inferência lógica do Agente B a um algoritmo de Busca em Largura (BFS) em uma malha de segurança global, otimizando o consumo de ações e eliminando movimentações estocásticas.

---


