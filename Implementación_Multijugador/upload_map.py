#!/usr/bin/env python
'''
Clase upload_map.py
'''

# pylint: disable=E1101
import sys
import json
import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

def main():
    if len(sys.argv) < 4:
        print("Introduzca todos los argumentos. <proxy> <token> <nombre_archivo.json>")
        sys.exit(1)

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
            with open(sys.argv[3]) as json_file:
                mapa = json.load(json_file)
        except FileNotFoundError:
            print("ERROR. No se pudo encontrar el archivo .json")
            sys.exit(1)

        try:
            proxy_maps_server.publish(sys.argv[2], json.dumps(mapa))
        except IceGauntlet.Unauthorized:
            print("El token introducido es incorrecto.")
            sys.exit(1)
        except IceGauntlet.RoomAlreadyExists:
            print("El mapa que intenta publicar ya existe.")
            sys.exit(1)
        except IceGauntlet.WrongRoomFormat:
            print("El formato del JSON no es valido, revisa los campos room y data")
            sys.exit(1)

        print("El mapa se ha subido con éxito.")

        return 0


if __name__ == '__main__':
    sys.exit(main())
