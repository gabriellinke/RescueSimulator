from random import randint
from state import State
import math
import copy

class AStarPlan:
    def __init__(self, maxRows, maxColumns, initialState, victimsMap, terrainMap, ts, name="none", mesh="square"):
        """
        Define as variaveis necessárias para a utilização do A* por um agente
        """
        self.name = name
        #max-time

        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.initialState = initialState
        self.currentState = initialState
        self.victimsMap = copy.deepcopy(victimsMap)
        self.terrainMap = copy.deepcopy(terrainMap)

        self.victimsCoordinates = []
        for i in range(self.maxRows):
            for j in range(self.maxColumns):
                if self.victimsMap[i][j] != 0:
                    self.victimsCoordinates.append((i,j))

        self.totalCost = 0
        self.totaVictims = 0
        self.savePath = []
        self.returnPath = []

        self.startCoordinate = initialState
        self.endCoordinate = self.getVictim()

        while(len(self.victimsCoordinates) >= 0 and self.totalCost < ts):
            self.totalCost += 0.5 #0.5 pra carregar o pacote

            self.goalPos = self.endCoordinate
            self.setStart(self.startCoordinate)
            tempSavePath = self.calculatePath()
            # Tira nós redundantes
            tempSavePath.pop(0)
            cost = self.calculatePathCost(tempSavePath)
            self.totalCost += cost
            # print('Path: ', tempSavePath, ' Cost: ', cost, ' Total cost: ', self.totalCost)

            self.totalCost += 0.5 #0.5 pra deixar o pacote com a vítima

            self.goalPos = self.initialState
            self.setStart(self.endCoordinate)
            tempReturnPath = self.calculatePath()
            cost = self.calculatePathCost(tempReturnPath)
            self.totalCost += cost
            # print('Path: ', tempReturnPath, ' Cost: ', cost, ' Total cost: ', self.totalCost)

            # Total cost < ts? Calcula para nova vítima
            if self.totalCost < ts:
                self.savePath.extend(tempSavePath.copy())
                self.returnPath = tempReturnPath.copy()
                # print('Save Path: ', self.savePath, ' Return Path: ', self.returnPath, '\n')

                # Pega nova vítima
                self.startCoordinate = self.endCoordinate
                self.endCoordinate = self.getVictim()

                if not (self.endCoordinate):
                    break

        # Tira nós redundantes
        self.returnPath.pop(0)


    def getVictim(self):
        if(len(self.victimsCoordinates) >= 1):
            rand = randint(0, len(self.victimsCoordinates)-1)
            victim = self.victimsCoordinates.pop(rand)
            self.totaVictims += 1
            return State(victim[0], victim[1])

    # Inicializa as variáveis para poder rodar o algoritmo
    def setStart(self, startState):
        self.openSet = [(startState.row, startState.col)] #Com Min-Heap as operações são O(nlgn), dessa forma são O(n^2)
        self.cameFrom = dict()
        self.gScore = dict()
        self.fScore = dict()
        for i in range(self.maxRows):
            for j in range(self.maxColumns):
                self.gScore[(i,j)] = math.inf
                self.fScore[(i,j)] = self.gScore[(i,j)] + self.calculateHeuristic(State(i,j))
        self.gScore[(startState.row, startState.col)] = 0

    # Heurística utilizada: distância pitagórica entre os 2 pontos
    def calculateHeuristic(self, currentState):
        if(self.goalPos and currentState):
            return math.sqrt(pow((self.goalPos.row - currentState.row), 2) + pow((self.goalPos.col - currentState.col), 2))

    def getLowestFScoreFromOpenSet(self):
        lowest = self.openSet[0]
        for item in self.openSet:
            if self.fScore[item] < self.fScore[lowest]: lowest = item
        return lowest

    # Cria um vetor ordenado por ordem de visita dos nós para sair do nó inicial para o final
    def reconstructPath(self, current):
        total_path = [current]
        while current in self.cameFrom.keys():
            current = self.cameFrom[current]
            total_path.append(current)
        return list(reversed(total_path))

    # Custo de um ponto para ir até seu vizinho
    def d(self, current, offset, neighbor):
        wall = self.terrainMap[neighbor[0]][neighbor[1]]
        if(wall >= math.inf): 
            return math.inf
        return 1 if (offset[0] == 0 or offset[1] == 0) else 1.5

    # Calcula o caminho do ponto inicial até o objetivo. Retorna um array com os 
    # nós na ordem que devem ser percorridos para chegar do ponto inicial até o final. 
    # Se não houver caminho, retorna um array vazio.
    def calculatePath(self):
        while(len(self.openSet) > 0):
            current = self.getLowestFScoreFromOpenSet()

            if State(current[0], current[1]) == self.goalPos:
                return self.reconstructPath(current) 

            self.openSet.remove(current)

            rowOffset = [-1, -1, -1, 0, 0, 1, 1, 1]
            colOffset = [-1, 0, 1, -1, 1, -1, 0, 1]

            for i in range(8): # Para cada vizinho
                neighbor = (current[0] - rowOffset[i], current[1] - colOffset[i])
                if neighbor[0] >= 0 and neighbor[1] >= 0 and neighbor[0] < self.maxRows and neighbor[1] < self.maxColumns:
                    tentative_gScore = self.gScore[current] + self.d(current, (rowOffset[i], colOffset[i]), neighbor)
                    if tentative_gScore < self.gScore[neighbor]:
                        self.cameFrom[neighbor] = current
                        self.gScore[neighbor] = tentative_gScore
                        self.fScore[neighbor] = tentative_gScore + self.calculateHeuristic(State(neighbor[0], neighbor[1]))
                        if(neighbor not in self.openSet):
                            self.openSet.append(neighbor)
        return [] #Não há caminho    

    def calculatePathCost(self, path):
        cost = 0
        for i in range(len(path) - 1):
            if (path[i+1][0] - path[i][0]) == 0 or (path[i+1][1] - path[i][1]) == 0:
                cost += 1
            else: 
                cost += 1.5
        return cost

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

        if(len(self.savePath) > 0):
            move = self.savePath.pop(0)
        elif (len(self.returnPath) > 0):
            move = self.returnPath.pop(0)
        else:
            return "nop", self.currentState

        position = (self.currentState.row, self.currentState.col)

        movePos = {"N": (-1, 0),
                   "S": (1, 0),
                   "L": (0, 1),
                   "O": (0, -1),
                   "NE": (-1, 1),
                   "NO": (-1, -1),
                   "SE": (1, 1),
                   "SO": (1, -1)}

        delta = (move[0] - position[0], move[1] - position[1])
        action = list(movePos.keys())[list(movePos.values()).index(delta)]
        return action, State(move[0], move[1])

    def takePackages(self):
        return self.totaVictims

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
