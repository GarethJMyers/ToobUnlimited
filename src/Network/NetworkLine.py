# a NetworkLine object holds the properties of the edges between NetworkStation nodes in the
# Network graph. The properties are "name" and "colour". Colour is an RGB tuple of integers between
# 0 and 255.


class NetworkLine:
    def __init__(self, line_name: str, line_colour: tuple[int, int, int]):
        for i in line_colour:
            if not 0 <= i <= 255:
                raise ValueError("The RGB colour values for a NetworkLine must be between 0 and 255.")
        self.name = line_name
        self.colour = line_colour
