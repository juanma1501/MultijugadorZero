#!/usr/bin/env python
"""Clase get_token"""

# pylint: disable=E1101
import sys
import hashlib
from getpass import getpass
import Ice

Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet


def main():
    if len(sys.argv) < 2:
        print("Hay que introducir el proxy")
        sys.exit(1)

    with Ice.initialize(sys.argv) as communicator:

        try:
            auth = IceGauntlet.AuthenticationPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))
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

        user = input("Introduce tu nombre de usuario: ")

        PASSWORD = getpass()
        PASSWORD = hashlib.sha256(PASSWORD.encode()).hexdigest()

        try:
            tkn = auth.getNewToken(user, PASSWORD)
        except IceGauntlet.Unauthorized:
            print("El usuario o la contraseña introducidos son incorrectos.")
            sys.exit(1)

        print("El token es : " + tkn)

        return 0


if __name__ == '__main__':
    sys.exit(main())
