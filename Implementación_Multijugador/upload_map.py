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

    try:
        proxy_maps_server = IceGauntlet.RoomManagerPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))
    except Ice.NoEndpointException:
        print("ERROR. No se pudo leer el proxy. ¿Es correcto?")
        sys.exit(0)
    try:
        proxy_maps_server.publish(sys.argv[2], json.dumps(mapa))
    except IceGauntlet.Unauthorized:
        print("El token introducido es incorrecto.")
        sys.exit(0)
    except IceGauntlet.WrongRoomFormat:
        print("El formato del JSON no es valido")

    print("El mapa se ha subido con éxito.")