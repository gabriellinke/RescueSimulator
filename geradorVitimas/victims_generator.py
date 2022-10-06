import random
import os

class Vict_gen:
    def __init__(self, mazeSizeX, mazeSizeY, qtdVictims, timeE, timeS, posBase):
        self.mazeSizeX = mazeSizeX
        self.mazeSizeY = mazeSizeY
        self.timeE = timeE
        self.timeS = timeS
        self.posBase = posBase
        self.qtdVictims = qtdVictims
        self.posVictims = []
        self.walls = []
        self.vitalSignals = []
        self.diffAccess = []
        self.generatorVictims()
        self.savePos()

    def generateWalls(self):
        walls = []
        qtd = random.randint(10, self.mazeSizeX*4)
        cont = 0
        while cont < qtd:
            row = random.randint(0, self.mazeSizeX-1)
            col = random.randint(0, self.mazeSizeY-1)
            if (row > 0 or col > 0) and (row, col) not in walls and (row, col) != self.posBase:
                self.walls.append((row, col))
                cont += 1
    
    def generatorVictims(self):
        self.generateWalls()
        qtdGen = 0
        while qtdGen < self.qtdVictims:
            pos = (random.randint(0, self.mazeSizeX-1), random.randint(0, self.mazeSizeY-1))
            if pos not in self.posVictims and (pos not in self.walls) and pos != self.posBase:
                self.posVictims.append(pos)
                    
                self.vitalSignals.append([
                    qtdGen+1,
                    round(random.random(),2),
                    round(random.random(),2),
                    round(random.random(),2),
                    round(random.random(),2),
                    round(random.random(),2),
                    round(random.random(),2)])
                
                qtdGen += 1
                
    def savePos(self):
        arquivo = open(os.path.join("..", "config_data", "ambiente.txt"), "w")
        strSave = "Te "+str(self.timeE)+"\n"
        strSave += "Ts "+str(self.timeS)+"\n"
        strSave += "Base "+str(self.posBase[0])+","+str(self.posBase[1])+"\n"
        strSave += "XMax "+str(self.mazeSizeY)+"\n"
        strSave += "YMax "+str(self.mazeSizeX)+"\n"
        strSave += "Vitimas"
        for i in self.posVictims:
            strSave += " " + str(i[0]) + "," + str(i[1])
        strSave += "\nParede"
        for i in self.walls:
            strSave += " " + str(i[0]) + "," + str(i[1])
        arquivo.writelines(strSave)
        arquivo.close()
        print("gerou new ambiente.txt\n")

        strSave=""
        sinaisvitais = open(os.path.join("..", "config_data", "sinais_vitais.txt"), "w")
        for i in self.vitalSignals:
            strSave += str(i[0]) + "," + str(i[1]) + "," + str(i[2]) + "," + str(i[3]) + "," + str(i[4]) + "," + str(i[5]) + "," + str(i[6]) + "\n"
        sinaisvitais.writelines(strSave)
        sinaisvitais.close()
        print("gerou new sinaisvitais.txt\n")

