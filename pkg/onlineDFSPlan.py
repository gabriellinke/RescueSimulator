from random import randint
from state import State


class OnlineDFSPlan:
    def __init__(self, maxRows, maxColumns, goal, initialState, name="none", mesh="square"):
        """
        Define as variaveis necessárias para a utilização do Online DFS por um agente
        """
        self.walls = []
        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.initialState = initialState
        self.currentState = initialState
        self.goalPos = goal
        self.actions = []

        self.untried = dict()  # key = estado s (x,y) -> mostra um array de ações ainda não tentadas no estado
        self.unbacktracked = dict()  # key = estado s (x,y) -> mostra uma fila de estados que levaram ao estado s
        for i in range(maxRows):
            for j in range(maxColumns):
                self.untried[(i, j)] = ["S", "L", "SE", "O", "NE", "NO", "N", "SO"]
                # self.untried[(i, j)] = ["SE", "S", "L", "NE", "SO", "N", "NO", "O"]
                self.unbacktracked[(i, j)] = []

        self.result = {}  # key = estado s (x,y) e ação ("NO", "NE", ...) -> mostra o estado resultado s' após executar ação a partir de s

    def setWalls(self, walls):
        row = 0
        col = 0
        for i in walls:
            col = 0
            for j in i:
                if j == 1:
                    self.walls.append((row, col))
                col += 1
            row += 1

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
        possibilities = self.untried[position]
        movePos = {"N": (-1, 0),
                   "S": (1, 0),
                   "L": (0, 1),
                   "O": (0, -1),
                   "NE": (-1, 1),
                   "NO": (-1, -1),
                   "SE": (1, 1),
                   "SO": (1, -1)}

        if len(possibilities) > 0:
            # rand = randint(0, len(possibilities)-1)
            rand = 0
            movDirection = possibilities[rand]

            possibilities.pop(rand)
            self.untried[position] = possibilities

            state = State(self.currentState.row + movePos[movDirection][0],
                          self.currentState.col + movePos[movDirection][1])
        else:
            if len(self.unbacktracked[position]) > 0:
                backtrackState = self.unbacktracked[position].pop(0)
                state = State(backtrackState[0], backtrackState[1])
                direction = (backtrackState[0] - position[0], backtrackState[1] - position[1])
                movDirection = list(movePos.keys())[list(movePos.values()).index(direction)]
            else:
                state = self.currentState
                movDirection = 'nop'
        return movDirection, state


    def chooseAction(self):
        """ Escolhe o proximo movimento de forma aleatoria. 
        Eh a acao que vai ser executada pelo agente. 
        @return: tupla contendo a acao (direcao) e uma instância da classe State que representa a posição esperada após a execução
        """

        ## Tenta encontrar um movimento possivel dentro do tabuleiro 
        result = self.getNextPosition()
        print('result: ', result[0], result[1]) #'L' , '01'
        currentPos = (self.currentState.row, self.currentState.col)# '0','0'
        nextPos = (result[1].row, result[1].col)# '0','1'

        if self.isPossibleToMove(result[1]) and result[0] != 'nop': #dá pra ir para '0','1'?
            if (currentPos, result[0]) not in self.result.keys():# se '00', 'L' não está nos results
                self.result[(currentPos, result[0])] = nextPos# O resultado de '00', 'L' é '01'
                # print('result ', self.result)

                self.unbacktracked[nextPos].append(currentPos) #de '01' dá para voltar para '00'
                print('unbacktracked ', self.unbacktracked)
        # else:


        return result

    def do(self):
        """
        Método utilizado para o polimorfismo dos planos

        Retorna o movimento e o estado do plano (False = nao concluido, True = Concluido)
        """

        nextMove = self.move()
        return (nextMove[1], self.goalPos == State(nextMove[0][0], nextMove[0][1]))
