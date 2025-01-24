# class that outputs station names
#
# the seed that generates the name is the floor of a user's seed (an integer) (provided when the
# object is initialised) minus n, then divided by n. It is intended that n is the number of stations
# + 1, but any number greater than 0 will work. This might make repetitions easily if the user's
# seed is short, therefore when the object is initialised, if the user's seed is < 12 digits long,
# it is concatenated until it is at least 12 digits long
#
# Names are made of four parts: [Prefix] [Former][latter] [Suffix]
# For example, if the prefix is "north", the former is "ac", the latter is "ton", and the suffix is
# "bridge", the full name will be "North Acton Bridge".
#
# The name must have:
# - a former
# - a latter or suffix or both
# The name may optionally have:
# - a prefix
#
# default weightings of chances of each occurring are set when the object is initialised, but these
# can be changed via method call. If weightings do not sum to 1, they will be normalised so that
# they do.

import random as rd
import os


class StationNameGenerator:
    def __init__(self, user_seed: int, list_paths: dict[str, str]):
        """
        :param user_seed: The global seed provided by the software user. If it is less than 12
        digits long, it is concatenated until it is at least 12 digits long.
        :param list_paths: A dictionary of filepaths containing name parts. Must contain the keys
        "prefix", "former", "latter", "suffix". All other keys are ignored.
        """
        # check arguments
        python_path = os.environ['PYTHONPATH'].split(os.pathsep)
        path_keys = [*list_paths]
        required_keys = ["prefix", "former", "latter", "suffix"]
        if not all([i in path_keys for i in required_keys]):
            raise ValueError("The dictionary of filepaths of part lists for a StationNameGenerator " +
                           "have keys including 'prefix', 'former', 'latter', and 'suffix'.")
        self.name_parts = {}
        for i in required_keys:
            new_name_list = []
            try:
                with open(list_paths[i], "r") as f:
                    for fline in f:
                        new_name_list.append(fline)
            except OSError:
                raise ValueError("The name parts list file with the key '" + i + "' was not a " +
                                 "valid file.")
            self.name_parts[i] = new_name_list

        # make user seed at least 12 digits long
        seed_checked = False
        long_seed = user_seed
        while not seed_checked:
            if long_seed > 99999999999:
                seed_checked = True
            else:
                long_seed = int(str(long_seed) + str(long_seed))
        self.userseed = long_seed

        # set default name shape weightings
        self.nameshape_weights_prefix = [
            0.8,  # no prefix
            0.2  # yes prefix
        ]
        self.nameshape_weights_latter_suffix = [
            0.8,  # just latter
            0.15,  # latter + suffix
            0.05  # just suffix
        ]