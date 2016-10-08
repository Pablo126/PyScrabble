import random

#Primer campo, nombre archivo; Segundo, valor de ficha; Tercero, numero de fichas iniciales
A = ["A",1,16]
B = ["B", 3, 4]
C = ["C", 3, 6]
D = ["D", 2, 8]
E = ["E", 1, 24]
F = ["F", 4, 4]
G = ["G", 2, 5]
H = ["H", 4, 5]
I = ["I", 1, 13]
J = ["J", 8, 2]
K = ["K", 5, 2]
L = ["L", 1, 7]
M = ["M", 3, 6]
N = ["N", 1, 13]
O = ["O", 1, 15]
P = ["P", 3, 4]
Q = ["Q", 10, 2]
R = ["R", 1, 13]
S = ["S", 1, 10]
T = ["T", 1, 15]
U = ["U", 1, 7]
V = ["V", 4, 3]
W = ["W", 4, 4]
X = ["X", 8, 2]
Y = ["Y", 4, 4]
Z = ["Z", 10, 2]
letras = [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z]

class Scrabble(object):
    def __init__(self):
        self.totals_letters= 196
        self.count_letters=0
        palabra_inicio = [H, E, L, L, O]

    def quedanLetras(self,letra):
        if(letra[2]>0):
            letra[2]=letra[2]-1
            return True
        return False

    def getToken(self):
        while(True):
            if (self.totals_letters == self.count_letters):
                return 0
            letra = random.choice(letras)
            if(self.quedanLetras(letra)):
                self.count_letters+=1
                break
        return letra

