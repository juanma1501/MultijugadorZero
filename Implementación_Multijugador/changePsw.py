#!/usr/bin/env python

import hashlib
import sys
from getpass import getpass
import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

#Recibiremos por parámetro un proxy, y pediremos usuario y contraseña por teclado

if len(sys.argv) < 2:
    print("Introduce el proxy por parámetro.")
    sys.exit(1)

with Ice.initialize(sys.argv) as communicator:
    proxy_auth = IceGauntlet.AuthenticationPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))

    print("Introduce tu nombre de usuario:")
    usuario = input()  #Existe el usuario?

    print("Introduce la antigua contraseña:")
    PSW_ANTIGUA = getpass()
    PSW_ANTIGUA = hashlib.sha256(PSW_ANTIGUA.encode()).hexdigest()

    print("Introduce la contraseña nueva")
    PSW_NUEVA = getpass()
    PSW_NUEVA = hashlib.sha256(PSW_NUEVA.encode()).hexdigest()
    try:
        proxy_auth.changePassword(str(usuario), PSW_ANTIGUA, PSW_NUEVA)
        print("La contraseña se ha cambiado con éxito.")
    except IceGauntlet.Unauthorized:
        print("ERROR. Usuario o contraseña incorrectos.")
