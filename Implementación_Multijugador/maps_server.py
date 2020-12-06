#!/usr/bin/env python
"""Clase maps_server"""

import sys
import logging
import json
import os
import Ice

Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

# pylint: disable=C0115
class RoomManagerI(IceGauntlet.RoomManager):
    def __init__(self, auth_server):
        self.maps = []
        self.load_maps()
        self.auth_server = auth_server

    # pylint: disable=W0613
    def publish(self, tkn, room_json, current=None):
        number = 0
        if self.auth_server.isValid(tkn):
            if json.loads(room_json) in self.maps:
                raise IceGauntlet.RoomAlreadyExists()
            else:
                self.maps.append(json.loads(room_json))  # Lo metemos en la lista
                # Lo incluimos en la carpeta Loaded_Maps
                # pylint: disable=W0612
                for i in os.listdir("./Loaded_Maps"):
                    number += 1
                with open('./Loaded_Maps/' + str(number) + '.json', 'w') as file:
                    json.dump(json.loads(room_json), file)
                print(self.maps)
        else:
            raise IceGauntlet.Unauthorized()

    # pylint: disable=W0613
    # pylint: disable=C0116
    def remove(self, tkn, room_name, current=None):
        i = 0
        if self.auth_server.isValid(tkn):
            if self.exist(room_name):
                for map in self.maps:
                    if map['room']:
                        if map['room'] == room_name:
                            self.maps.remove(map)
                            os.remove('./Loaded_Maps/' + str(i) + '.json')
                            self.rename()
                            print(self.maps)
                    else:
                        raise IceGauntlet.WrongRoomFormat()
                    i += 1
            else:
                raise IceGauntlet.RoomNotExists()
        else:
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
        with Ice.initialize(sys.argv) as communicator:
            logging.debug('Initializing server...')

            # Proxy del servicio de mapas
            prx_auth = IceGauntlet.AuthenticationPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))
            servant = RoomManagerI(prx_auth)

            adapter = communicator.createObjectAdapterWithEndpoints("RoomManagerAdapter",
                                                                    "default -h localhost -p 10001")
            proxy = adapter.add(servant, self.communicator().stringToIdentity('roommanager'))
            adapter.addDefaultServant(servant, '')
            adapter.activate()

            # Proxy del servicio de juego
            servant_game = DungeonI(servant.maps)
            adapter_game = communicator.createObjectAdapterWithEndpoints("DungeonAdapter",
                                                                         "default -h localhost -p 10002")
            proxy_game = adapter_game.add(servant_game, self.communicator().stringToIdentity('dungeon'))
            adapter_game.addDefaultServant(servant_game, '')
            adapter_game.activate()

            # Vamos a escribir el proxy de juego en el txt, ya que este servidor solo puede imprimir uno
            txt = open('proxy_juego', 'w')
            txt.write(str(proxy_game))
            txt.close()

            logging.debug('Adapter ready, servant proxy: {}'.format(proxy))
            print('"{}"'.format(proxy), flush=True)

            logging.debug('Entering server loop...')
            self.shutdownOnInterrupt()
            self.communicator().waitForShutdown()

            return 0


if __name__ == '__main__':
    app = Server()
    sys.exit(app.main(sys.argv))
