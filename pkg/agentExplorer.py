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

## Importa o algoritmo para o plano
from randomPlan import RandomPlan
from baseReturnPlan import BaseReturnPlan

##Importa o Planner
sys.path.append(os.path.join("pkg", "planner"))
from planner import Planner

## Classe que define o Agente
class AgentExplorer:
    def __init__(self, model, configDict):
        """ 
        Construtor do agente explorador
        @param model referencia o ambiente onde o agente estah situado
        """

        self.model = model

        ## Obtem o tempo que tem para executar
        self.time = configDict["Te"]
        print("Tempo disponivel: ", self.time)
        
        ## Pega o tipo de mesh, que está no model (influência na movimentação)
        self.mesh = self.model.mesh

        ## Cria a instância do problema na mente do agente (sao suas crencas)
        self.prob = Problem(model.rows, model.columns)
    
        # O agente le sua posica no ambiente por meio do sensor
        initial = self.positionSensor()
        self.prob.defBasePosition(initial.row, initial.col)
        # Define o estado atual do agente = estado inicial
        self.currentState = self.prob.basePosition
        print("*** Estado inicial do agente: ", self.prob.basePosition)
        print("*** Total de vitimas existentes no ambiente: ", self.model.getNumberOfVictims())

        """
        DEFINE OS PLANOS DE EXECUÇÃO DO AGENTE
        """
        
        ## Custo da solução
        self.costAll = 0

        ## Cria a instancia do plano para se movimentar aleatoriamente no labirinto (sem nenhuma acao) 
        self.plan = RandomPlan(model.rows, model.columns, self.prob.goalState, initial, "explorar", self.mesh)

        ## Adiciona o(s) planos a biblioteca de planos do agente
        self.libPlan=[self.plan]

        ## inicializa acao do ciclo anterior com o estado esperado
        self.previousAction = "nop"    ## nenhuma (no operation)
        self.expectedState = self.currentState

    ## Metodo que define a deliberacao do agente 
    def deliberate(self):

        # Verifica se pode continuar deliberando
        if not (self.canKeepExecuting()): 
            return -1

        if (self.plan.name != "voltarBase"):
            self.checkShouldReturnToBase()

        # Atualiza o plano que irá executar
        self.plan = self.libPlan[0]

        # Inicia o raciocínio do agente
        print("\n*** Inicio do ciclo raciocinio ***")
        print("Pos agente no amb.: ", self.positionSensor())

        # Redefine o estado atual do agente de acordo com o resultado da execução da ação do ciclo anterior
        self.updateCurrentState()

        # Verifica se a execução da ação do ciclo anterior funcionou ou não
        self.checkPreviousExecution()

        # Funcionou ou nao, vou somar o custo da acao com o total 
        self.costAll += self.prob.getActionCost(self.previousAction)
        print ("Custo até o momento (com a ação escolhida):", self.costAll) 

        # consome o tempo gasto
        self.time -= self.prob.getActionCost(self.previousAction)
        print("Tempo disponivel: ", self.time)
        
        # Verifica se tem alguma vítima na posição atual do robô
        self.checkForVictim()

        # Define a proxima acao a ser executada e executa-a
        self.executeNextAction()

        return 1

    ## Metodo que executa as acoes
    def executeGo(self, action):
        """Atuador: solicita ao agente físico para executar a acao.
        @param direction: Direcao da acao do agente {"N", "S", ...}
        @return 1 caso movimentacao tenha sido executada corretamente """

        ## Passa a acao para o modelo
        result = self.model.go(action)
        
        ## Se o resultado for True, significa que a acao foi completada com sucesso, e ja pode ser removida do plano
        ## if (result[1]): ## atingiu objetivo ## TACLA 20220311
        ##    del self.plan[0]
        ##    self.actionDo((2,1), True)
            

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
    
    ## Metodo que atualiza a biblioteca de planos, de acordo com o estado atual do agente
    def updateLibPlan(self):
        for i in self.libPlan:
            i.updateCurrentState(self.currentState)

    def actionDo(self, posAction, action = True):
        self.model.do(posAction, action)

    """Verifica se há uma vítima na posição atual do robô
    Se tiver, faz a leitura dos sinais vitais, consome o tempo da leitura e
    adiciona a vítima no mapa do robô
    """
    def checkForVictim(self):
        ## Verifica se tem vitima na posicao atual    
        victimId = self.victimPresenceSensor()
        if victimId > 0 and not self.prob.isVictimInPosition(self.currentState): #Se encontrei vítima e ela ainda não está no mapa: tenho que adicionar a posição da vítima no mapa
            print ("vitima encontrada em ", self.currentState, " id: ", victimId, " sinais vitais: ", self.victimVitalSignalsSensor(victimId))
            self.getVictimVitalSignals(victimId)
            self.addVictimToMap(self.currentState, victimId)

    """Checa os sinais vitais da vítima especificada e consome o tempo dessa ação.
    @param victimId: o id da vítima"""
    def getVictimVitalSignals(self, victimId):
        self.time -= self.prob.getActionCost("checkVitalSignals")
        self.costAll += self.prob.getActionCost("checkVitalSignals")
        vitalSignals = self.victimVitalSignalsSensor(victimId)
        self.prob.saveVitalSignals(vitalSignals[0])
        return vitalSignals

    """Adiciona uma parede no mapa do robô na posição especificada
    @param position: posição no mapa"""
    def addWallToMap(self, position):
        self.prob.updateMazePosition(position, -2)

    """Adiciona uma posição explorada no mapa do robô na posição especificada
    @param position: posição no mapa"""
    def addExploredPositionToMap(self, position):
        self.prob.updateMazePosition(position, 0)

    """Adiciona uma vítima no mapa do robô na posição especificada
    @param position: posição no mapa"""
    def addVictimToMap(self, position, victimId):
        self.prob.updateMazePosition(position, victimId)

    """Verifica se ainda tem algum plano para executar e se ainda tem tempo para continuar executando o programa"""
    def canKeepExecuting(self):
        ## Verifica se há algum plano a ser executado
        if len(self.libPlan) == 0:
            return 0   ## fim da execucao do agente, acabaram os planos
        
        ## Verifica se ainda tem tempo para executar
        if self.time <= 0:
            self.prob.printWalls()
            self.prob.printExplored()
            self.prob.printVictims()
            self.prob.printVitalSignals()
            return 0 ## fim da execucao do agente, acabou o tempo

        return 1

    """Verifica qual a posição atual do agente e atualiza essa posição no plano do agente"""
    def updateCurrentState(self):
        self.currentState = self.positionSensor()
        self.plan.updateCurrentState(self.currentState) # atualiza o current state no plano
        print("Ag cre que esta em: ", self.currentState)

    """Verifica se a ação foi executada com sucesso:
    Se ela tiver funcionado, adiciono a posição atual como uma posição explorada no mapa
    Se ela não tiver funcionado, adiciono a posição que eu esperava estar como uma posição com parede no mapa"""
    def checkPreviousExecution(self):
        if not (self.currentState == self.expectedState): #Ação não funcionou: tenho que marcar uma parede no mapa
            print("---> erro na execucao da acao ", self.previousAction, ": esperava estar em ", self.expectedState, ", mas estou em ", self.currentState)
            self.addWallToMap(self.expectedState)
        else: #Ação funcionou: tenho que marcar o mapa como explorado
            if not(self.prob.isVictimInPosition(self.currentState)):
                self.addExploredPositionToMap(self.currentState)

    """ Define a proxima acao a ser executada e então executa-a.
        """
    def executeNextAction(self):
        # Escolhe a próxima ação de acordo com o plano que está sendo executado
        result = self.plan.chooseAction()
        # result é uma tupla na forma: <direcao>, <state>
        action = result[0]
        expectedState = result[1]
        print("Ag deliberou pela acao: ", action, " o estado resultado esperado é: ", expectedState)

        # Executa a próxima ação e atualiza a previousAction e o expectedState para verificar
        # no próximo ciclo se a ação funcionou
        self.executeGo(action)
        self.previousAction = action
        self.expectedState = expectedState

    def checkShouldReturnToBase(self):
        if(self.time-3 <= self.costAll): # Se não passar no if é porque tem mais tempo sobrando do que gastou até agora, então terá tempo para retornar
            plano = BaseReturnPlan(self.prob, "voltarBase") # Cria plano de voltar para a base
            if (self.time - plano.getCost() <= 3 ): # Verifica se tem tempo sobrando caso execute mais uma ação. Se não tiver, inicia o plano de voltar para a base
                self.libPlan.pop(0)
                self.libPlan.append(plano)