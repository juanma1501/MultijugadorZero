#!/usr/bin/env python

import sys
import Ice

Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

if len(sys.argv) < 4:
    print("Introduzca todos los argumentos. <proxy> <token> <nombre_del_mapa>")

with Ice.initialize(sys.argv) as communicator:
    proxy_maps_server = IceGauntlet.RoomManagerPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))
    proxy_maps_server.remove(sys.argv[2], sys.argv[3])
    print('El mapa se ha borrado con éxito.')
