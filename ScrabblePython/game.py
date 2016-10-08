from collections import deque
import chat_server
from settings import *
import player
import scrabble

#NUMERO DE FICHAS CON LAS QUE JUEGA CADA JUGADOR
N_FICHAS_JUGADOR = 8
#TAMANO DE TABLERO(FILAS X COLUMNAS)
TAMANO=10
#EL NUMERO DE FILA PARA LAS FICHAS DEL JUGADOR, NORMALMENTE 1 MAS DEL TAMANO
FILA_FICHAS_JUGADOR = 11
#TAMANO DEL PAQUETE DE INFORMACION DE JUEGO
TAM_INFOGAME = 2
class Game(object):
    def __init__(self):
        self.player_list = []
        self.queue = deque([])
        self.data = "NO DATA"
        # MATRIZ LOGICA PARA TABLERO
        self.grid = [[-1 for i in xrange(TAMANO)] for i in xrange(TAMANO)]
        self.scrabble = scrabble.Scrabble()
        self.current_player = ""

    def getNextIDPlayer(self):
        return self.player_list.__len__()+1

    def getPlayerState(self,playername):
        p = self.getPlayerByName(playername)
        package = []
        package.append(self.current_player)
        package.append(p.getPoints())
        return package

    def add_player(self,playername):
        p = player.Player(self.getNextIDPlayer(),playername,N_FICHAS_JUGADOR,self.scrabble)
        try:
            self.player_list.append(p)
            self.create_queue()
            self.current_player = self.next_player().getName()
            return True
        except:
            return False

    def del_player(self,playername):
        try:
            self.player_list.remove(self.getPlayerByName(playername))
            self.create_queue()
            return True
        except:
            return False

    def create_queue(self):
        try:
            self.queue = deque(self.player_list)
            self.next_player()
            return True
        except:
            return False

    def next_player(self):
        try:
            p = self.queue.popleft()
            #self.queue.remove(p)
            self.queue.append(p)
            self.current_player = p.getName()
            return p
        except:
            return "Unknown"

    def addTokenToPlayer(self,name):
        p = self.getPlayerByName(name)
        return p.addNewToken(self.scrabble)

    def removeToken(self,name,index):
        p = self.getPlayerByName(name)
        p.removeToken(index)
        return p.getTokenList()

    def getPlayerByName(self,name):
        for p in self.player_list:
            if p.getName()==name:
                return p
        return False

    def getTokenListByPlayer(self,name):
        p = self.getPlayerByName(name)
        return p.getTokenList()

    def diferenceBetweenMatrixes(self,matrix_original,matrix_comparable):
        aux_grid = [[-1 for i in xrange(len(matrix_original))] for i in xrange(len(matrix_original))]
        for fila in range(0,len(matrix_original)):
            for columna in range(0,len(matrix_original)):
                if matrix_original[fila][columna] != matrix_comparable[fila][columna]:
                    aux_grid[fila][columna] = matrix_comparable[fila][columna]
        return aux_grid

    def compareGrids(self,game_grid,player_grid,name):
        #extraemos la matriz diferencia entre la del juego y la del cliente
        diference_grid = self.diferenceBetweenMatrixes(game_grid,player_grid)
        #Comprobamos que se ha cambiado algo, si no no hacemos nada
        if self.newGridNotNull(diference_grid):
        #comprobamos que es una combinacion valida (horizontal o vertical)
            coor_word = self.checkGrid(diference_grid)
            if(coor_word.__len__()>1):
                #extraemos la palabra del grid
                word = self.extractWord(diference_grid,coor_word)
                #convertimos a string el array
                word_str = ''.join(word)
                #buscamos en el diccionario la palabra
                print("Searching in dictionary...")
                if self.searchWord('HELLO'):
                    self.getPlayerByName(name).sumPoints(self.calculatePointsofWord(word))
                    self.grid = player_grid
                    self.next_player()
                    return self.grid
                    print("Word found")
                else:
                    print("Word NOT found")

    def calculatePointsofWord(self,word_array):
        sum = 0
        for l in word_array:
            for k in scrabble.letras:
                if(l==k[0]):
                    sum+=k[1]
        return sum


    def searchWord(self,word):
        with open("dictionary.txt", "r") as ins:
            for line in ins:
                if(line.rstrip('\n').upper()==word.upper()):
                    return True
            return False

    def newGridNotNull(self,grid_newstokens):
        for fila in grid_newstokens:
            for columna in fila:
                if(columna!=-1):
                    return True
        return False

    def extractWord(self,grid_newstokens,coordinates_word):
        palabra = []
        index = 0
        for coor in coordinates_word:
            if grid_newstokens[coor[0]][coor[1]]!=-1:
                palabra.append(grid_newstokens[coor[0]][coor[1]][0])
            elif self.grid[coor[0]][coor[1]]!=-1:
                palabra.append(self.grid[coor[0]][coor[1]][0])
        return palabra

    def checkGrid(self,grid_newstokens):
        palabras = None
        coordenada_primera =[]
        encontrada = False
        #Extraemos la primera letra de las nuevas que se han puesto
        for fila in range(0, len(grid_newstokens)):
            if encontrada:
                break
            for columna in range(0, len(grid_newstokens)):
                if grid_newstokens[fila][columna] != -1:
                    if encontrada:
                        break
                    coordenada_primera=[fila, columna]
                    encontrada = True

        horizontal = False
        vertical = False
        #Horizontal
        p = []
        f = coordenada_primera[0]
        for i in range(0,len(grid_newstokens)):
            if grid_newstokens[f][i]!=-1 or self.grid[f][i]!=-1:
                p.append([f,i])
            else:
                if p.__len__()>1:
                    for c in p:
                        if c==coordenada_primera:
                            palabras = p
                            horizontal = True
                    p=[]
                else:
                    p=[]

        # Vertical
        p = []
        c = coordenada_primera[1]
        for i in range(0, len(grid_newstokens)):
            if grid_newstokens[i][c] != -1 or self.grid[i][c] != -1:
                p.append([i, c])
            else:
                if p.__len__() > 1:
                    for j in p:
                        if j == coordenada_primera:
                            if(palabras==None or palabras.__len__()<p.__len__()):
                                palabras = p
                                vertical = True
                    p = []
                else:
                    p = []

        #if horizontal:

        return palabras