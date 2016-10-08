from mastermind_import import *
from settings import *

import threading
from time import gmtime, strftime
import game



class ServerChat(MastermindServerTCP):
    def __init__(self):
        MastermindServerTCP.__init__(self, 0.5,0.5,10.0) #server refresh, connections' refresh, connection timeout
        self.chat = [None]*scrollback
        self.mutex = threading.Lock()
        self.currentgame = game.Game()


    def add_message(self, msg):
        timestamp = strftime("%H:%M:%S",gmtime())
        
        self.mutex.acquire()
        self.chat = self.chat[1:] + [timestamp+" | "+msg]
        self.mutex.release()

    def callback_connect          (self                                          ):
        #Something could go here
        return super(ServerChat,self).callback_connect()
    def callback_disconnect       (self                                          ):
        #Something could go here
        return super(ServerChat,self).callback_disconnect()
    def callback_connect_client   (self, connection_object                       ):
        #Something could go here
        return super(ServerChat,self).callback_connect_client(connection_object)
    def callback_disconnect_client(self, connection_object                       ):
        #Something could go here
        return super(ServerChat,self).callback_disconnect_client(connection_object)
    
    def callback_client_receive   (self, connection_object                       ):
        #Something could go here
        return super(ServerChat,self).callback_client_receive(connection_object)
    def callback_client_handle    (self, connection_object, data                 ):
        cmd = data[0]
        fichas = None
        grid = None
        state_player = None
        if cmd == "introduce":
            self.currentgame.add_player(data[1])
            self.add_message("Server: "+data[1]+" has joined.")
        elif cmd == "add":
            self.add_message(data[1])
        elif cmd == "update":
            pass
        elif cmd == "gettoken":
            fichas = self.currentgame.addTokenToPlayer(data[1])
        elif cmd == "getstate":
            state_player = self.currentgame.getPlayerState(data[1])
        elif cmd == "removetoken":
            fichas = self.currentgame.removeToken(data[1],data[2])
        elif cmd == "gettokenlist":
            fichas = self.currentgame.getTokenListByPlayer(data[1])
        elif cmd == "sendgrid":
            grid = self.currentgame.compareGrids(self.currentgame.grid,data[2],data[1])
        elif cmd == "leave":
            if self.currentgame.del_player(data[1]):
                self.add_message("Server: "+data[1]+" has left.")
        if fichas != None:
            self.callback_client_send(connection_object, fichas)
        elif state_player != None:
            self.callback_client_send(connection_object, state_player)
        elif grid != None:
            for c in self._mm_connections.items():
              self.callback_client_send(c.__getitem__(1), grid)
        else:
            self.callback_client_send(connection_object, self.chat)

    def callback_client_send      (self, connection_object, data,compression=None):
        #Something could go here
        return super(ServerChat,self).callback_client_send(connection_object, data,compression)

if __name__ == "__main__":
    server = ServerChat()
    server.connect(server_ip,port)

    try:
        server.accepting_allow_wait_forever()
    except:
        #Only way to break is with an exception
        pass
    server.accepting_disallow()
    server.disconnect_clients()
    server.disconnect()
