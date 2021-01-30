# pylint: disable=C0103
#!/usr/bin/env python
'''
Clase changePsw.py
'''

import hashlib
import sys
from getpass import getpass
import Ice

Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

# pylint: disable=C0116
def main():
    # Recibiremos por parámetro un proxy, y pediremos usuario y contraseña por teclado
    if len(sys.argv) < 2:
        print("Introduce el proxy por parámetro.")
        sys.exit(1)

    with Ice.initialize(sys.argv) as communicator:
        # pylint: disable=C0301
        proxy_auth = IceGauntlet.AuthenticationPrx.checkedCast(communicator.stringToProxy(sys.argv[1]))

        print("Introduce tu nombre de usuario:")
        usuario = input()  # Existe el usuario?

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


if __name__ == '__main__':
    sys.exit(main())
