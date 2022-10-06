## AGENTE RESCUE
### @Author: Gabriel Linke e Thiago de Mendonça (UTFPR)
### Agente que recebe informações coletadas pelo Agente Explorador e tenta
### resgatar o máximo de vítimas possível, priorizando gravidade em certa medida
### Executa raciocíni on-line: percebe --> [delibera] --> executa ação --> percebe --> ...
import sys
import os
import time as _time

## Importa Classes necessarias para o funcionamento
from model import Model
from problem import Problem
from state import State
from random import randint

## Importa o algoritmo para o plano
from greedyPathPlan import GreedyPathPlan

## Classe que define o Agente de resgate
class AgentRescue:
    def __init__(self, model, problem, time, debug_mode):
        """ 
        Construtor do agente rescue
        @param model referencia o ambiente onde o agente estah situado
        @param problem: crenças do agente
        @param time: tempo para execução
        """

        self.debug = debug_mode
        self.model = model

        ## Obtem o tempo que tem para executar
        self.time = time
        print("Tempo disponivel: ", self.time)
        
        ## Pega o tipo de mesh, que está no model (influência na movimentação)
        self.mesh = self.model.mesh

        ## Cria a instância do problema na mente do agente (sao suas crencas)
        self.prob = problem

        # print("\n\n*** Agente de resgate, informações do problema: ")
        # self.prob.printWalls()
        # self.prob.printExplored()
        # self.prob.printVictims()
        # self.prob.printVitalSignals()

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

        ## Cria a instancia do plano para decidir o caminho a seguir
        self.plan = GreedyPathPlan(self.prob, initial, time)

        ## Adiciona o(s) planos a biblioteca de planos do agente
        self.libPlan = [self.plan]

        ## inicializa acao do ciclo anterior com o estado esperado
        self.previousAction = "nop"    ## nenhuma (no operation)
        self.expectedState = self.currentState

    ## Metodo que define a deliberacao do agente 
    def deliberate(self):

        # Verifica se pode continuar deliberando
        if not (self.canKeepExecuting()): 
            return -1

        # Atualiza o plano que irá executar
        self.plan = self.libPlan[0]

        # Inicia o raciocínio do agente
        if(self.debug):
            print("\n*** Inicio do ciclo raciocinio ***")
            print("Pos agente no amb.: ", self.positionSensor())

        # Redefine o estado atual do agente de acordo com o resultado da execução da ação do ciclo anterior
        self.updateCurrentState()

        # Funcionou ou nao, vou somar o custo da acao com o total 
        self.costAll += self.prob.getActionCost(self.previousAction)
        if(self.debug):
            print ("Custo até o momento (com a ação escolhida):", self.costAll) 

        # consome o tempo gasto
        self.time -= self.prob.getActionCost(self.previousAction)
        if(self.debug):
            print("Tempo disponivel: ", self.time)

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

    # def victimPresenceSensor(self):
    #     """Simula um sensor que realiza a deteccao de presenca de vitima na posicao onde o agente se encontra no ambiente
    #        @return retorna o id da vítima"""     
    #     return self.model.isThereVictim()

    # def victimVitalSignalsSensor(self, victimId):
    #     """Simula um sensor que realiza a leitura dos sinais da vitima 
    #     @param o id da vítima
    #     @return a lista de sinais vitais (ou uma lista vazia se não tem vítima com o id)"""     
    #     return self.model.getVictimVitalSignals(victimId)
    
    ## Metodo que atualiza a biblioteca de planos, de acordo com o estado atual do agente
    def updateLibPlan(self):
        for i in self.libPlan:
            i.updateCurrentState(self.currentState, self.time)

    def actionDo(self, posAction, action = True):
        self.model.do(posAction, action)

    """Verifica se ainda tem algum plano para executar e se ainda tem tempo para continuar executando o programa"""
    def canKeepExecuting(self):
        ## Verifica se há algum plano a ser executado
        if len(self.libPlan) == 0:
            return 0   ## fim da execucao do agente, acabaram os planos
        
        ## Verifica se ainda tem tempo para executar
        if self.time <= 0:
            return 0 ## fim da execucao do agente, acabou o tempo

        return 1

    """Verifica qual a posição atual do agente e atualiza essa posição no plano do agente"""
    def updateCurrentState(self):
        self.currentState = self.positionSensor()
        self.plan.updateCurrentState(self.currentState, self.time) # atualiza o current state no plano
        if(self.debug):
            print("Ag cre que esta em: ", self.currentState)

    """ Define a proxima acao a ser executada e então executa-a.
        """
    def executeNextAction(self):
        # Escolhe a próxima ação de acordo com o plano que está sendo executado
        result = self.plan.chooseAction()
        # result é uma tupla na forma: <direcao>, <state>
        action = result[0]
        expectedState = result[1]
        if(self.debug):
            print("Ag deliberou pela acao: ", action, " o estado resultado esperado é: ", expectedState)

        # a ação "nop" só ocorre quando acabam as opções do agente
        # por isso, a execução já pode parar depois de retornar o primeiro "nop"
        if action == "nop":
            self.printMetrics()
            self.libPlan.remove(self.plan)

        # Executa a próxima ação e atualiza a previousAction e o expectedState para verificar
        # no próximo ciclo se a ação funcionou
        self.executeGo(action)
        self.previousAction = action
        self.expectedState = expectedState

    def printMetrics(self):
        V = self.model.getNumberOfVictims()
        victimsVitalSignals = [self.model.getVictimVitalSignals(victimId)[0] for victimId in range(1, V+1)]
        self.plan.printMetrics(self.costAll, victimsVitalSignals, V)