import sys
import os
import time

## Importa as classes que serao usadas
sys.path.append(os.path.join("pkg"))
from model import Model
from agentExplorer import AgentExplorer
from agentRescue import AgentRescue

## Metodo utilizado para permitir que o usuario construa o labirindo clicando em cima
def buildMaze(model):
    model.drawToBuild()
    step = model.getStep()
    while step == "build":
        model.drawToBuild()
        step = model.getStep()
    ## Atualiza o labirinto
    model.updateMaze()


# Faz a leitura dos parâmetros do ambiente
def loadConfig():
    arq = open(os.path.join("config_data","ambiente.txt"),"r")
    configDict = {}
    for line in arq:
            var, *values = line.replace('\n', '').split(' ')
            if(var == 'Te' or var == 'Ts' or var == 'XMax' or var == 'YMax'):
                configDict[var] = int(values[0])
            elif(var == 'Base'):
                x, y = values[0].split(',')
                configDict[var] = [int(x),int(y)]
            elif(var == 'Vitimas' or var == 'Parede'):
                coords = []
                for coord in values:
                    x, y = coord.split(',')
                    coords.append([int(x), int(y)])
                configDict[var] = coords
    
    return configDict

def loadModelAndMaze(configDict):
    # Cria o ambiente (modelo) = Labirinto com suas paredes
    mesh = "square"

    ## nome do arquivo de configuracao do ambiente - deve estar na pasta <proj>/config_data
    loadMaze = "ambiente"

    model = Model(configDict["XMax"], configDict["YMax"], mesh, loadMaze)
    buildMaze(model)

    # Define a posição inicial do agente no ambiente - corresponde ao estado inicial
    model.setAgentPos(model.maze.board.posAgent[0],model.maze.board.posAgent[1])
    model.draw()

    return model

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description="Rescue Simulator")
    parser.add_argument("-d", "--debug", help="Debug mode", action="store_false", default=True)
    args = parser.parse_args()
    return args


def main():
    # Faz a leitura dos parâmetros do ambiente
    configDict = loadConfig()

    # Pega argumentos da linha de comando
    args = get_args()

    # Cria o ambiente (modelo)
    model = loadModelAndMaze(configDict)

    # Cria um agente explorador
    agentExplorer = AgentExplorer(model, configDict["Te"], args.debug)

    while agentExplorer.deliberate() != -1:
        model.draw()
        time.sleep(0.001) # para dar tempo de visualizar as movimentacoes do agente no labirinto
    model.draw()

    # Cria um agente de resgate
    agentRescue = AgentRescue(model, agentExplorer.prob, configDict["Ts"], args.debug)

    while agentRescue.deliberate() != -1:
        model.draw()
        time.sleep(0.01) # para dar tempo de visualizar as movimentacoes do agente no labirinto
    model.draw()

if __name__ == '__main__':
    main()
