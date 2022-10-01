from maze import Maze
from state import State
from cardinal import *


class Problem:
    """Representação de um problema a ser resolvido por um algoritmo de busca clássica.
    A formulação do problema - instância desta classe - reside na 'mente' do agente.
    @param basePosition: State com as coordenadas da base (início do agente)
    @param goalState: State com as coordenadas do objetivo (Não utilizado)
    @param maxRows: Número de linhas no mapa
    @param maxColumns: Número de colunas no mapa
    @param mazeBeliefs: matriz de tamanho maxRows*maxColumns, percepções do agente sobre o labirinto
    # -1 são locais não explorado, 0 são locais explorados, -2 é parede, número maior que 0 é vítima (id da vítima)
    """
    def __init__(self, maxRows, maxColumns):
        self.basePosition = State(0,0) 
        self.goalState = State(0,0)
        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.mazeBeliefs = [[-1 for j in range(maxColumns)] for i in range(maxRows)]

    def defBasePosition(self, row, col):
        """Define o estado inicial.
        @param row: linha do estado inicial.
        @param col: coluna do estado inicial."""
        self.basePosition.row = row
        self.basePosition.col = col

    def setMaze(self, maze):
        self.mazeBeliefs = maze

    def updateMazePosition(self, coord, value):
        """Atualiza a posição do mapa com o valor passado
        @param coord: state com row e col do mapa que se quer atualizar
        @param value: valor que deseja-se colocar nessa posição do mapa"""
        self.mazeBeliefs[coord.row][coord.col] = value

    def defGoalState(self, row, col):
        """Define o estado objetivo.
        @param row: linha do estado objetivo.
        @param col: coluna do estado objetivo."""
        self.goalState.row = row
        self.goalState.col = col

    def getActionCost(self, action):
        """Retorna o custo da ação.
        @param action:
        @return custo da ação"""
        if (action=="nop"):
            return 0

        if (action=="checkVitalSignals"):
            return 2.0

        if (action == "N" or action == "L" or action == "O" or action == "S"):   
            return 1.0
        
        return 1.5

    def goalTest(self, currentState):
        """Testa se alcançou o estado objetivo.
        @param currentState: estado atual.
        @return True se o estado atual for igual ao estado objetivo."""
        if currentState == self.goalState:
            return True
        else:
            return False


