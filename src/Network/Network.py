# the Network class contains all the information about a network of tube lines and stations

import weakref as wr
from NetworkContainerSuper import NetworkContainerSuper
from NetworkLine import NetworkLine


class Network(NetworkContainerSuper):
    def add_line(self, network_line: NetworkLine):
        
