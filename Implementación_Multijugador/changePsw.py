#!/usr/bin/env python

import Ice
import hashlib
import sys
from getpass import getpass
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

#Recibiremos por parámetro un proxy, y pediremos usuario y contraseña por teclado

if len(sys.argv) < 2:
    print("Introduce el proxy por parámetro.")
    sys.exit(0)  

with Ice.initialize(sys.argv) as communicator:
    proxy_auth = IceGauntlet.AuthenticationPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))

    print("Introduce tu nombre de usuario:")
    usuario = input()  #Existe el usuario?

    print("Introduce la antigua contraseña:")
    psw_antigua = getpass()
    psw_antigua = hashlib.sha256(psw_antigua.encode()).hexdigest()

    print("Introduce la contraseña nueva")
    psw_nueva = getpass()
    psw_nueva = hashlib.sha256(psw_nueva.encode()).hexdigest()
    
    try:
        proxy_auth.changePassword(str(usuario), psw_antigua, psw_nueva)
        print("La contraseña se ha cambiado con éxito.")
    except IceGauntlet.Unauthorized:
        print("ERROR. Usuario o contraseña incorrectos.")
