# The super class for Network and NetworkLine. Network contains NetworkLine objects, and NetworkLine
# contains NetworkStation objects. This class may contain objects and may be contained by one or
# more obejcts.

import weakref as wr


class NetworkContainerSuper:
    def __init__(self, name: str):
        self.name = name
        self.contents = []
        self.containers = []

    def __contains__(self, item):
        return item in self.contents

    def add_content(self, new_content):
        self.contents.append(wr.ref(new_content))

    def add_container(self, new_container):
        self.containers.append(wr.ref(new_container))
