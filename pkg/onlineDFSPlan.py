from random import randint
from state import State
import math

class OnlineDFSPlan:
    def __init__(self, problem, startState, name="explorar"):    
        """
        Plano para explorar o mapa, implementado utilizando DFS-Online.
        @param problem: crenças do agente (onde irá ser salvo o mapa da exploração)
        @param startState: coordenada de início do robô
        @param name: nome do plano
        """
        self.name = name
        self.initialState = startState
        self.currentState = startState
        self.prob = problem
        self.actions = ["S", "L", "N", "O"]

        self.untried = dict()  # mostra um array de ações ainda não tentadas no estado
        self.unbacktracked = dict()  # mostra uma fila de estados que levaram ao estado s
        for i in range(self.prob.maxRows):
            for j in range(self.prob.maxColumns):
                self.untried[(i, j)] = self.actions
                self.unbacktracked[(i, j)] = []

        self.result = {}  # mostra o estado resultado s' após executar ação a partir de s

    def updateCurrentState(self, state):
        self.currentState = state

    def isPossibleToMove(self, toState):
        """Verifica se eh possivel ir da posicao atual para o estado (lin, col) considerando 
        a posicao das paredes do labirinto e os limites do labirinto
        @param toState: instancia da classe State - um par (lin, col) - que aqui indica a posicao futura 
        @return: True quando é possivel ir do estado atual para o estado futuro """

        # vai para fora do labirinto
        if not (self.isCoordinateValid([toState.row, toState.col])):
            return False

        ## vai para cima de uma parede que já conheço
        if (self.isThereWall([toState.row, toState.col])):
            return False

        # Como não vai andar na diagonal, não precisa checar mais nada
        return True

    def getNextPosition(self):
        """ Pega uma ação ainda não tentada no estado atual e calcula a posicao futura do agente.
        Se não tem mais nenhuma ação, volta para o estado que fez com que o agente chegasse no estado atual
        Se não tiver mais nada para executar, termina a execução
        return: tupla contendo a acao (direcao) e o estado futuro resultante da movimentacao """

        position = (self.currentState.row, self.currentState.col)
        possibilities = self.untried[position].copy() # As possibilidades de movimentos são os movimentos que não tentei fazer ainda
        movePos = {"N": (-1, 0),
                   "S": (1, 0),
                   "L": (0, 1),
                   "O": (0, -1)}

        if len(possibilities) > 0: # Se ainda tem algum movimento que não tentei nessa posição
            rand = randint(0, len(possibilities)-1)
            # rand = 0
            movDirection = possibilities[rand] # Pega uma das possibilidades de movimento

            possibilities.pop(rand) # Remove o movimento que escolhi dos movimentos não tentados
            self.untried[position] = possibilities 
            state = State(self.currentState.row + movePos[movDirection][0], # Atualiza o estado que eu espero ir
                          self.currentState.col + movePos[movDirection][1])
        else: # Se já fiz todos os movimentos dessa posição, olho a lista de backtrack e volto uma posição
            if len(self.unbacktracked[position]) > 0:
                backtrackState = self.unbacktracked[position].pop(0) # Pego o primeiro elemento da lista de backtrack
                state = State(backtrackState[0], backtrackState[1]) # Coordenada para onde quero ir
                direction = (backtrackState[0] - position[0], backtrackState[1] - position[1])
                movDirection = list(movePos.keys())[list(movePos.values()).index(direction)] # Direção pra que preciso ir para chegar na coordenada desejada
            else: # Se não tem nenhum nó em unbacktracked, termina a execução
                movDirection = "nop"
                state = self.currentState

        return movDirection, state


    def chooseAction(self):
        """ Escolhe o proximo movimento. É a ação que vai ser executada pelo agente. 
        @return: tupla contendo a acao (direcao) e uma instância da classe State que representa a posição esperada após a execução
        """

        ## Tenta encontrar um movimento possivel dentro do tabuleiro 
        result = self.getNextPosition()
        currentPos = (self.currentState.row, self.currentState.col)
        nextPos = (result[1].row, result[1].col)

        if self.isPossibleToMove(result[1]) and result[0] != 'nop': 
            if (currentPos, result[0]) not in self.result.keys(): # Se eu ainda não sei o resultado de executar essa ação (result[0]) nessa posição (currentPos)
                self.result[(currentPos, result[0])] = nextPos # Adiciona que o resultado de executar a ação (result[0]) na currentPos resulta ir para nextPos
                self.unbacktracked[nextPos].insert(0, currentPos) # Adiciona a posição atual na frente da lista de unbacktracked da posição futura

        # Se é um movimento que não é possível de ser feito, tenta encontrar outro movimento
        if not self.isPossibleToMove(result[1]):
            return self.chooseAction()

        return result

    # Se for um local com parede, o valor no mapa é -2
    def isThereWall(self, pos):
        """ Verifica se o agente já detectou que há uma parede na coordenada especificada
        @param pos: coordenada que se quer checar se há parede """
        return self.prob.mazeBeliefs[pos[0]][pos[1]] == -2

    def isCoordinateValid(self, coord):
        """ Verifica se é uma coordenada dentro das fronteiras do mapa """
        return coord[0] >= 0 and coord[1] >= 0 and coord[0] < self.prob.maxRows and coord[1] < self.prob.maxColumns