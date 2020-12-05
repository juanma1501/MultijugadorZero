#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=W1203

'''
    ICE Gauntlet DISTRIB GAME
'''

import sys
import atexit
import logging
import argparse
import Ice

Ice.loadSlice('../Implementación_Multijugador/icegauntlet.ice')
import IceGauntlet
import os
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
    parser.add_argument('PROXY', help='Proxy', type=str)
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


    if len(sys.argv) < 2:
        print('Command arguments: {} <proxy>'.format(
            os.path.basename(sys.argv[0]))
        )
        sys.exit(1)

    game.pyxeltools.initialize()
    communicator = Ice.initialize(sys.argv)
    maps_proxy = IceGauntlet.DungeonPrx.checkedCast(communicator.stringToProxy(user_options.PROXY))
    dungeon = RemoteDungeon(maps_proxy)
    gauntlet = game.Game(user_options, dungeon)
    gauntlet.add_state(game.screens.TileScreen, game.common.INITIAL_SCREEN)
    gauntlet.add_state(game.screens.StatsScreen, game.common.STATUS_SCREEN)
    gauntlet.add_state(game.screens.GameScreen, game.common.GAME_SCREEN)
    gauntlet.add_state(game.screens.GameOverScreen, game.common.GAME_OVER_SCREEN)
    gauntlet.add_state(game.screens.GoodEndScreen, game.common.GOOD_END_SCREEN)
    gauntlet.start()

    return EXIT_OK


if __name__ == '__main__':
    sys.exit(main())