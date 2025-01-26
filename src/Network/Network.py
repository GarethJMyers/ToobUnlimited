# a network is a graph where stations are the nodes, connected with edges. Edges that all have the
# same property are the tube lines between stations.
#
# There are three ways of adding stations to the graph:
# 1) Disconnected Stations
#    Generate n stations with no edges between them. It is intended for this to be carried out
#    when the network is created but not afterwards.
# 2) New Line
#    Generate a new NetworkLine object, then generate n new stations that are on that line. This
#    new NetworkLine object will not initially connect any pre-existing stations, those connections
#    must be added afterwards.
# 3) Extend Line
#    Defining the NetworkLine and the NetworkStation to start from, extend the line by adding n new
#    stations. The starting NetworkStation does not necessarily need to be at the end of a line.
#    Other than the starting station, these new stations will not initially connect any pre-existing
#    stations, those connections must be added afterwards.
#
# The class variables are:
# all of the class variables that are inherited from the parent networkx.Graph class, of course
# .station_names: a list of station names within the network
# .line_names: a list of line names within the network
# .line_objects: a list of NetworkLine objects used as edges in the network
# .user_seed: The seed supplied by the user, used for random generation
# .sn_gen: The StationNameGenerator object used to generate new station names
# .start_range: The number of disconnected stations that should be generated when stations are
#               first genenrated.

import networkx as nx
import typing as ty
from src.Network.NetworkStation import NetworkStation
from src.Network.NetworkLine import NetworkLine
from src.Naming.StationNameGenerator import StationNameGenerator


class Network(nx.Graph):
    def __init__(self,user_seed: int,name_part_paths: dict[str, str],num_start_range: ty.Optional[tuple[int, int]]):
        """
        abc
        :param user_seed: the seed set by the user to be used for RNG
        :param name_part_paths: a dictionary of file paths for the lists of possible parts of
        station names. See the comments in /src/Naming/StationNameGenerator.py for more info.
        :param num_start_range: a tuple of the range of possible starting numbers of stations
        before any lines connect them. Optional, defaults to None. If None, then the default
        numbers of (20, 40) are used.
         """
        super().__init__()
        self.station_names = []
        self.line_names = []
        self.line_objects = []
        self.user_seed = user_seed
        self.sn_gen = StationNameGenerator(
            user_seed=user_seed,
            list_paths=name_part_paths
        )
        if num_start_range is None:
            self.start_range = (20, 40)
        else:
            self.start_range = num_start_range

    def _generate_station_names(self, num_names: int) -> list[str]:
        """
        Given a number of station names to generate, genenrate that many station names that are
        unique. This is done by making sure none of the generated names appear in self.station_names.
        The seed used is the user_seed modified with the number of stations in the network plus 1.
        The plus 1 is to make sure n is always > 0, as an n of 0 causes a /0 error. See the
        comments in /src/Naming/StationNameGenerator.py for more info.
        :param num_names: The number of new names to generate.
        :return: a list of unique station names.
        """
        generated_names = self.sn_gen.generate_names(
            n=len(self.station_names) + 1,
            num_names=num_names
        )

        # check which new names are repeats of earlier new names in the list. The chances of this
        # happening are infintessimally small, but check anyway.
        intra_repeats = [generated_names[i] in generated_names[:i] for i in range(num_names)]
        # check which new names are repeats of pre-existing stations. Still very, very unlikely,
        # but check anyway.
        inter_repeats = [i in self.station_names for i in generated_names]
        repeats = [i or j for i, j in zip(intra_repeats, inter_repeats)]

        # if no repeats exist, then the newly generated names are all fine to use
        if not any(repeats):
            return generated_names

        # however, if there are repeats, then new names will need to be generated
        num_new_required = repeats.count(True)
        new_names = self._generate_station_names(num_names=num_new_required)
        new_name_index = 0
        names_to_return = []
        for i in len(generated_names):
            if repeats[i]:
                names_to_return.append(new_names[new_name_index])
                new_name_index += 1
            else:
                names_to_return.append(generated_names[i])
        return names_to_return

    def generate_disconnected_stations(self, num_stations):
        new_names = self._generate_station_names(num_stations)
        for i in new_names:
            new_station = NetworkStation(i)
            self.add_node(new_station)
