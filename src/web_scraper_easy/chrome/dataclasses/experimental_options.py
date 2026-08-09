from web_scraper_easy.chrome.enums import ChromeOptionState
from dataclasses import dataclass
from typing import Any


@dataclass(slots = True)
class _ChromeExperimentalOption:
    """
    *For internal use only*

    Chrome experimental option, that must be added
    to the chrome driver `Options` property to work
    like below:

    ```
    options.add_experimental_option('prefs', {
        'excludeSwitches': ['enable-automation', 'load-extension', 'disable-popup-blocking'],
        'profile.default_content_setting_values.automatic_downloads': 1,
        'profile.default_content_setting_values.media_stream_mic': 1,
        'profile.content_settings.exceptions.clipboard': 1
        # 'profile.content_settings.exceptions.clipboard': {
        #     f'{host},*': {
        #         'setting': 1
        #     }
        # }
    })
    ```
    """

    name: str
    """
    The name of the experimental option.
    """
    value: Any
    """
    The value of the experimental option.
    """


class ExcludeSwitchesChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to exclude switches.

    The option itself:
    - `excludeSwitches: switches`
    """

    def __init__(
        self,
        switches: list[str] = ['enable-automation', 'load-extension', 'disable-popup-blocking']
    ):
        super().__init__(
            name = 'excludeSwitches',
            value = switches
        )


class EnableDownloadsChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to enable the 
    downloads.

    The option itself:
    - `profile.default_content_setting_values.automatic_downloads: 1`
    """
    def __init__(
        self
    ):
        super().__init__(
            name = 'profile.default_content_setting_values.automatic_downloads',
            value = ChromeOptionState.ENABLED.value
        )


class EnableMicrophoneChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to enable the
    microphone.

    The option itself:
    - `profile.default_content_setting_values.media_stream_mic: 1`
    """
    def __init__(self):
        super().__init__(
            name = 'profile.default_content_setting_values.media_stream_mic',
            value = ChromeOptionState.ENABLED.value
        )


class EnableClipboardChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to enable the
    clipboard.

    The option itself:
    - `profile.content_settings.exceptions.clipboard: 1`
    """

    def __init__(
        self
    ):
        super().__init__(
            name = 'profile.content_settings.exceptions.clipboard',
            value = ChromeOptionState.ENABLED.value
        )


class SetDefaultDownloadDirectoryChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to set the default
    directory to store the downloads.

    This is the directory in which the Google Chrome
    navigator will store the downloads that are 
    downloaded directly without any prompt to choose
    the folder, because of a link (a) download, a
    http response with 'Content-Disposition', etc.

    This is very useful for a scraper like this.

    Please, make sure the `dir_abspath` provided is
    an absolute path (you can use `os.path.abspath()`)

    The option itself:
    - `download.default_directory: {dir_abspath}`
    """

    def __init__(
        self,
        dir_abspath: str
    ):
        super().__init__(
            name = 'download.default_directory',
            value = dir_abspath
        )

class SetDefaultSavefileDirectoryChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to set the default
    directory suggested when the 'Save as' dialog
    appears.

    This is the directory that will be suggested
    when the prompt to choose where to download a
    file is opened.

    This is not useful for a scraper like this.

    Please, make sure the `dir_abspath` provided is
    an absolute path (you can use `os.path.abspath()`)

    The option itself:
    - `savefile.default_directory: {dir_abspath}`
    """

    def __init__(
        self,
        dir_abspath: str
    ):
        super().__init__(
            name = 'savefile.default_directory',
            value = dir_abspath
        )


class PromptForDownloadChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to enable (or disable)
    the prompt dialog to choose where to save a
    download.

    When disabled, the download will be automatically
    stored in the directory defined in the 
    `download.default_directory` option (see the
    `SetDefaultDownloadDirectoryChromeExperimentalOption`
    class).

    This is interesting to have it disabled and use
    the `download.default_directory` instead.

    The option itself:
    - `download.prompt_for_download: False`
    """

    def __init__(
        self,
        is_enabled: bool = False
    ):
        super().__init__(
            name = 'download.prompt_for_download',
            value = is_enabled
        )


class DownloadDirectoryUpgradeChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to force the directory
    set in the `download.default_directory` as the
    directory to download the files, even if there is
    a previous configuration or there are changes
    related to it.

    The option itself:
    - `download.directory_upgrade: True`
    """

    def __init__(
        self,
        do_upgrade: bool = True
    ):
        super().__init__(
            name = 'download.directory_upgrade',
            value = do_upgrade
        )


class SafebrowsingEnabledChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to enable or disable
    some security checks that will intercept the
    downloads. Having it disabled could make the
    downloads to be blocked or work in an unexpected
    way.

    The option itself:
    - `safebrowsing.enabled: True`
    """

    def __init__(
        self,
        is_enabled: bool = True
    ):
        super().__init__(
            name = 'safebrowsing.enabled',
            value = is_enabled
        )


class CustomChromeExperimentalOption(
    _ChromeExperimentalOption
):
    """
    Chrome experimental option to enable something
    custom defined directly by the user.

    The use of this one should be limited and the
    one we want to use should be added as a specific
    class here.

    The option itself:
    - `{name}: {value}`
    """

    def __init__(
        self,
        name: str,
        value: any
    ):
        super().__init__(
            name = name,
            value = value
        )