from state import State
import math
import random


class GeneticPlan:
    def __init__(self, problem, startState, time, name="caminhoGenetico"):
        """
        Plano para escolher um caminho que tenta passar pelo máximo de vítimas possível,
        priorizando as de maior gravidade. Calcula inicialmente todas as distâncias entre
        as posições das vítimas, utilizando o algoritmo A*.
        @param problem: crenças do agente (contém o mapa criado durante a exploração)
        @param startState: coordenada de início do robô
        @param time: tempo que o plano tem para ser executado
        @param name: nome do plano
        """

        # Inicializa as variáveis do plano
        self.prob = problem
        self.name = name
        self.currentState = startState
        self.startCoordinate = startState
        self.time = time

        # 
        self.victimsPositions = []
        for i in range(self.prob.maxRows):
            for j in range(self.prob.maxColumns):
                if(self.prob.mazeBeliefs[i][j] > 0): self.victimsPositions.append((i, j))
        
        self.savedVictims = []
        self.savedVictimsIds = []
        self.possibleSubPaths = dict()

        basePos = (startState.row, startState.col)
        self.possibleSubPaths[basePos] = dict()
        self.possibleSubPaths[basePos][basePos] = ([], 0)
        for pos in self.victimsPositions:
            path_to_base = self.a_star(pos, basePos)
            path_from_base = list(reversed(path_to_base))
            path_from_base.pop(0)
            path_from_base.append(pos)

            # print("a", end="")
            self.possibleSubPaths[basePos][pos] = (path_from_base, self.calculatePathCost(basePos, path_from_base))

            self.possibleSubPaths[pos] = dict()
            self.possibleSubPaths[pos][basePos] = (path_to_base, self.calculatePathCost(pos, path_to_base))
            for other in self.victimsPositions:
                if (pos == other):
                    continue
                path = self.a_star(pos, other)
                self.possibleSubPaths[pos][other] = (path, self.calculatePathCost(pos, path))

        # self.orderedVictimsVitalSignals = []
        self.orderedVictimsGravity = []
        for v in self.victimsPositions:
            victim_id = self.prob.mazeBeliefs[v[0]][v[1]]
            vital_signals = next(filter(lambda x: x[0] == victim_id, self.prob.victimsVitalSignals), False)
            gravity = math.floor((100 - vital_signals[6]) / 25) + 1
            # self.orderedVictimsVitalSignals.append(vital_signals)
            self.orderedVictimsGravity.append(gravity)

        # vetor com as próximas posições a serem visitadas;
        # calculado no início, quando o algoritmo genético é executado
        self.path = []
        self.expectedCost = 0

        # variáveis do algoritmo genético:

        # tamanho da população (é também o tamanho da descendência)
        self.popSize = 5000

        # número máximo de gerações
        self.maxGens = 150

        # probabilidades de crossover e mutação
        self.pCross = 0.8
        self.pMut = 0.005

        # executa do algoritmo genético para encontrar o caminho a seguir
        self.algoritmoGenetico()

    def a_star(self, start, end):
        openSet = [start]
        cameFrom = dict()
        gScore = dict()
        fScore = dict()
        for i in range(self.prob.maxRows): # No início do algoritmo o custo para chegar em qualquer nó é infinito, e para chegar no atual é 0
            for j in range(self.prob.maxColumns):
                gScore[(i,j)] = math.inf
                fScore[(i,j)] = math.inf
        gScore[start] = 0
        fScore[start] = 0

        while(len(openSet) > 0): # Enquanto houverem nós na fronteira
            current = self.getLowestFScoreFromOpenSet(openSet, fScore) # Pega o nó da fronteira com menor f(n)

            if current == end: # Verifica se é a posição objetivo. Se for, retorna o caminho até o objetivo
                return self.reconstructPath(current, cameFrom)

            openSet.remove(current) # Remove o nó da fronteira

            rowOffset = [-1, -1, -1,  0, 0,  1, 1, 1]
            colOffset = [-1,  0,  1, -1, 1, -1, 0, 1]

            for i in range(8): # Para cada vizinho do nó
                neighbor = (current[0] - rowOffset[i], current[1] - colOffset[i])
                if self.isCoordinateValid(neighbor): 
                    tentative_gScore = gScore[current] + self.d(current, (rowOffset[i], colOffset[i]), neighbor) 
                    if tentative_gScore < gScore[neighbor]: # Verifica se é possível melhorar o g(n) do vizinho
                        cameFrom[neighbor] = current # Atualiza o nó de origem para ir até o viziho
                        gScore[neighbor] = tentative_gScore # Atualiza g(n)
                        fScore[neighbor] = tentative_gScore + self.calculateHeuristic(neighbor, end) # Atualiza f(n)
                        if(neighbor not in openSet): # Adiciona o nó na fronteira se ele ainda não estiver nela
                            openSet.append(neighbor)
        return [] #Não há caminho    

    def getLowestFScoreFromOpenSet(self, openSet, fScore):
        """Retorna o nó da fronteira que tem o menor valor da função f(n)""" # Com um min-heap era só retornar o topo
        lowest = openSet[0]
        for item in openSet:
            if fScore[item] < fScore[lowest]: lowest = item
        return lowest

    def reconstructPath(self, end, cameFrom):
        """ Cria o caminho do robô a partir da informação de origem encontrada de cada posição,
        começando do final.
        O retorno é um vetor ordenado por ordem de visita dos nós para sair do nó inicial até o final
        @param end: coordenada final do caminho"""
        reversed_path = [end]
        current = end
        while current in cameFrom.keys():
            current = cameFrom[current]
            reversed_path.append(current)
        path = list(reversed(reversed_path))
        path.pop(0)
        return path

    def isCoordinateValid(self, coord):
        """ Verifica se é uma coordenada dentro das fronteiras do mapa """
        return coord[0] >= 0 and coord[1] >= 0 and coord[0] < self.prob.maxRows and coord[1] < self.prob.maxColumns

    # Se for um local com parede o valor no mapa é -1, se for um local não explorado o valor é -2
    def isPossibleToMove(self, pos):
        """ Verifica se o agente pode se mover para a posição especificada. Para isso, verifica se há paredes nessa
        coordenada ou se ela é um local desconheido. Caso não seja um desses casos, é possível mover até a posição.
        @param pos: coordenada que se quer checar se é possível mover """
        return self.prob.mazeBeliefs[pos[0]][pos[1]] >= 0 and self.isCoordinateValid(pos)

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

    # Heurística utilizada: distância pitagórica entre os 2 pontos - admissível e consistente
    def calculateHeuristic(self, currentState, end):
        """Calcula a distância pitagórica entre a coordenada atual e o objetivo
        @param currentState: coordenada em que se encontra o robô"""
        if end and currentState:
            return math.sqrt(pow((end[0] - currentState[0]), 2) + pow((end[1] - currentState[1]), 2))

    def calculatePathCost(self, start, path):
        """ Retorna o custo do caminho calculado """
        if (len(path) > 0):
            cost = 1.5 if ((start[0] - path[0][0]) != 0 and (start[1] - path[0][1]) != 0) else 1 # Custo para ir da posição atual até a primeira do plano
            for i in range(len(path) - 1):
                if (path[i+1][0] - path[i][0]) == 0 or (path[i+1][1] - path[i][1]) == 0:
                    cost += 1
                else: 
                    cost += 1.5
            return cost
        return 0
    
    def updateCurrentState(self, state, time):
        self.currentState = state
        self.time = time
        pos = (state.row, state.col)
        if pos in self.victimsPositions and pos not in self.savedVictims:
            self.savedVictims.append(pos)
            self.savedVictimsIds.append(self.prob.mazeBeliefs[pos[0]][pos[1]])

    def getNextPosition(self):
        """ Desempilha o próximo movimento previsto. Se não há mais movimentos
        para realizar, retorna nop """
        if len(self.path) == 0:
            return "nop", self.currentState

        move = self.path.pop(0)

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
    
    def printMetrics(self, totalCost, victimsVitalSignals, numVictims):
        vs = len(self.savedVictims)
        V = numVictims
        print("Número de vítimas salvas: ", vs)
        print("Número de vítimas encontradas: ", len(self.victimsPositions))
        print("Tempo total gasto pelo agente: ", totalCost)
        print("pvs: ", vs / V)
        if not (vs):
            print("tvs: ", math.inf)
        else:
            print("tvs: ", totalCost / vs)
        vsg = 0
        Vi = [0, 0, 0, 0]
        for v in victimsVitalSignals:
            i = math.floor((100 - v[6]) / 25) + 1
            Vi[i-1] += i
            if v[0] in self.savedVictimsIds:
                vsg += i
        vsg = vsg / sum(Vi)
        print("vsg: ", vsg)
        pass

    def fitness(self, cromossomo):
        basePos = (self.startCoordinate.row, self.startCoordinate.col)
        atual = basePos
        acc_cost = 0
        # num_saved = len(cromossomo)
        gravity_saved = 0
        for proximo_idx in cromossomo:
            proximo = self.victimsPositions[proximo_idx]

            subpath, cost = self.possibleSubPaths[atual][proximo]
            ret_path, ret_cost = self.possibleSubPaths[proximo][basePos]
            if acc_cost + cost + ret_cost > self.time:
                # num_saved = proximo_idx + 1
                # não dá tempo de terminar o caminho proposto pelo cromossomo;
                # nesse caso, ele faria só até o anterior e depois voltaria
                break

            gravity = self.orderedVictimsGravity[proximo_idx]
            gravity_saved += gravity

            acc_cost += cost
            atual = proximo
            pass
        pass
        acc_cost += self.possibleSubPaths[atual][basePos][1]
        return gravity_saved + 1/acc_cost
        # return gravity_saved

    def crossover(self, pai1, pai2):
        sz = len(pai1)
        i = random.randrange(sz)
        j = random.randrange(i+1, sz+1)
        d1 = pai1.copy()
        d2 = pai2.copy()
        set1 = set()
        set2 = set()
        if j <= sz and i < (j-1):
            for k in range(i, j):
                d1[k] = pai2[k]
                set1.add(d1[k])

                d2[k] = pai1[k]
                set2.add(d2[k])
            for k in range(i, j):
                if pai1[k] not in set1:
                    index = k
                    while index in range(i, j):
                        val = pai2[index]
                        index = pai1.index(val)
                    d1[index] = pai1[k]
                    
                if pai2[k] not in set2:
                    index = k
                    while index in range(i, j):
                        val = pai1[index]
                        index = pai2.index(val)
                    d2[index] = pai2[k]

        return d1, d2
    
    def mutate(self, cromossomo, indice):
        outro = random.randrange(len(cromossomo))
        while outro == indice:
            outro = random.randrange(len(cromossomo))
        temp = cromossomo[indice]
        cromossomo[indice] = cromossomo[outro]
        cromossomo[outro] = temp

    def algoritmoGenetico(self):
        populacao_inicial = [random.sample(range(len(self.victimsPositions)), k=len(self.victimsPositions)) for i in range(self.popSize)]
        populacao = [(c, self.fitness(c)) for c in populacao_inicial]

        geracoes = 0
        while geracoes < self.maxGens:
            geracoes += 1
            # um método da biblioteca padrão para fazer o método da roleta
            descendentes = random.choices([c for c, f in populacao], [f for c, f in populacao], k=len(populacao))

            # um método manual de calcular os descendentes
            # descendentes = []
            # fitness_sum = sum([tup[1] for tup in populacao])
            # for i in range(self.popSize):
            #     soma = 0
            #     sorteado = random.random()
                
            #     for c, f in populacao:
            #         soma += f/fitness_sum
            #         if soma >= sorteado:
            #             descendentes.append(c)
            #             break
            #     else:
            #         descendentes.append(populacao[-1])
            # assim foram sorteados com o método da roleta os descendentes
            
            for i in range(1, len(descendentes), 2):
                sorteado = random.random()
                if sorteado <= self.pCross:
                    d1, d2 = self.crossover(descendentes[i-1], descendentes[i])
                    descendentes[i-1] = d1
                    descendentes[i] = d2
            
            for i in range(len(descendentes)):
                for j in range(len(descendentes[i])):
                    sorteado = random.random()
                    if sorteado <= self.pMut:
                        self.mutate(descendentes[i], j)
                pass

            populacao.extend([(c, self.fitness(c)) for c in descendentes])

            if self.maxGens - geracoes < 4 or geracoes < 4:
                melhor, melhor_fitness = max(populacao, key=lambda tup: tup[1])
                print(melhor_fitness, end="; ")
            # seleciona os N com maior fitness
            populacao.sort(key=lambda tup: tup[1])
            del populacao[:self.popSize]
            if self.maxGens - geracoes < 4 or geracoes < 4:
                melhor, melhor_fitness = max(populacao, key=lambda tup: tup[1])
                print(melhor_fitness)

        melhor, melhor_fitness = max(populacao, key=lambda tup: tup[1])

        # cria caminho com o melhor
        basePos = (self.startCoordinate.row, self.startCoordinate.col)
        atual = basePos
        acc_cost = 0
        for proximo_idx in melhor:
            proximo = self.victimsPositions[proximo_idx]

            subpath, cost = self.possibleSubPaths[atual][proximo]
            ret_path, ret_cost = self.possibleSubPaths[proximo][basePos]
            if acc_cost + cost + ret_cost > self.time:
                break
            
            acc_cost += cost
            atual = proximo
            self.path.extend(subpath)
            pass
        ret_path, ret_cost = self.possibleSubPaths[atual][basePos]
        self.path.extend(ret_path)
        acc_cost += ret_cost
        self.expectedCost = acc_cost

        # print(self.path)
        pass
