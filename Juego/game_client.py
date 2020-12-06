#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=W1203

'''
    ICE Gauntlet DISTRIB GAME
'''

import sys
import atexit
import argparse
import Ice
# pylint: disable=E0401
# pylint: disable=C0413
Ice.loadSlice('../Implementación_Multijugador/icegauntlet.ice')
import IceGauntlet
import game
import game.common
import game.screens
import game.pyxeltools
import game.orchestration
from Remote.RemoteDungeon import RemoteDungeon

EXIT_OK = 0
BAD_COMMAND_LINE = 1

DEFAULT_HERO = game.common.HEROES[0]

@atexit.register
# pylint: disable=W0613
def bye(*args, **kwargs):
    '''Exit callback, use for shoutdown'''
    print('Thanks for playing!')


# pylint: enable=W0613

def parse_commandline():
    '''Parse and check commandline'''
    parser = argparse.ArgumentParser('IceDungeon Remote Game')
    parser.add_argument('PROXY', help='List of levels', type=str)
    parser.add_argument(
        '-p', '--player', default=DEFAULT_HERO, choices=game.common.HEROES,
        dest='hero', help='Hero to play with'
    )
    options = parser.parse_args()
    return options


def main():
    '''Start game according to commandline'''
    user_options = parse_commandline()
    if not user_options:
        return BAD_COMMAND_LINE

    game.pyxeltools.initialize()
    communicator = Ice.initialize(sys.argv)
    game_ = IceGauntlet.DungeonPrx.checkedCast(communicator.stringToProxy(user_options.PROXY))
    try:
        dungeon = RemoteDungeon(game_)
    except IceGauntlet.RoomNotExists:
        print("ERROR. No hay mapas subidos para jugar.")
        sys.exit(1)
    gauntlet = game.Game(user_options.hero, dungeon)
    gauntlet.add_state(game.screens.TileScreen, game.common.INITIAL_SCREEN)
    gauntlet.add_state(game.screens.StatsScreen, game.common.STATUS_SCREEN)
    gauntlet.add_state(game.screens.GameScreen, game.common.GAME_SCREEN)
    gauntlet.add_state(game.screens.GameOverScreen, game.common.GAME_OVER_SCREEN)
    gauntlet.add_state(game.screens.GoodEndScreen, game.common.GOOD_END_SCREEN)
    gauntlet.start()

    return EXIT_OK


if __name__ == '__main__':
    sys.exit(main())
