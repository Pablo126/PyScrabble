import game
class Player(object):
    def __init__(self,id,name,n_tokens,scrabble_ins):
        self.ID = id
        self.Name = name
        self.Tokens = []
        self.getTokens(n_tokens,scrabble_ins)
        self.Points = 0

    def getTokens(self,n_tokens,scrabble_instance):
        for i in range(n_tokens):
            self.Tokens.append(scrabble_instance.getToken())

    def getName(self):
        return self.Name

    def getPoints(self):
        return self.Points

    def sumPoints(self,points):
        self.Points+=points

    def addNewToken(self,scrabble_instance):
        if self.Tokens.count(0) > 0:
            n = self.Tokens.count(0)
            for i in range(n):
                self.Tokens.pop()
            self.Tokens.append(scrabble_instance.getToken())
            while self.Tokens.__len__() < game.N_FICHAS_JUGADOR:
                self.Tokens.append(0)
        return self.Tokens



        if(self.Tokens.__len__()<game.N_FICHAS_JUGADOR):
            self.Tokens.append(scrabble_instance.getToken())
            return True
        return False

    def getTokenList(self):
        return self.Tokens

    def removeToken(self,index):
        self.Tokens.pop(index)
        while self.Tokens.__len__()<game.N_FICHAS_JUGADOR:
            self.Tokens.append(0)

