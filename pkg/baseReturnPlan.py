from random import randint
from state import State
import math
import copy

class BaseReturnPlan:
    def __init__(self, problem, startState, name="voltarBase"):
        """
        Plano para retornar para a base, implementado utilizando o algoritmo A*.
        @param problem: crenças do agente (contém o mapa criado durante a exploração)
        @param startState: coordenada de início do robô
        @param name: nome do plano
        """

        # Inicializa as variáveis do plano
        self.prob = problem
        self.name = name
        self.currentState = startState
        self.startCoordinate = startState
        self.goalPos = problem.basePosition

        self.initiate() # Inicializa as variáveis utilizadas para o cálculo do A*
        self.path = self.calculatePath() # Calcula o melhor caminho para retornar para a base
        self.totalCost = self.calculatePathCost() # Calcula o custo do caminho de volta para a base

    def initiate(self):
        """Inicializa as variáveis para poder rodar o algoritmo A*"""
        self.openSet = [(self.startCoordinate.row, self.startCoordinate.col)] #Com Min-Heap as operações são O(nlgn), dessa forma com array são O(n^2)
        self.cameFrom = dict() # Armazena de qual coordenada o robô chegou para chegar na outra
        self.gScore = dict() # g(n): custo para chegar ao nó n
        self.fScore = dict() # f(n): custo estimado para chegar do estado inicial até o objetivo passando por n
        for i in range(self.prob.maxRows): # No início do algoritmo o custo para chegar em qualquer nó é infinito, e para chegar no atual é 0
            for j in range(self.prob.maxColumns):
                self.gScore[(i,j)] = math.inf
                self.fScore[(i,j)] = self.gScore[(i,j)] + self.calculateHeuristic(State(i,j))
        self.gScore[(self.startCoordinate.row, self.startCoordinate.col)] = 0

    # Heurística utilizada: distância pitagórica entre os 2 pontos - admissível e consistente
    def calculateHeuristic(self, currentState):
        """Calcula a distância pitagórica entre a coordenada atual e o objetivo
        @param currentState: coordenada em que se encontra o robô"""
        if(self.goalPos and currentState):
            return math.sqrt(pow((self.goalPos.row - currentState.row), 2) + pow((self.goalPos.col - currentState.col), 2))

    def getLowestFScoreFromOpenSet(self):
        """Retorna o nó da fronteira que tem o menor valor da função f(n)""" # Com um min-heap era só retornar o topo
        lowest = self.openSet[0]
        for item in self.openSet:
            if self.fScore[item] < self.fScore[lowest]: lowest = item
        return lowest

    def reconstructPath(self, current):
        """ Cria o caminho do robô até a base. É um vetor ordenado por ordem de visita dos nós para sair do nó inicial até o final
        @param current: coordenada atual do robô"""
        total_path = [current]
        while current in self.cameFrom.keys():
            current = self.cameFrom[current]
            total_path.append(current)
        path_to_base = list(reversed(total_path))
        path_to_base.pop(0)
        return path_to_base

    def d(self, current, offset, neighbor):
        """ Custo para ir de um ponto até seu vizinho.
        Verifica se a posição para onde está tentando ir é uma parede ou um local desconhecido. Se for, é impossível ir até o vizinho (inf)
        Se for um local já explorado, se a ação não for de andar na diagonal, retorna o custo da ação.
        Se for uma ação para andar na diagonal, verifica se há uma parede ou um local não explorado no caminho que possam impossibilitar o movimento.
        Se tiver algo impossibilitando, retorna inf, senão, retorna o custo da ação
        @param current: nó atual
        @param offset: qual é a variação das coordenadas do nó atual para chegar até o vizinho
        @param neighbor: nó vizinho"""
        canMove = self.isPossibleToMove(neighbor)
        if not (canMove): # Se passou daqui, neighbor é um local sem parede e que foi explorado
            return math.inf

        if (offset[0] == 0 or offset[1] == 0): # Se não tiver parede no lugar e não estou indo na diagonal o custo é 1
            return 1

        # Se estou indo pra diagonal, não é possível mover se tiver alguma parede no caminho ou se eu não explorei o local e não sei se tem parede ou não
        canMove = self.isPossibleToMove((current[0] - offset[0], current[1])) and self.isPossibleToMove((current[0], current[1] - offset[1]))
        if not (canMove): # Se passou daqui, é porque eu conheço os locais na lateral e não tem nada impossibilitando o movimento
            return math.inf
        return 1.5

    def calculatePath(self):
        """ Calcula o caminho do ponto inicial até o objetivo. Retorna um array com os nós na ordem que devem 
        ser percorridos para chegar do ponto inicial até o final. Se não houver caminho, retorna um array vazio."""
        while(len(self.openSet) > 0): # Enquanto houverem nós na fronteira
            current = self.getLowestFScoreFromOpenSet() # Pega o nó da fronteira com menor f(n)

            if State(current[0], current[1]) == self.goalPos: # Verifica se é a posição objetivo. Se for, retorna o caminho até o objetivo
                return self.reconstructPath(current) 

            self.openSet.remove(current) # Remove o nó da fronteira

            rowOffset = [-1, -1, -1,  0, 0,  1, 1, 1] 
            colOffset = [-1,  0,  1, -1, 1, -1, 0, 1]

            for i in range(8): # Para cada vizinho do nó
                neighbor = (current[0] - rowOffset[i], current[1] - colOffset[i])
                if self.isCoordinateValid(neighbor): 
                    tentative_gScore = self.gScore[current] + self.d(current, (rowOffset[i], colOffset[i]), neighbor) 
                    if tentative_gScore < self.gScore[neighbor]: # Verifica se é possível melhorar o g(n) do vizinho
                        self.cameFrom[neighbor] = current # Atualiza o nó de origem para ir até o viziho
                        self.gScore[neighbor] = tentative_gScore # Atualiza g(n)
                        self.fScore[neighbor] = tentative_gScore + self.calculateHeuristic(State(neighbor[0], neighbor[1])) # Atualiza f(n)
                        if(neighbor not in self.openSet): # Adiciona o nó na fronteira se ele ainda não estiver nela
                            self.openSet.append(neighbor)
        return [] #Não há caminho    

    def calculatePathCost(self):
        """ Retorna o custo do caminho para ir até a base """
        if (len(self.path) > 0):
            cost = 1.5 if ((self.startCoordinate.row - self.path[0][0]) != 0 and (self.startCoordinate.col - self.path[0][1]) != 0) else 1 # Custo para ir da posição atual até a primeira do plano
            for i in range(len(self.path) - 1):
                if (self.path[i+1][0] - self.path[i][0]) == 0 or (self.path[i+1][1] - self.path[i][1]) == 0:
                    cost += 1
                else: 
                    cost += 1.5
            return cost
        return 0

    def updateCurrentState(self, state):
        self.currentState = state

    def getNextPosition(self):
        """ Desempilha o próximo movimento que é necessário fazer para voltar para a base. Se não há mais movimentos para realizar, retorna nop """
        if (len(self.path) > 0):
            move = self.path.pop(0)
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

    def chooseAction(self):
        """ Utilizado pelo agente para executar o plano """
        return self.getNextPosition()

    def getCost(self):
        """ Utilizado pelo agente para saber qual o custo do plano """
        return self.totalCost

    def isCoordinateValid(self, coord):
        """ Verifica se é uma coordenada dentro das fronteiras do mapa """
        return coord[0] >= 0 and coord[1] >= 0 and coord[0] < self.prob.maxRows and coord[1] < self.prob.maxColumns

    # Se for um local com parede o valor no mapa é -1, se for um local não explorado o valor é -2
    def isPossibleToMove(self, pos):
        """ Verifica se o agente pode se mover para a posição especificada. Para isso, verifica se há paredes nessa
        coordenada ou se ela é um local desconheido. Caso não seja um desses casos, é possível mover até a posição.
        @param pos: coordenada que se quer checar se é possível mover """
        return self.prob.mazeBeliefs[pos[0]][pos[1]] >= 0 and self.isCoordinateValid(pos)