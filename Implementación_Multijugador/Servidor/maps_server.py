#!/usr/bin/env python3
"""Clase maps_server"""

import sys
import logging
import json
import uuid
import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet
import IceStorm


# pylint: disable=C0115
class RoomManagerSyncI(IceGauntlet.RoomManagerSync):
    # pylint: disable=C0103
    def __init__(self, syncChannelPrx, roomManager, roomManagerPrx):
        # pylint: disable=C0103
        self.syncChannelPrx = syncChannelPrx
        # pylint: disable=C0103
        self.roomManager = roomManager
        # pylint: disable=C0103
        self.clientRoomManagerPrx = roomManagerPrx
        # pylint: disable=C0103
        self.roomsProxies = {}

    # pylint: disable=C0116
    def start(self):
        self.createClient().hello(self.clientRoomManagerPrx, self.roomManager.id)

    # pylint: disable=C0116
    # pylint: disable=W0613
    def hello(self, newRoom, idRoom, current=None):
        self.roomsProxies[idRoom] = newRoom
        #print(self.roomManager.id + ' :'+idRoom)
        #print(self.roomManager.id + ' :{}'.format(self.roomsProxies))
        if idRoom != self.roomManager.id:
            print(self.roomManager.id + ' :hello: '+idRoom)
            self.createClient().announce(self.clientRoomManagerPrx, self.roomManager.id)
        #print(self.roomManager.id + ' : hello => ' + idRoom)
        #print(self.roomsProxies)

    # pylint: disable=C0116
    # pylint: disable=C0116
    def createClient(self):
        return IceGauntlet.RoomManagerSyncPrx.uncheckedCast(self.syncChannelPrx.getPublisher())

    # pylint: disable=C0116
    # pylint: disable=C0103
    # pylint: disable=W0613
    def announce(self, newRoom, idRoom, current=None):
        if not idRoom in self.roomsProxies:
            self.roomsProxies[idRoom] = newRoom
            if self.roomManager.id == idRoom:
                return
            print(self.roomManager.id + ' : announce a => ' + idRoom)
            #print(self.roomManager.id + ' : announce b => {}'.format(self.roomsProxies))
            if idRoom != self.roomManager.id:
                try:
                    # pylint: disable=C0301
                    strRoomsOfManager = IceGauntlet.RoomManagerPrx.checkedCast(self.roomsProxies[idRoom]).availableRooms()
                except:
                    # pylint: disable=C0103
                    strRoomsOfManager = []
                # pylint: disable=C0301
                print(self.roomManager.id + ' : recibe las habitaciones de  ' + idRoom + '\n {}'.format(strRoomsOfManager))
                if len(strRoomsOfManager) > 0:
                    # pylint: disable=C0103
                    for mapaStored in strRoomsOfManager:
                        if not self.existMap(mapaStored):
                            # pylint: disable=C0301
                            item = {"room": mapaStored, "data": json.loads(self.roomsProxies[idRoom].getRoom(mapaStored))}
                            self.roomManager.maps.append(item)

                #print(self.roomManager.id + ' : announce')
                self.printMaps()

    # pylint: disable=W0613
    # pylint: disable=C0103
    def existMap(self, mapaStored, current=None):
        # pylint: disable=W0622
        for map in self.roomManager.maps:
            if map['room'] == mapaStored:
                return True
        return False

    # pylint: disable=C0103
    # pylint: disable=W0613
    def newRoom(self, roomName, idRoomManager, current=None):
        # pylint: disable=C0103
        strRoomsOfManager = self.roomsProxies[idRoomManager].availableRooms()
        # pylint: disable=C0103
        for mapRoom in strRoomsOfManager:
            if mapRoom == roomName:
                available = False
                for mapaStored in self.roomManager.maps:
                    if mapRoom == mapaStored['room']:
                        available = True
                if not available:
                    # pylint: disable=C0301
                    item = {"room": mapRoom, "data": json.loads(self.roomsProxies[idRoomManager].getRoom(mapRoom))}
                    self.roomManager.maps.append(item)
        print(self.roomManager.id + ' : newRoom')
        self.printMaps()

    # pylint: disable=C0103
    # pylint: disable=W0613
    def removedRoom(self, roomName, current=None):
        # pylint: disable=C0103
        for mapRoom in self.roomManager.maps:
            if mapRoom['room'] == roomName:
                self.roomManager.maps.remove(mapRoom)
        print(self.roomManager.id + ' : removedRoom')
        self.printMaps()

    # pylint: disable=C0103
    def printMaps(self):
        # pylint: disable=W0622
        for map in self.roomManager.maps:
            print(map['room'])
        print('\n')

# pylint: disable=C0115
class RoomManagerI(IceGauntlet.RoomManager):
    # pylint: disable=C0103
    def __init__(self, auth_server, id):
        # pylint: disable=C0103
        # pylint: disable=W0622
        self.id = id
        # pylint: disable=C0103
        self.roomManagerSync = None
        self.maps = []
        self.auth_server = auth_server

    # pylint: disable=W0613
    # pylint: disable=C0103
    # pylint: disable=C0116
    def availableRooms(self, current=None):
        ##print(self.id+' availableRooms')
        maps_string = []
        if len(self.maps) > 0:
            # pylint: disable=W0622
            for map in self.maps:
                maps_string.append(map['room'])

        print(self.id+' AVAILABLE ROOMS:\n{} '.format(maps_string))
        return maps_string

    # pylint: disable=W0613
    # pylint: disable=C0103
    # pylint: disable=C0116
    def getRoom(self, name, current=None):
        # pylint: disable=W0622
        for map in self.maps:
            if map['room'] == name:
                return json.dumps(map['data'])
        raise IceGauntlet.RoomNotExists()

    # pylint: disable=C0116
    # pylint: disable=W0613
    def publish(self, tkn, room_json, current=None):
        json_map = json.loads(room_json)
        if self.check(json_map):
            try:
                # pylint: disable=W0612
                usuario = self.auth_server.getOwner(tkn)

            except IceGauntlet.Unauthorized:
                #print("No se ha recuperado ningun token")
                # pylint: disable=W0707
                raise IceGauntlet.Unauthorized()

            # pylint: disable=R1720
            if json_map in self.maps:
                raise IceGauntlet.RoomAlreadyExists()
            else:
                self.maps.append(json_map)  # Lo metemos en la lista
                self.syncServers(True, json_map['room'])

        else:
            raise IceGauntlet.WrongRoomFormat()

    # pylint: disable=C0103
    # pylint: disable=C0116
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
            # pylint: disable=W0612
            usuario = self.auth_server.getOwner(tkn)
        except IceGauntlet.Unauthorized:
            #print("No se ha recuperado ningun token")
            # pylint: disable=W0707
            raise IceGauntlet.Unauthorized()

        if self.exist(room_name):
            # pylint: disable=W0622
            for map in self.maps:
                if map['room'] == room_name:
                    self.maps.remove(map)
                    self.syncServers(False, room_name)

                i += 1
        else:
            raise IceGauntlet.RoomNotExists()


    def exist(self, room_name):
        encontrado = False
        # pylint: disable=W0622
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
    # pylint: disable=C0103
    # pylint: disable=C0116
    def getRoom(self, current=None):
        if len(self.maps) == 0:
            raise IceGauntlet.RoomNotExists
        return json.dumps(self.maps)


# Vamos a crear un servidor con dos sirvientes, para el de mapas y para el de juego
# pylint: disable=C0115
class Server(Ice.Application):
    def run(self, args):

        logging.debug('Initializing server...')

        # pylint: disable=C0103
        propertyAuthorization = self.communicator().propertyToProxy("authorization")
        authorizationProxy = IceGauntlet.AuthenticationPrx.checkedCast(propertyAuthorization)
        # pylint: disable=C0301
        # Proxy del servicio de mapas
        #prx_auth = IceGauntlet.AuthenticationPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))

        # pylint: disable=C0103
        roomManager = RoomManagerI(authorizationProxy, uuid.uuid4().hex)
        adapter = self.communicator().createObjectAdapter("RoomManagerAdapter")
        # pylint: disable=C0103
        identityRoomManager = self.communicator().stringToIdentity(self.communicator().getProperties().getProperty('proxyIndex'))
        roomManagerPrx = adapter.add(roomManager, identityRoomManager)
        adapter.addDefaultServant(roomManager, '')

        # Ice Storm
        # pylint: disable=C0103
        proxyIceBox = self.communicator().stringToProxy('Multijugador_SSDD.IceStorm/TopicManager')
        if proxyIceBox is None:
            #print("Invalid topic proxy")
            return 2

        # pylint: disable=C0103
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
        # pylint: disable=C0301
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

        # pylint: disable=W1202
        logging.debug('Adapter ready, servant proxy: {}'.format(roomManagerPrx))
        print(roomManager.id + ' "{}"'.format(roomManagerPrx), flush=True)

        logging.debug('Entering server loop...')
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


if __name__ == '__main__':
    app = Server()
    sys.exit(app.main(sys.argv))
