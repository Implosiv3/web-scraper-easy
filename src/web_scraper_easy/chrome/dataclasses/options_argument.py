from dataclasses import dataclass


@dataclass(slots = True)
class _ChromeOptionsArgument:
    """
    *For internal use only*

    Chrome options arguments to control it, that
    must be added to the chrome driver `Options`
    property to work like below:

    ```
    option_arguments.append('--ignore-certificate-errors')
    option_arguments.append('--ignore-ssl-errors')
    option_arguments.append('--ignore-certificate-errors-spki-list')

    for argument in option_arguments:
        options.add_argument(argument)
    ```
    """

    value: str
    """
    The value of the options argument.
    """


class WindowSizeChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to set the size of 
    the window.

    The `value` of the option:
    - `window-size={width},{height}`
    """

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080
    ):
        super().__init__(
            value = f'window-size={str(width)},{str(height)}'
        )


class HeadlessChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to set the instance
    headless.

    The `value` of the option:
    - `--headless=new`
    """

    def __init__(
        self
    ):
        super().__init__(
            value = '--headless=new'
        )


class NoSandboxChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument recommended to be
    applied when in a container.

    The `value` of the option:
    - `--no-sandbox`
    """

    def __init__(
        self
    ):
        super().__init__(
            value = '--no-sandbox'
        )


class DisableDevShmUsageChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument recommended to be
    applied when in a container.

    The `value` of the option:
    - `--disable-dev-shm-usage`
    """

    def __init__(
        self
    ):
        super().__init__(
            value = '--disable-dev-shm-usage'
        )


class LoadExtensionChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to set an extension
    that must be loaded when the driver instance
    is initiated.

    The `value` of the option:
    - `load-extension={extension_abspath}`
    """

    def __init__(
        self,
        extension_abspath: str
    ):
        super().__init__(
            value = f'load-extension={extension_abspath}'
        )


class LoadChromeUserProfileChromeOptionArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to set a chrome user
    profile to be used within the driver instance.

    The `value` of the option:
    - `user-data-dir={chrome_user_profile_abspath}`
    """

    # A valid example:
    # - `user-data-dir=C:/Users/dania/AppData/Local/Google/Chrome/User Data/Profile 2`

    def __init__(
        self,
        chrome_user_profile_abspath: str
    ):
        super().__init__(
            value = f'user-data-dir={chrome_user_profile_abspath}'
        )


class IgnoreCertificateErrorsChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to ignore the
    certificate errors.
    
    The `value` of the option:
    - `--ignore-certificate-errors`
    """

    def __init__(
        self
    ):
        super().__init__(
            value = '--ignore-certificate-errors'
        )


class IgnoreSslErrorsChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to ignore the SSL
    errors.

    The `value` of the option:
    - `--ignore-ssl-errors`
    """

    def __init__(
        self
    ):
        super().__init__(
            value = '--ignore-ssl-errors'
        )


class IgnoreCertificateErrorsSpkiListChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to ignore the
    certificate errors (spki list).

    The `value` of the option:
    - `--ignore-certificate-errors-spki-list`
    """

    def __init__(
        self
    ):
        super().__init__(
            value = '--ignore-certificate-errors-spki-list'
        )


class StartMaximizedChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to start the driver
    with the window maximized.

    The `value` of the option:
    - `--start-maximized`
    """

    def __init__(
        self
    ):
        super().__init__(
            value = '--start-maximized'
        )

class MuteAudioChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to mute the audio
    and avoid id (this is necessary even when
    using not the GUI).

    The `value` of the option:
    - `--mute-audio`
    """

    def __init__(
        self
    ):
        super().__init__(
            value = '--mute-audio'
        )


class CustomChromeOptionsArgument(
    _ChromeOptionsArgument
):
    """
    Chrome options argument to start the driver
    with the consequence of it.

    The use of this one should be limited and the
    one we want to use should be added as a specific
    class here.

    The `value` of the option:
    - `{value}`
    """

    def __init__(
        self,
        value: any
    ):
        super().__init__(
            value = value
        )

# TODO: Keep adding options