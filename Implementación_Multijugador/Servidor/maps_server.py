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
        self.clientRoomManagerPrx = roomManagerPrx
        self.roomsProxies = {}

    def start(self):
        self.createClient().hello(self.clientRoomManagerPrx, self.roomManager.id)  

    def hello(self, newRoom, idRoom, current=None):
        self.roomsProxies[idRoom] = newRoom
        #print(self.roomManager.id + ' :'+idRoom)
        #print(self.roomManager.id + ' :{}'.format(self.roomsProxies))
        if idRoom != self.roomManager.id:
            print(self.roomManager.id + ' :hello: '+idRoom)
            self.createClient().announce(self.clientRoomManagerPrx, self.roomManager.id)  
        #print(self.roomManager.id + ' : hello => ' + idRoom)
        #print(self.roomsProxies)

    def createClient(self):
        return IceGauntlet.RoomManagerSyncPrx.uncheckedCast(self.syncChannelPrx.getPublisher())

    def announce(self, newRoom, idRoom, current=None):
        if not(idRoom in self.roomsProxies):
            self.roomsProxies[idRoom] = newRoom
            if self.roomManager.id == idRoom:
                return
            print(self.roomManager.id + ' : announce a => ' + idRoom)
            #print(self.roomManager.id + ' : announce b => {}'.format(self.roomsProxies))
            if idRoom != self.roomManager.id:
                try:
                    strRoomsOfManager = IceGauntlet.RoomManagerPrx.checkedCast(self.roomsProxies[idRoom]).availableRooms()
                except:
                    strRoomsOfManager = []
                print(self.roomManager.id + ' : recibe las habitaciones de  ' + idRoom + '\n {}'.format(strRoomsOfManager))
                if len(strRoomsOfManager) > 0:
                    for mapaStored in strRoomsOfManager:
                        if not(self.existMap(mapaStored)):
                            item = {"room": mapaStored, "data": json.loads(self.roomsProxies[idRoom].getRoom(mapaStored))}
                            self.roomManager.maps.append(item)

                #print(self.roomManager.id + ' : announce')
                self.printMaps()
    
    def existMap(self, mapaStored, current=None):
        for map in self.roomManager.maps:
            if map['room'] == mapaStored:
                return True
        return False

    def newRoom(self, roomName, idRoomManager, current=None):
        strRoomsOfManager = self.roomsProxies[idRoomManager].availableRooms()
        for mapRoom in strRoomsOfManager:
            if mapRoom == roomName:
                available = False
                for mapaStored in self.roomManager.maps:
                     if mapRoom == mapaStored['room']:
                         available = True
                if not(available):
                    item = {"room": mapRoom, "data": json.loads(self.roomsProxies[idRoomManager].getRoom(mapRoom))}
                    self.roomManager.maps.append(item)
        print(self.roomManager.id + ' : newRoom')
        self.printMaps()

    def removedRoom(self, roomName, current=None):
        for mapRoom in self.roomManager.maps:
            if(mapRoom['room'] == roomName):
                self.roomManager.maps.remove(mapRoom)
        print(self.roomManager.id + ' : removedRoom')
        self.printMaps()

    def printMaps(self):
        for map in self.roomManager.maps:
            print(map['room'])
        print('\n')

# pylint: disable=C0115
class RoomManagerI(IceGauntlet.RoomManager):
    def __init__(self, auth_server, id):
        self.id = id
        self.roomManagerSync = None
        self.maps = []
        self.auth_server = auth_server

    # pylint: disable=W0613
    def availableRooms(self, current=None):
        ##print(self.id+' availableRooms')
        maps_string = []
        if len(self.maps) > 0:
            for map in self.maps:
                maps_string.append(map['room'])

        print(self.id+' AVAILABLE ROOMS:\n{} '.format(maps_string))
        return maps_string

    # pylint: disable=W0613
    def getRoom(self, name, current=None):
        for map in self.maps:
            if map['room'] == name:
                return json.dumps(map['data'])
        raise IceGauntlet.RoomNotExists()

    # pylint: disable=W0613
    def publish(self, tkn, room_json, current=None):
        number = 0
        json_map = json.loads(room_json)
        if self.check(json_map):
            try:
                usuario = self.auth_server.getOwner(tkn)

            except IceGauntlet.Unauthorized():
                #print("No se ha recuperado ningun token")
                raise IceGauntlet.Unauthorized()

            if json_map in self.maps:
                raise IceGauntlet.RoomAlreadyExists()
            else:
                self.maps.append(json_map)  # Lo metemos en la lista
                self.syncServers(True, json_map['room'])

        else:
            raise IceGauntlet.WrongRoomFormat()

    def syncServers(self, upload, data):
        if upload and self.roomManagerSync:
            self.roomManagerSync.createClient().newRoom(data, self.id)
        elif not(upload) and self.roomManagerSync:
            self.roomManagerSync.createClient().removedRoom(data)


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
        except IceGauntlet.Unauthorized():
            #print("No se ha recuperado ningun token")
            raise IceGauntlet.Unauthorized()

        if self.exist(room_name):
            for map in self.maps:
                if map['room'] == room_name:
                    self.maps.remove(map)
                    self.syncServers(False, room_name)

                i += 1
        else:
            raise IceGauntlet.RoomNotExists()


    def exist(self, room_name):
        encontrado = False
        for map in self.maps:
            if map['room'] == room_name:
                encontrado = True
                return encontrado
        return encontrado

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
            #print("Invalid topic proxy")
            return 2

        topicPrx = IceStorm.TopicManagerPrx.checkedCast(proxyIceBox)
        #print("Icebox ready")

        try:
            topicRoomSyncPrx = topicPrx.retrieve("RoomManagerSyncChannel")
        except IceStorm.NoSuchTopic:
            topicRoomSyncPrx = topicPrx.create("RoomManagerSyncChannel")
        #print("Created RoomManagerSyncChannel")

        roomManagerSync = RoomManagerSyncI(topicRoomSyncPrx, roomManager, IceGauntlet.RoomManagerPrx.checkedCast(roomManagerPrx))
        roomManager.roomManagerSync = roomManagerSync
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
        #print(roomManager.id + ' "{}"'.format(roomManagerPrx), flush=True)

        logging.debug('Entering server loop...')
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


if __name__ == '__main__':
    app = Server()
    sys.exit(app.main(sys.argv))
