try:    name = raw_input("Enter a screen name: ")
except: name =     input("Enter a screen name: ")

import pygame
from pygame.locals import *
import traceback
pygame.display.init()
pygame.font.init()
from mastermind_import import *
from settings import *
import scrabble
import game

#COLORES
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
COLOR_FONDO = (60,179,113)
COLOR_TABLERO = (255, 249, 196)
COLOR_FICHAS_JUGADOR = (255,224,130)


#TAMANO DE PIEZAS DEL TABLERO
ALTO = 40
LARGO = 40
MARGEN = 5

client = None

log = [None]*scrollback

message = ""
to_send = [
    ["introduce",name]
]
ficha_jugador_seleccionada_ant = -1

folder = "letras"  # replace with "." if pictures lay in the same folder as program

class PygView(object):

    #FUNCION PRINCIPAL DONDE INICIALIZAR
    def __init__(self, width=800, height=600, fps=30):
        """Initialize pygame, window, background, font,..."""
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        self.width = width
        self.height = height
        #self.height = width // 4
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(COLOR_FONDO)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        # MATRIZ LOGICA PARA TABLERO DEL CLIENTE
        self.grid = []

        # FILA LOGICA PARA FICHAS DE JUGADOR
        self.fichas = []
        self.stateplayer = ["",0]

    #FUNCION QUE MANEJA LOS CLICKS EN LAS FICHAS Y CASILLAS
    def handler_click(self,event):
        if self.stateplayer[0] == name:
            # --------------------------------------
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Obtenemos la posicion del click
                pos = pygame.mouse.get_pos()
                # Cambia las coordenadas x/y de la pantalla por coordenadas reticulares
                columna = pos[0] // (LARGO + MARGEN)
                fila = pos[1] // (ALTO + MARGEN)
                # TABLERO---------------------------------
                if (fila < game.TAMANO and columna < game.TAMANO):
                    if(self.grid[fila][columna] == -1):#SI NO HAY FICHA YA EN ESE HUECO
                        if(self.ficha_jugador_seleccionada_ant!= -1): #SI EXISTE UNA FICHA SELECCIONADA
                            self.grid[fila][columna] = self.fichas[self.ficha_jugador_seleccionada_ant] #MOVEMOS LA FICHA AL TABLERO
                            self.fichas[self.ficha_jugador_seleccionada_ant] = 0 #VACIAMOS LA CASILLA DE FICHA DE JUGADOR MOVIDA
                            self.removeToken(self.ficha_jugador_seleccionada_ant)
                            self.grid[game.FILA_FICHAS_JUGADOR][self.ficha_jugador_seleccionada_ant] = 0 #LIMPIAMOS EL ESTADO DE SELECCIONADO
                            self.ficha_jugador_seleccionada_ant = -1 #ELIMINAMOS EL INDICE DE FICHA SELECCIONADA
                    print("Click ", pos, "Coordenada de tablero:", fila, columna)
                # FICHAS JUGADOR---------------------------------
                elif (fila == game.FILA_FICHAS_JUGADOR and columna<game.N_FICHAS_JUGADOR):
                    if(self.fichas[columna]!= 0 ):
                        #Si ya estaba seleccionada, se deselecciona
                        if(self.ficha_jugador_seleccionada_ant==columna and self.grid[game.FILA_FICHAS_JUGADOR][columna] == 1):
                            self.grid[game.FILA_FICHAS_JUGADOR][columna] = 0
                        else:
                            self.grid[game.FILA_FICHAS_JUGADOR][self.ficha_jugador_seleccionada_ant] = 0
                            self.grid[game.FILA_FICHAS_JUGADOR][columna] = 1
                            self.ficha_jugador_seleccionada_ant = columna
                    print("Click ", pos, "Coordenada de jugador:", fila, columna)
                elif (fila == game.FILA_FICHAS_JUGADOR and columna == game.TAMANO-1):
                    self.sendGrid(self.grid)
                elif(fila==game.FILA_FICHAS_JUGADOR and columna==game.TAMANO):
                    print("Click ", pos, "COGIENDO CARTA", fila, columna)
                    self.getToken()
                    #self.robarFichaNueva()

            # -----------------------------------------

    #-----------------------------------HILO DE EJECUCION PRINCIPAL DEL JUEGO---------------------------------
    def run(self):

        #CONEXION DE CLIENTE Y SERVIDOR-------------------------------
        global client, server
        client = MastermindClientTCP(client_timeout_connect, client_timeout_receive)
        try:
            print("Client connecting on \"" + client_ip + "\", port " + str(port) + " . . .")
            client.connect(client_ip, port)
        except MastermindError:
            print("No server found; starting server!")
            print("Client connecting on \"" + client_ip + "\", port " + str(port) + " . . .")
            client.connect(client_ip, port)
        print("Client connected!")
        #FIN CLIENTE SERVIDOR---------------------------------------------------

        # Creamos la cuadricula logica del tablero
        for fila in range(game.TAMANO + 2):
            self.grid.append([])
            for columna in range(game.TAMANO + 2):
                self.grid[fila].append(-1)

        for i in range(game.N_FICHAS_JUGADOR):
            self.fichas.append(0)
        #self.pintarPalabraInicial()
        self.getTokenList()
        #self.obtenerFichasInicio()
        self.ficha_jugador_seleccionada_ant = -1

        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit(name)
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit(name)
                        running = False
                #Funcion que controla los clicks en el tablero
                self.handler_click(event)
            #-----------------------ENVIO DE MENSAJE CHAT
                if not self.get_input(event):
                    to_send.append(["leave", name])
                 #   self.send_next_blocking()
                 #   break

            # -----------------------------------------------------------------
            self.draw_map()
            self.draw_chat()
            self.draw_text("Points:"+str(self.stateplayer[1])+"       Turn:"+str(self.stateplayer[0]),30,460)
            self.send_next_blocking()
            clock.tick(60)
            self.getState()

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            pygame.display.set_caption("FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(self.clock.get_fps(), " "*5, self.playtime))
            #self.draw_text("FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(self.clock.get_fps(), " "*5, self.playtime))

            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

        pygame.quit()

        #----------------------------DESCONEXION DE SERVIDOR---------------------
        client.disconnect()
        #------------------------------------------------------------------------

    #FUNCION PARA PINTAR TEXTOS EN LA PANTALLA
    def draw_text(self, text,pos_x,pos_y):
        """Center text in window
        """
        fw, fh = self.font.size(text) # fw: font width,  fh: font height
        surface = self.font.render(text, True, (255, 255, 255))
        # // makes integer division in python3
        #self.screen.blit(surface, ((self.width - fw) // 2, (self.height - fh) // 2))
        self.screen.blit(surface, (pos_x,pos_y))

    #PINTAMOS EL CHAT-------------------------------------------------------
    def draw_chat(self):
        font = pygame.font.SysFont("Times New Roman", 14)
        x = self.width - 280
        y = self.height - 190

        for msg in log[::-1]:
            if msg == None: break
            surf_msg = font.render(msg, True, (255, 255, 255))
            self.screen.blit(surf_msg, (x, y))
            y -= 15

        pygame.draw.rect(self.screen, (255, 255, 255), (self.width -280, self.height - 170, self.width, 20))
        surf_msg = font.render(message, True, (0, 0, 0))
        self.screen.blit(surf_msg, (self.width-280, self.height - 170 + 3))

    def obtenerTablero(self):
        aux_grid = [[-1 for i in xrange(game.TAMANO)] for i in xrange(game.TAMANO)]
        for fila in range(0,game.TAMANO):
            for columna in range(0,game.TAMANO):
                aux_grid[fila][columna] = self.grid[fila][columna]
        return aux_grid

    def modificarTablero(self,game_grid):
        for fila in range(0,game.TAMANO):
            for columna in range(0,game.TAMANO):
                self.grid[fila][columna] = game_grid[fila][columna]


    def robarFichaNueva(self):
        aux = -1
        for i in range(game.N_FICHAS_JUGADOR):
            if self.fichas[i]==0:
                aux = i
                self.fichas[i] = scrabble.obtenerFicha()
                break
        if(aux!=-1):
            return True
        return False

    def getToken(self):
        to_send.append(["gettoken", name])
        #self.send_next_blocking()

    def getState(self):
        to_send.append(["getstate", name])

    def exit(self,name):
        to_send.append(["leave", name])
        self.send_next_blocking()

    def getTokenList(self):
        to_send.append(["gettokenlist", name])
        self.send_next_blocking()

    def removeToken(self,index):
        to_send.append(["removetoken",name,index])
        #self.send_next_blocking()

    def sendGrid(self,grid):
        to_send.append(["sendgrid", name, self.obtenerTablero()])
        #self.send_next_blocking()



    def pintarPalabraInicial(self):
        aux = 0
        for i in scrabble.palabra_inicio:
            self.grid[4][aux+4] = i
            aux+=1

    #DIBUJAMOS EL TABLERO CON SUS FICHAS
    def draw_map(self):
        #Dibujamos la cuadricula del tablero
        for fila in range(game.TAMANO):
            for columna in range(game.TAMANO):
                if self.grid[fila][columna] != -1:
                    ficha_img = pygame.image.load(os.path.join(folder, self.grid[fila][columna][0] + ".jpg"))
                    ficha_img2 = ficha_img.convert_alpha()
                    self.screen.blit(pygame.transform.scale(ficha_img2, (LARGO, ALTO)),
                                     ((MARGEN + LARGO) * columna + MARGEN,
                                      (MARGEN + ALTO) * fila + MARGEN))
                    #------------------------------------------------------
                else:
                    pygame.draw.rect(self.screen,COLOR_TABLERO,[(MARGEN + LARGO) * columna + MARGEN, (MARGEN + ALTO) * fila + MARGEN, LARGO, ALTO])
        #Dibujamos el area para las fichas del jugador
        for columna in range(game.TAMANO+1):
            if columna<game.N_FICHAS_JUGADOR:
                if self.fichas[columna] != 0:
                    ficha_img = pygame.image.load(os.path.join(folder, self.fichas[columna][0]+".jpg"))
                    if(self.grid[game.FILA_FICHAS_JUGADOR][columna] == 1):
                        ficha_img.set_alpha(140)
                    ficha_img2 = ficha_img.convert_alpha()
                    self.screen.blit(pygame.transform.scale(ficha_img2, (LARGO, ALTO)),
                                     ((MARGEN + LARGO) * columna + MARGEN, (MARGEN + ALTO) * game.FILA_FICHAS_JUGADOR + MARGEN))
                else:
                    pygame.draw.rect(self.screen, COLOR_FICHAS_JUGADOR,[(MARGEN + LARGO) * columna + MARGEN, self.height - 100, LARGO, ALTO])
            elif columna==game.TAMANO-1:
                tick_green = pygame.image.load(os.path.join(folder,"tick_green.png"))
                tick_green2 = tick_green.convert_alpha()
                self.screen.blit(pygame.transform.scale(tick_green2, (LARGO, ALTO)),
                                 ((MARGEN + LARGO) * columna + MARGEN,
                                  (MARGEN + ALTO) * game.FILA_FICHAS_JUGADOR + MARGEN))
            elif columna==game.TAMANO:
                robar_ficha = pygame.image.load(os.path.join(folder,"hand.png"))
                robar_ficha2 = robar_ficha.convert_alpha()
                self.screen.blit(pygame.transform.scale(robar_ficha2, (LARGO, ALTO)),
                                 ((MARGEN + LARGO) * columna + MARGEN, (MARGEN + ALTO) * game.FILA_FICHAS_JUGADOR + MARGEN))
            else:
                pygame.draw.rect(self.screen,COLOR_FICHAS_JUGADOR,[(MARGEN + LARGO) * columna + MARGEN,self.height-100,LARGO,ALTO])





#----------------------------------------FUNCIONES DE CHAT-----------------------
#----------------------------------------FUNCIONES DE CHAT-----------------------
#----------------------------------------FUNCIONES DE CHAT-----------------------
    #MANEJO DE EVENTO PARA ENVIAR MENSAJES DE CHAT
    def get_input(self,evento):
        global message
        keys_pressed = pygame.key.get_pressed()
        if evento.type == QUIT:
            return False
        elif evento.type == KEYDOWN:
            if evento.key == K_ESCAPE:
                return False
            elif evento.key == K_RETURN:
                if message != "":
                    to_send.append(["add", "" + name + ": " + message])
                    message = ""
            elif evento.key == K_BACKSPACE:
                if len(message) > 0:
                    message = message[:-1]
            else:
                try:
                    message += str(evento.unicode)
                except:
                    pass
        return True

    #FUNCION DE BLOQUEO CLIENTE SERVIDOR
    def send_next_blocking(self):
        global log, to_send, continuing
        a = 0
        try:
            if len(to_send) == 0:
                client.send(["update"], None)
            else:
                client.send(to_send[0], None)
                to_send = to_send[1:]

            reply = None
            while reply == None:
                reply = client.receive(False)
                if a==30 and reply == None:
                    reply = log
                a+=1
            if(reply.__len__() == game.N_FICHAS_JUGADOR):
                self.fichas = reply
            elif (reply.__len__() == game.TAM_INFOGAME):
                self.stateplayer = reply
            elif(reply.__len__() == game.TAMANO):
                self.modificarTablero(reply)
            else:
                log = reply
        except MastermindError:
            continuing = False

# ----------------------------------------FIN FUNCIONES DE CHAT-----------------------
# ----------------------------------------FIN FUNCIONES DE CHAT-----------------------
# ----------------------------------------FIN FUNCIONES DE CHAT-----------------------




if __name__ == '__main__':
    try:
        PygView(800, 600).run()
    except:
        traceback.print_exc()
        pygame.quit()
        input()
    # call with width of window and fps
