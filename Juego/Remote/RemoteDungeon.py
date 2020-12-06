import json
import os

class RemoteDungeon:
    '''Store a list of rooms'''

    def __init__(self, game_proxy):
        self._levels_ = []
        self.game_proxy = game_proxy
        maps = json.loads(self.game_proxy.getRoom())
        for i in range(len(maps)):
            self._levels_.append(str(i) + '.json')
            with open('./assets/' + str(i) + '.json', 'w') as f:
                json.dump(maps[i], f)
        self._levels_.reverse()

    @property
    def next_room(self):
        if self._levels_:
            return self._levels_.pop()

    @property
    def finished(self):
        return not self._levels_
