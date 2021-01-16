#!/bin/sh

mkdir -p /tmp/db/registry
mkdir -p /tmp/db/node1
mkdir -p /tmp/db/node2
mkdir -p /tmp/db/Multijugador_SSDD
cp icegauntlet.ice /tmp/db/Multijugador_SSDD
cp auth_server /tmp/db/Multijugador_SSDD
cp maps_server.py /tmp/db/Multijugador_SSDD
cp -r /Loaded_Maps /tmp/db/Multijugador_SSDD
icepatch2calc /tmp/db/Multijugador_SSDD
icegridnode --Ice.Config=node1.config & icegridnode --Ice.Config=node2.config

