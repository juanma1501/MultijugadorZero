#!/usr/bin/env python
import Ice
import sys
import hashlib
from getpass import getpass
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

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

    user = input("Introduce tu nombre de usuario: ")

    password = getpass()
    password = hashlib.sha256(password.encode()).hexdigest()


    try:
        tkn = auth.getNewToken(user, password)
    except IceGauntlet.Unauthorized:
        print("El usuario o la contraseña introducidos son incorrectos.")
        sys.exit(1)

    print("El token es : " + str(tkn))
