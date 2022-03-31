from random import randint
from state import State
import math
import copy

class LRTAStarPlan:
    def __init__(self, maxRows, maxColumns, goal, initialState, map, name="none", mesh="square"):
        """
        Define as variaveis necessárias para a utilização do LRTA* por um agente
        """
        self.name = name
        self.goalPos = goal

        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.initialState = initialState
        self.currentState = initialState
        self.map = map

    def updateCurrentState(self, state):
        self.currentState = state

    def isPossibleToMove(self, toState):
        """Verifica se eh possivel ir da posicao atual para o estado (lin, col) considerando 
        a posicao das paredes do labirinto e movimentos na diagonal
        @param toState: instancia da classe State - um par (lin, col) - que aqui indica a posicao futura 
        @return: True quando é possivel ir do estado atual para o estado futuro """

        ## vai para fora do labirinto
        if (toState.col < 0 or toState.row < 0):
            return False

        if (toState.col >= self.maxColumns or toState.row >= self.maxRows):
            return False

        if len(self.walls) == 0:
            return True

        ## vai para cima de uma parede
        if (toState.row, toState.col) in self.walls:
            return False

        # vai na diagonal? Caso sim, nao pode ter paredes acima & dir. ou acima & esq. ou abaixo & dir. ou abaixo & esq.
        delta_row = toState.row - self.currentState.row
        delta_col = toState.col - self.currentState.col

        ## o movimento eh na diagonal
        if (delta_row != 0 and delta_col != 0):
            if (self.currentState.row + delta_row, self.currentState.col) in self.walls and (
                    self.currentState.row, self.currentState.col + delta_col) in self.walls:
                return False

        return True

    def getNextPosition(self):
        """ Sorteia uma direcao e calcula a posicao futura do agente
         @return: tupla contendo a acao (direcao) e o estado futuro resultante da movimentacao """

        position = (self.currentState.row, self.currentState.col)

        mapCopy = copy.deepcopy(self.map)

        for i in range(position[0] - 1, position[0] + 2):
            for j in range(position[1] - 1, position[1] + 2):
                if i >= 0 and j >= 0 and i < self.maxRows and j < self.maxColumns:
                    if i == position[0] or j == position[1]:
                        if i != position[0] or j != position[1]: #Para não aumentar o valor da posição atual
                            mapCopy[i][j] += 1
                    else:
                        mapCopy[i][j] += 1.5

        betterPair = (position[0] - 1, position[1] - 1)
        for i in range(position[0] - 1, position[0] + 2):
            for j in range(position[1] - 1, position[1] + 2):
                if i >= 0 and j >= 0 and i < self.maxRows and j < self.maxColumns:
                    if (i != position[0] or j != position[1]) and mapCopy[i][j] < mapCopy[betterPair[0]][betterPair[1]]:
                        betterPair = (i, j)

        # print('\nPosição: ', position, mapCopy[position[0]][position[1]] , '\nMelhor: ', betterPair, mapCopy[betterPair[0]][betterPair[1]], '\n')

        self.map[betterPair[0]][betterPair[1]] = mapCopy[betterPair[0]][betterPair[1]]

        movePos = {"N": (-1, 0),
                   "S": (1, 0),
                   "L": (0, 1),
                   "O": (0, -1),
                   "NE": (-1, 1),
                   "NO": (-1, -1),
                   "SE": (1, 1),
                   "SO": (1, -1)}

        # for line in mapCopy:
        #     print(line)

        delta = (betterPair[0] - position[0], betterPair[1] - position[1])
        action = list(movePos.keys())[list(movePos.values()).index(delta)]
        return action, State(betterPair[0], betterPair[1])

    def chooseAction(self):
        """ Escolhe o proximo movimento de forma aleatoria. 
        Eh a acao que vai ser executada pelo agente. 
        @return: tupla contendo a acao (direcao) e uma instância da classe State que representa a posição esperada após a execução
        """

        ## Tenta encontrar um movimento possivel dentro do tabuleiro 
        result = self.getNextPosition()

        return result

    def do(self):
        """
        Método utilizado para o polimorfismo dos planos

        Retorna o movimento e o estado do plano (False = nao concluido, True = Concluido)
        """

        nextMove = self.move()
        return (nextMove[1], self.goalPos == State(nextMove[0][0], nextMove[0][1]))
