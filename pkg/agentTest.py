## AGENTE RANDOM
### @Author: Luan Klein e Tacla (UTFPR)
### Agente que fixa um objetivo aleatório e anda aleatoriamente pelo labirinto até encontrá-lo.
### Executa raciocíni on-line: percebe --> [delibera] --> executa ação --> percebe --> ...
import sys
import os

## Importa Classes necessarias para o funcionamento
from model import Model
from problem import Problem
from state import State
from random import randint
from maze import Maze

## Importa o algoritmo para o plano
from testPlan import TestPlan
from onlineDFSPlan import OnlineDFSPlan

##Importa o Planner
sys.path.append(os.path.join("pkg", "planner"))
from planner import Planner
## Classe que define o Agente
class AgentTest:
    def __init__(self, model, configDict):
        """ 
        Construtor do agente random
        @param model referencia o ambiente onde o agente estah situado
        """
       
        self.model = model

        ## Obtem o tempo que tem para executar
        self.tl = configDict["Tl"]
        print("Tempo disponivel: ", self.tl)
        
        ## Pega o tipo de mesh, que está no model (influência na movimentação)
        self.mesh = self.model.mesh

        ## Cria a instância do problema na mente do agente (sao suas crencas)
        self.prob = Problem()
        self.prob.createMaze(model.rows, model.columns, Maze(model.rows, model.columns))
    
        # O agente le sua posica no ambiente por meio do sensor
        initial = self.positionSensor()
        self.prob.defInitialState(initial.row, initial.col)
        print("*** Estado inicial do agente: ", self.prob.initialState)
        
        # Define o estado atual do agente = estado inicial
        self.currentState = self.prob.initialState

        # Define o estado objetivo:        
        # definimos um estado objetivo aleatorio
        # self.prob.defGoalState(randint(0,model.rows-1), randint(0,model.columns-1))
        
        # definimos um estado objetivo que veio do arquivo ambiente.txt
        self.prob.defGoalState(model.maze.board.posGoal[0],model.maze.board.posGoal[1])
        print("*** Objetivo do agente: ", self.prob.goalState)
        print("*** Total de vitimas existentes no ambiente: ", self.model.getNumberOfVictims())


        """
        DEFINE OS PLANOS DE EXECUÇÃO DO AGENTE
        """
        
        ## Custo da solução
        self.costAll = 0

        ## Cria a instancia do plano para se movimentar aleatoriamente no labirinto (sem nenhuma acao) 
        self.plan = OnlineDFSPlan(model.rows, model.columns, self.prob.goalState, initial, "goal", self.mesh)

        ## adicionar crencas sobre o estado do ambiente ao plano - neste exemplo, o agente faz uma copia do que existe no ambiente.
        ## Em situacoes de exploracao, o agente deve aprender em tempo de execucao onde estao as paredes

        # Quando tento executar uma ação e ela dá erro, adiciono a posição que deu erro no mapa de paredes
        self.plan.setWalls(self.model.maze.walls)

        ## Adiciona o(s) planos a biblioteca de planos do agente
        self.libPlan=[self.plan]

        ## inicializa acao do ciclo anterior com o estado esperado
        self.previousAction = "nop"    ## nenhuma (no operation)
        self.expectedState = self.currentState

    ## Metodo que define a deliberacao do agente 
    def deliberate(self):
        ## Verifica se há algum plano a ser executado
        if len(self.libPlan) == 0:
            return -1   ## fim da execucao do agente, acabaram os planos
        
        self.plan = self.libPlan[0]

        print("\n*** Inicio do ciclo raciocinio ***")
        print("Pos agente no amb.: ", self.positionSensor())

        ## Redefine o estado atual do agente de acordo com o resultado da execução da ação do ciclo anterior
        self.currentState = self.positionSensor()
        self.plan.updateCurrentState(self.currentState) # atualiza o current state no plano
        print("Ag cre que esta em: ", self.currentState)

        ## Verifica se a execução do acao do ciclo anterior funcionou ou nao
        if not (self.currentState == self.expectedState):
            print("---> erro na execucao da acao ", self.previousAction, ": esperava estar em ", self.expectedState, ", mas estou em ", self.currentState)

        ## Funcionou ou nao, vou somar o custo da acao com o total 
        self.costAll += self.prob.getActionCost(self.previousAction)
        print ("Custo até o momento (com a ação escolhida):", self.costAll) 

        ## consome o tempo gasto
        self.tl -= self.prob.getActionCost(self.previousAction)
        print("Tempo disponivel: ", self.tl)

        if(self.tl <= 0):
            print("O tempo acabou!")
            del self.libPlan[0]  ## retira plano da biblioteca
            print(self.prob.mazeBelief.walls)
            print(self.prob.mazeBelief.victims)
            print(self.prob.mazeBelief.vitalSignals)
            print(self.prob.mazeBelief.diffAccess)

        ## Verifica se atingiu o estado objetivo
        ## Poderia ser outra condição, como atingiu o custo máximo de operação
        if self.prob.goalTest(self.currentState):
            print("!!! Objetivo atingido !!!")
            del self.libPlan[0]  ## retira plano da biblioteca
        
        ## Verifica se tem vitima na posicao atual    
        victimId = self.victimPresenceSensor()
        if victimId > 0:
            print ("vitima encontrada em ", self.currentState, " id: ", victimId, " sinais vitais: ", self.victimVitalSignalsSensor(victimId))
            print ("vitima encontrada em ", self.currentState, " id: ", victimId, " dif de acesso: ", self.victimDiffOfAcessSensor(victimId))
            if(self.prob.mazeBelief.victims[self.currentState.row][self.currentState.col] == 0):
                self.prob.mazeBelief.victims[self.currentState.row][self.currentState.col] = victimId
                self.prob.mazeBelief.vitalSignals.append(self.victimVitalSignalsSensor(victimId))
                self.prob.mazeBelief.diffAccess.append(self.victimDiffOfAcessSensor(victimId))

        ## Define a proxima acao a ser executada
        ## currentAction eh uma tupla na forma: <direcao>, <state>
        result = self.plan.chooseAction()
        print("Ag deliberou pela acao: ", result[0], " o estado resultado esperado é: ", result[1])

        ## Executa esse acao, atraves do metodo executeGo 
        self.executeGo(result[0])
        self.previousAction = result[0]
        self.expectedState = result[1]       

        return 1

    ## Metodo que executa as acoes
    def executeGo(self, action):
        """Atuador: solicita ao agente físico para executar a acao.
        @param direction: Direcao da acao do agente {"N", "S", ...}
        @return 1 caso movimentacao tenha sido executada corretamente """

        ## Passa a acao para o modelo
        result = self.model.go(action)
        # Se a ação foi executada ela foi completada com sucesso e posso fazer algo com isso
        if result:
            print('Execução funcionou: ', result, action)

        # Se a ação não foi executada e a Action solicitada tiver sido N, S, L, O há uma parede na direção da action
        # Se a ação não foi executada e a Action solicitada tiver sido NO, NE, SO, SE
        # Podem haver paredes nas laterais ou na diagonal - Acredito que não consigo saber onde fica a parede
        else:
            print('Execução não funcionou: ', result, action)

            # Encontro qual seria a posição que eu estaria caso a ação desse certo. 
            # Se for uma posição válida no mapa, quer dizer que tem parede

            movePos = {"N": (-1, 0),
                    "S": (1, 0),
                    "L": (0, 1),
                    "O": (0, -1),
                    "NE": (-1, 1),
                    "NO": (-1, -1),
                    "SE": (1, 1),
                    "SO": (1, -1),
                    "nop": (0, 0)}

            position = State(self.currentState.row + movePos[action][0], self.currentState.col + movePos[action][1])

            # Adiciona parede no mapa do robô - Se o erro foi tentando ir pra diagonal não adiciono parede
            if action != 'NO' and action != 'NE' and action != 'SO' and action != 'SE':
                if position.row > 0 and position.col > 0 and position.row < self.prob.mazeBelief.maxRows and position.col < self.prob.mazeBelief.maxColumns:
                    self.prob.mazeBelief.walls[position.row][position.col] = 1


    ## Metodo que pega a posicao real do agente no ambiente
    def positionSensor(self):
        """Simula um sensor que realiza a leitura do posição atual no ambiente.
        @return instancia da classe Estado que representa a posição atual do agente no labirinto."""
        pos = self.model.agentPos
        return State(pos[0],pos[1])

    def victimPresenceSensor(self):
        """Simula um sensor que realiza a deteccao de presenca de vitima na posicao onde o agente se encontra no ambiente
           @return retorna o id da vítima"""     
        return self.model.isThereVictim()

    def victimVitalSignalsSensor(self, victimId):
        """Simula um sensor que realiza a leitura dos sinais da vitima 
        @param o id da vítima
        @return a lista de sinais vitais (ou uma lista vazia se não tem vítima com o id)"""     
        return self.model.getVictimVitalSignals(victimId)

    def victimDiffOfAcessSensor(self, victimId):
        """Simula um sensor que realiza a leitura dos dados relativos à dificuldade de acesso a vítima
        @param o id da vítima
        @return a lista dos dados de dificuldade (ou uma lista vazia se não tem vítima com o id)"""     
        return self.model.getDifficultyOfAcess(victimId)
    
    ## Metodo que atualiza a biblioteca de planos, de acordo com o estado atual do agente
    def updateLibPlan(self):
        for i in self.libPlan:
            i.updateCurrentState(self.currentState)

    def actionDo(self, posAction, action = True):
        self.model.do(posAction, action)
