import math
import pathlib as pl


def project_root() -> pl.Path:
    return pl.Path(__file__).parent.parent


def new_seed(primary_seed: int, secondary_seed: int) -> int:
    """
    Given a primary seed that should not change and a secondary seed that should, return a new seed
    that uses both.
    """
    if secondary_seed == 0:
        raise ValueError("Cannot create a new seed with a secondary seed of 0, as it will cause a" +
                         " divide-by-zero error.")
    return int(math.floor((float(primary_seed) - float(secondary_seed)) / float(secondary_seed)))
