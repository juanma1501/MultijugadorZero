import json

class RemoteDungeon:
    '''Store a list of rooms'''

    def __init__(self, maps_proxy):
        self.maps_proxy = maps_proxy
        rooms = json.loads(maps_proxy.getRoom())
        self._levels_ = []
        for i in range(len(rooms)):
            self._levels_.append('data' + str(i) + '.json')
            with open('../assets/' + str(i) + '.json', 'w') as f:
                json.dump(rooms[i], f)
        self._levels_.reverse()

    @property
    def next_room(self):
        if self._levels_:
            return self._levels_.pop()

    @property
    def finished(self):
        return not self._levels_
