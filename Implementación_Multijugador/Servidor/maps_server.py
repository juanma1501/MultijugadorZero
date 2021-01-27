#!/usr/bin/env python3
"""Clase maps_server"""

import sys
import logging
import json
import os
from sys import excepthook
import IceStorm
import uuid
import Ice

Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet


# pylint: disable=C0115
class RoomManagerSyncI(IceGauntlet.RoomManagerSync):
    def __init__(self, syncChannelPrx, roomManager, roomManagerPrx):
        self.syncChannelPrx = syncChannelPrx
        self.roomManager = roomManager
        self.clientRoomManagerPrx = IceGauntlet.RoomManagerPrx.checkedCast(roomManagerPrx)
        self.roomsProxies = {}

    def start(self):
        # hello 
        self.createClient().hello(self.clientRoomManagerPrx, self.roomManager.id)  

    def hello(self, newRoom, idRoom, current=None):
        self.roomsProxies[idRoom] = newRoom
        self.createClient().announce(self.clientRoomManagerPrx, self.roomManager.id)  
        print(self.roomManager.id + ' : hello => ' + idRoom)
        print(self.roomsProxies)

    def createClient(self):
        return IceGauntlet.RoomManagerSyncPrx.uncheckedCast(self.syncChannelPrx.getPublisher())


    def announce(self, newRoom, idRoom, current=None):
        if not(idRoom in self.roomsProxies):
            self.roomsProxies[idRoom] = newRoom
        print(self.roomManager.id + ' : announce => ' + idRoom)
        print(self.roomsProxies)

'''

    def newRoom(self, roomName, managerId, current=None):

    def removedRoom(self, roomName, current=None):
'''


# pylint: disable=C0115
class RoomManagerI(IceGauntlet.RoomManager):
    def __init__(self, auth_server, id):
        self.id = id
        self.maps = []
        self.load_maps()
        self.auth_server = auth_server

    # pylint: disable=W0613
    def publish(self, tkn, room_json, current=None):
        number = 0
        json_map = json.loads(room_json)
        if self.check(json_map):
            try:
                usuario = self.auth_server.getOwner(tkn)

                if json_map in self.maps:
                    raise IceGauntlet.RoomAlreadyExists()
                else:
                    self.maps.append(json_map)  # Lo metemos en la lista
                    # Lo incluimos en la carpeta Loaded_Maps
                    # pylint: disable=W0612
                    for i in os.listdir("./Loaded_Maps"):
                        number += 1
                    with open('./Loaded_Maps/' + str(number) + '.json', 'w') as file:
                        json.dump(json_map, file)
            except IceGauntlet.Unauthorized():
                print("No se ha recuperado ningun token")
                raise IceGauntlet.Unauthorized()
        else:
            raise IceGauntlet.WrongRoomFormat()

    def check(self, json_map):
        if 'data' in json_map and 'room' in json_map:
            return True
        return False

    # pylint: disable=W0613
    # pylint: disable=C0116
    def remove(self, tkn, room_name, current=None):
        i = 0
        try:
            usuario = self.auth_server.getOwner(tkn)

            if self.exist(room_name):
                for map in self.maps:
                    if map['room'] == room_name:
                        self.maps.remove(map)
                        os.remove('./Loaded_Maps/' + str(i) + '.json')
                        self.rename()
                    i += 1
            else:
                raise IceGauntlet.RoomNotExists()

        except IceGauntlet.Unauthorized():
            print("No se ha recuperado ningun token")
            raise IceGauntlet.Unauthorized()

    # si luego no funciona, hay que quitar el static
    @staticmethod
    def rename():
        i = 0
        for map in os.listdir('./Loaded_Maps'):
            nombre_antiguo = './Loaded_Maps/' + str(map)
            nombre_nuevo = './Loaded_Maps/' + str(i) + '.json'
            os.rename(nombre_antiguo, nombre_nuevo)
            i += 1

    def exist(self, room_name):
        encontrado = False
        for map in self.maps:
            if map['room'] == room_name:
                encontrado = True
                return encontrado
        return encontrado

    # pylint: disable=C0116
    def load_maps(self):
        if len(os.listdir('./Loaded_Maps')) == 0:
            return

        for map in os.listdir('./Loaded_Maps'):
            with open('./Loaded_Maps/' + map) as json_file:
                self.maps.append(json.load(json_file))

    # si no funciona, hay que quitar el static
    @staticmethod
    def shutdown(current):
        current.adapter.getCommunicator().shutdown()

#pylint: disable=R0903
# pylint: disable=C0115
class DungeonI(IceGauntlet.Dungeon):
    def __init__(self, maps):
        self.maps = maps


    # pylint: disable=W0613
    def getRoom(self, current=None):
        if len(self.maps) == 0:
            raise IceGauntlet.RoomNotExists
        return json.dumps(self.maps)


# Vamos a crear un servidor con dos sirvientes, para el de mapas y para el de juego
# pylint: disable=C0115
class Server(Ice.Application):
    def run(self, args):

        logging.debug('Initializing server...')

        propertyAuthorization = self.communicator().propertyToProxy("authorization")
        authorizationProxy = IceGauntlet.AuthenticationPrx.checkedCast(propertyAuthorization)
        # Proxy del servicio de mapas
        #prx_auth = IceGauntlet.AuthenticationPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))
        roomManager = RoomManagerI(authorizationProxy, uuid.uuid4().hex)

        adapter = self.communicator().createObjectAdapter("RoomManagerAdapter")
        identityRoomManager = self.communicator().stringToIdentity(self.communicator().getProperties().getProperty('proxyIndex'))
        roomManagerPrx = adapter.add(roomManager, identityRoomManager)
        adapter.addDefaultServant(roomManager, '')

        # Ice Storm
        proxyIceBox = self.communicator().stringToProxy('Multijugador_SSDD.IceStorm/TopicManager')
        if proxyIceBox is None:
            print("Invalid topic proxy")
            return 2

        topicPrx = IceStorm.TopicManagerPrx.checkedCast(proxyIceBox)
        print("Icebox ready")

        try:
            topicRoomSyncPrx = topicPrx.retrieve("RoomManagerSyncChannel")
        except IceStorm.NoSuchTopic:
            topicRoomSyncPrx = topicPrx.create("RoomManagerSyncChannel")
        print("Created RoomManagerSyncChannel")

        roomManagerSync = RoomManagerSyncI(topicRoomSyncPrx, roomManager, roomManagerPrx)
        roomManagerSyncPrx = adapter.addWithUUID(roomManagerSync)
        topicRoomSyncPrx.subscribeAndGetPublisher(dict(),roomManagerSyncPrx)

        # Proxy del servicio de juego
        #servant_game = DungeonI(servant.maps)
        #adapter_game = self.communicator().createObjectAdapter("DungeonAdapter")
        #proxy_game = adapter_game.add(servant_game, self.communicator().stringToIdentity('dungeon'))
        #adapter_game.addDefaultServant(servant_game, '')
        #adapter_game.activate()

        # Vamos a escribir el proxy de juego en el txt, ya que este servidor solo puede imprimir uno
        #txt = open('proxy_juego.txt', 'w')
        #txt.write(str(proxy_game))
        #txt.close()
        adapter.activate()

        # Cliente del topic ejecuta hello
        roomManagerSync.start()

        logging.debug('Adapter ready, servant proxy: {}'.format(roomManagerPrx))
        print(roomManager.id + ' "{}"'.format(roomManagerPrx), flush=True)

        logging.debug('Entering server loop...')
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


if __name__ == '__main__':
    app = Server()
    sys.exit(app.main(sys.argv))
