#!/usr/bin/env python
'''
Clase remove_map.py
'''

# pylint: disable=E1101
import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

def main():
    if len(sys.argv) < 4:
        print("Introduzca todos los argumentos. <proxy> <token> <nombre_del_mapa>")

    with Ice.initialize(sys.argv) as communicator:
        try:
            # pylint: disable=C0301
            proxy_maps_server = IceGauntlet.RoomManagerPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))
        except Ice.NoEndpointException:
            print("ERROR. No se pudo leer el proxy. ¿Es correcto?")
            sys.exit(1)
        except Ice.ConnectionRefusedException:
            print("ERROR. No se pudo leer el proxy. ¿Es correcto?")
            sys.exit(1)
        except Ice.EndpointParseException:
            print("ERROR. No se pudo leer el proxy. ¿Es correcto?")
            sys.exit(1)
        except Ice.NotRegisteredException:
            print("ERROR. No se pudo leer el proxy. ¿Es correcto?")
            sys.exit(1)
          

        try:
            proxy_maps_server.remove(sys.argv[2], sys.argv[3])
        except IceGauntlet.Unauthorized:
            print("El token introducido es incorrecto.")
            sys.exit(1)
        except IceGauntlet.RoomNotExists:
            print("El mapa que intentas borrar no existe.")
            sys.exit(1)

        print('El mapa se ha borrado con éxito.')

        return 0


if __name__ == '__main__':
    sys.exit(main())
