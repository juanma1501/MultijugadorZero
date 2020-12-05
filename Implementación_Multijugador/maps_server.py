#!/usr/bin/env python

import sys
import logging
import json
import Ice

Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class RoomManagerI(IceGauntlet.RoomManager):
    def __init__(self, auth_server):
        self.maps = []
        self.auth_server = auth_server

    def publish(self, tkn, room_json, current=None):
        if self.auth_server.isValid(tkn):
            if json.loads(room_json) in self.maps:
                raise IceGauntlet.RoomAlreadyExists()
            else:
                self.maps.append(json.loads(room_json))
                print(self.maps)
        else:
            raise IceGauntlet.Unauthorized()

    def remove(self, tkn, room_name, current=None):
        if self.auth_server.isValid(tkn):
            if self.exist(room_name):
                for map in self.maps:
                    if map['room'] and map['room'] == room_name:
                        self.maps.remove(map)
                        print(self.maps)
                    #wrong format exception
            else:
                raise IceGauntlet.RoomNotExists()
        else:
            raise IceGauntlet.Unauthorized()

    def getRoom(self, current=None):
        return json.dumps(self.maps)

    def exist(self, room_name):
        encontrado = False
        for map in self.maps:
            if map['room'] == room_name:
                encontrado = True
                return encontrado
        return encontrado

    def shutdown(self, current):
        current.adapter.getCommunicator().shutdown()

class Server(Ice.Application):
    def run(self, args):
        with Ice.initialize(sys.argv) as communicator:
            logging.debug('Initializing server...')
            prx_auth = IceGauntlet.AuthenticationPrx.checkedCast(
                communicator.stringToProxy("authentication -t -e 1.1:tcp -h localhost -p 10000 -t 60000"))
            servant = RoomManagerI(prx_auth)
            adapter = communicator.createObjectAdapterWithEndpoints("RoomManagerAdapter", "default -h localhost -p 10001")
            proxy = adapter.add(servant, self.communicator().stringToIdentity('roommanager'))
            adapter.addDefaultServant(servant, '')
            adapter.activate()
            logging.debug('Adapter ready, servant proxy: {}'.format(proxy))
            print('"{}"'.format(proxy), flush=True)

            logging.debug('Entering server loop...')
            self.shutdownOnInterrupt()
            self.communicator().waitForShutdown()

            return 0

if __name__ == '__main__':
    app = Server()
    sys.exit(app.main(sys.argv))
