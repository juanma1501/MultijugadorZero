#!/usr/bin/env python

import sys
import Ice

Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

if len(sys.argv) < 4:
    print("Introduzca todos los argumentos. <proxy> <token> <nombre_del_mapa>")

with Ice.initialize(sys.argv) as communicator:
    try:
        proxy_maps_server = IceGauntlet.RoomManagerPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))
    except Ice.NoEndpointException:
        print("ERROR. No se pudo leer el proxy. ¿Es correcto?")
        sys.exit(0)
    except Ice.ConnectionRefusedException:
        print("ERROR. No se pudo leer el proxy. ¿Es correcto?")
        sys.exit(0)
    except Ice.EndpointParseException:
        print("ERROR. No se pudo leer el proxy. ¿Es correcto?")
        sys.exit(0)

    try:
        proxy_maps_server.remove(sys.argv[2], sys.argv[3])
    except IceGauntlet.Unauthorized:
        print("El token introducido es incorrecto.")
        sys.exit(0)
    except IceGauntlet.RoomNotExists:
        print("El mapa que intentas borrar no existe.")
        sys.exit(0)

    print('El mapa se ha borrado con éxito.')
