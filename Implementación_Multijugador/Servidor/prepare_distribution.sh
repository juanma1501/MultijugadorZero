#!/bin/sh
mkdir -p /tmp/db/Multijugador_SSDD
cp icegauntlet.ice /tmp/db/Multijugador_SSDD
cp auth_server /tmp/db/Multijugador_SSDD
cp maps_server.py /tmp/db/Multijugador_SSDD
cp users.json /tmp/db/Multijugador_SSDD
mkdir -p /tmp/db/registry
mkdir -p /tmp/db/node1
mkdir -p /tmp/db/node2
chmod 777 /tmp/db/Multijugador_SSDD/users.json
icepatch2calc /tmp/db/Multijugador_SSDD
icegridnode --Ice.Config=node1.config & icegridnode --Ice.Config=node2.config

