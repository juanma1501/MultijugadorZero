#!/usr/bin/env python

import sys
import Ice
import json
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

if len(sys.argv) < 4:
    print("Introduzca todos los argumentos. <proxy> <token> <nombre_archivo.json>")
    sys.exit(1)

with Ice.initialize(sys.argv) as communicator:
    with open('Maps/' + sys.argv[3]) as json_file:
        mapa = json.load(json_file)

    proxy_maps_server = IceGauntlet.RoomManagerPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))
    proxy_maps_server.publish(sys.argv[2], json.dumps(mapa))

    print("El mapa se ha subido con éxito.")