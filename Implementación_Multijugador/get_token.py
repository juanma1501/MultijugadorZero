#!/usr/bin/env python

import Ice
import sys
import hashlib
from getpass import getpass
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

if len(sys.argv) < 2:
    print("Hay que introducir el proxy")


with Ice.initialize(sys.argv) as communicator:

    print("Introduce tu nombre de usuario: ")
    user = input()

    password = getpass()
    password = hashlib.sha224(password.encode()).hexdigest()

    auth = IceGauntlet.AuthenticationPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))

    tkn = auth.getNewToken(user, password)
    print("El token es : " + str(tkn))
