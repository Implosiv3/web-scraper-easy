from pystandards.enum import _BaseEnum, Enum


class ChromeOptionState(
    _BaseEnum,
    Enum
):
    """
    The state value of the option in Chrome.
    """

    ENABLED = 1
    """
    The option will be enabled by default in the web
    navigator.
    """
    DISABLED = 2
    """
    The option will be disabled by default in the web
    navigator.
    """