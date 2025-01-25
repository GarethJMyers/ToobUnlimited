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
# If the last letter of the former and the first letter of the latter are identical, there is also
# the probability that the last letter of the former is deleted so that the letter no longer repeats.
# This probability is 100 % if that letter is "a", "h", "i", "j", "q", "u", "v", "w", "x", or "y", as
# such double letters do not appear in British English.
#
# default weightings of chances of each occurring are set when the object is initialised, but these
# can be changed via method call. If weightings do not sum to 1, they will be normalised so that
# they do.

import random as rd
import typing as ty
import src.utils


def _construct_station_name(prefix: ty.Optional[str], former: str, latter: ty.Optional[str],
                             suffix: ty.Optional[str]) -> str:
    """
    Given the parts of a station name, combine them into a station name, including capitalisation.
    Has the form [Prefix] [Former][latter] [Suffix]
    :param prefix: The prefix, if not to be included should be None. Defaults to None.
    :param former: The former, must be included.
    :param latter: The latter, if not to be included should be None. Defaults to None.
    :param suffix: The suffix, if not to be included should be None. Defaults to None.
    :return: The station name as a string.
    """
    return_str = ""
    if prefix is not None:
        return_str += prefix.capitalize() + " "
    return_str += former.capitalize()
    if latter is not None:
        return_str += latter
    if suffix is not None:
        return_str += " " + suffix.capitalize()
    return return_str


class StationNameGenerator:
    def __init__(self, user_seed: int, list_paths: dict[str, str]):
        """
        :param user_seed: The global seed provided by the software user. If it is less than 12
        digits long, it is concatenated until it is at least 12 digits long.
        :param list_paths: A dictionary of filepaths containing name parts. Must contain the keys
        "prefix", "former", "latter", "suffix". All other keys are ignored.
        """
        # check arguments
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
                        new_name_list.append(fline.split("\n"))
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
        self.nameshape_weights_prefix = (
            0.8,  # no prefix
            0.2  # yes prefix
        )
        self.nameshape_weights_latter_suffix = (
            0.8,  # just latter
            0.15,  # latter + suffix
            0.05  # just suffix
        )
        self.nameshape_weights_double_letter = (
            0.5, # yes double letter allowed
            0.5 # no double letter allowed
        )

    def update_weights(
            self,
            prefix_weights: ty.Optional[tuple[float, float]],
            latter_weights: ty.Optional[tuple[float, float, float]],
            double_weights: ty.Optional[tuple[float, float]]
    ):
        """
        Manually set the weights of the random choices of name shapes. If the weights that are tuples
        do not sum to 1, then they are normalised so that they do.
        :param prefix_weights: Either None for weights not being updated, or a new two-long tuple of
        floats. Element 0 is the weight of no prefix, element 1 is the weight of a prefix. Defaults
        to None.
        :param latter_weights: Either None for weights not being updated, or a new three-long tuple
        of floats. Element 0 is the weight of just a latter, element 1 is the weight of a latter and
        a suffix, and element 2 is the weight of just a suffix. Defaults to None.
        :param double_weights: Either None for weights not being updated, or a new two-long tuple of
        floats. Element 0 is the weight of double letters being allowed, element 1 is the weight of
        double letters not being allowed. Defaults to None.
        """
        if prefix_weights is not None:
            prefix_sum = sum(list(prefix_weights))
            self.nameshape_weights_prefix = tuple([i / prefix_sum for i in prefix_weights])
        if latter_weights is not None:
            latter_sum = sum(list(latter_weights))
            self.nameshape_weights_latter_suffix = tuple([i / latter_sum for i in latter_weights])
        if double_weights is not None:
            double_sum = sum(list(double_weights))
            self.nameshape_weights_latter_suffix = tuple([i / double_sum for i in double_weights])

    def generate_names(self, n: int, num_names: int) -> list[str]:
        """
        Given a secondary seed, produce a list of new names generated using a new seed generated
        from the user seed and n. n cannot be 0 as it will cause a divide-by-zero error.
        :param n: value to modify the user seed with to create a new seed, from which the station
        name is generated.
        :param num_names: the number of names to generate.
        :return: the generated station name as a string.
        """
        newseed = src.utils.new_seed(
            primary_seed=self.userseed,
            secondary_seed=n
        )
        rngenerator = rd.Random(newseed)
        use_prefix = rngenerator.choices(
            population=[False, True],
            weights=self.nameshape_weights_prefix,
            k=num_names
        )
        use_latter_suffix = rngenerator.choices(
            population=[
                "just_latter",
                "both",
                "just_suffix"
            ],
            weights=self.nameshape_weights_latter_suffix,
            k=num_names
        )
        use_double_letters = rngenerator.choices(
            population=[True, False],
            weights=self.nameshape_weights_double_letter,
            k=num_names
        )

        prefixes = []
        formers = [
            i[0] for i in rngenerator.choices(
            population=self.name_parts["former"],
            k=num_names
        )
        ]
        latters = []
        suffixes = []
        former_num = 0
        for i, j, k in zip(use_prefix, use_latter_suffix, use_double_letters):
            if i:
                prefixes.append(
                    rngenerator.choice(self.name_parts["prefix"])[0]
                )
            else:
                prefixes.append(None)

            match j:
                case "just_latter":
                    use_latter = True
                    use_suffix = False
                case "just_suffix":
                    use_latter = False
                    use_suffix = True
                case "both":
                    use_latter = True
                    use_suffix = True
                case _:
                    raise ValueError("use_latter_suffix was not one of the three values it " +
                                     "should be?!?")

            if use_latter:
                chosen_latter = rngenerator.choice(self.name_parts["latter"])[0]
                if (not k) and (chosen_latter[0] == formers[former_num][-1]):
                    latters.append(chosen_latter[1:-1])
                else:
                    latters.append(chosen_latter)
            else:
                latters.append(None)
            if use_suffix:
                suffixes.append(
                    rngenerator.choice(self.name_parts["suffix"])[0]
                )
            else:
                suffixes.append(None)
            former_num += 1

        return [
            _construct_station_name(i, j, k, m) for i, j, k, m in zip(
                prefixes,
                formers,
                latters,
                suffixes
            )
        ]
