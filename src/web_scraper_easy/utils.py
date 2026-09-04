import random


def get_random(
    min_value: float = 0.0,
    max_value: float = 1.0
) -> float:
    """
    Get a random `float` number in between the
    `min_value` and the `max_value` provided.
    """
    return random.uniform(min_value, max_value)