from web_scraper_easy.chrome.dataclasses.options_argument import HeadlessChromeOptionsArgument, LoadExtensionChromeOptionsArgument, _ChromeOptionsArgument, WindowSizeChromeOptionsArgument, IgnoreCertificateErrorsChromeOptionsArgument, IgnoreCertificateErrorsSpkiListChromeOptionsArgument, IgnoreSslErrorsChromeOptionsArgument, LoadChromeUserProfileChromeOptionArgument
from web_scraper_easy.chrome.dataclasses.experimental_options import ExcludeSwitchesChromeExperimentalOption, EnableDownloadsChromeExperimentalOption, EnableMicrophoneChromeExperimentalOption, EnableClipboardChromeExperimentalOption, _ChromeExperimentalOption
from web_scraper_easy.chrome.consts import TIMEOUT, TIME_INTERVAL
from web_scraper_easy.utils import get_random
from pystandards.regex.general import GeneralRegularExpression
from env_easy import getenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Union

import time
import warnings


"""
TODO: Is all this needed? Could we do
something to make it work without (?)
"""
CHROME_EXTENSIONS_ABSPATH = getenv('CHROME_EXTENSIONS_ABSPATH')
AD_BLOCK_ABSOLUTEPATH = getenv('AD_BLOCK_ABSOLUTEPATH')
CHROME_USER_DATA_ABSPATH = getenv('CHROME_USER_DATA_ABSPATH')

if not CHROME_EXTENSIONS_ABSPATH:
    warnings.warn('The "CHROME_EXTENSIONS_ABSPATH" environment variable is not defined.')
    # raise Exception('The "CHROME_EXTENSIONS_ABSPATH" environment variable is not defined.')

if not AD_BLOCK_ABSOLUTEPATH:
    warnings.warn('The "AD_BLOCK_ABSOLUTEPATH" environment variable is not defined.')
    # raise Exception('The "AD_BLOCK_ABSOLUTEPATH" environment variable is not defined.')

if not CHROME_USER_DATA_ABSPATH:
    warnings.warn('The "CHROME_USER_DATA_ABSPATH" environment variable is not defined.')
    # raise Exception('The "CHROME_USER_DATA_ABSPATH" environment variable is not defined.')


class ChromeScraper:
    """
    A class that wraps and simplify the functionality of
    the Google Chrome scrapper, useful to interact with
    websites and navigate through them interacting with
    their elements being able to perform complex actions
    such as downloading files, sending forms, etc.

    Use it like this:
    ```
    chrome = ChromeScraper.init(
        additional_options = [
            StartMaximizedChromeOptionsArgument
        ]
    )
    ```
    """


    @property
    def active_element(
        self
    ) -> Union[WebElement, None]:
        """
        Get the current active element by running the
        'driver.switch_to.active_element' command.
        """
        return (
            self.driver.switch_to.active_element
            if self.driver is not None else
            None
        )
    

    @property
    def current_url(
        self
    ) -> Union[str, None]:
        """
        Get the current url in which the scraper is
        located.
        """
        return (
            self.driver.current_url
            if self.driver is not None else
            None
        )
    

    @property
    def is_page_loading(
        self
    ) -> bool:
        """
        Flag to indicate if the page is still loading, which
        is `True` if the `document.readyState` is `loading`.

        The command:
        - `self.execute_script('return document.readyState;') == 'loading'`
        """
        PAGE_STATE_IS_LOADING = 'loading'

        return self.execute_script('return document.readyState;') == PAGE_STATE_IS_LOADING
    

    @property
    def is_page_loaded(
        self
    ) -> bool:
        """
        Flag to indicate if the page has been loaded, which
        is `True` if the `document.readyState` is `complete`.

        The command:
        - `self.execute_script('return document.readyState;') == 'complete'`
        """
        PAGE_STATE_IS_COMPLETE = 'complete'

        return self.execute_script('return document.readyState;') == PAGE_STATE_IS_COMPLETE


    @property
    def current_page_y_offset(
        self
    ) -> int:
        """
        Get the Y axis offset of the current web page, which
        is the amount of pixels moved from the origin (top).

        An offset of 50 pixels means that the scraper has
        scrolled down 50 pixels. The minimum value is 0 when
        on top of the web page.

        The command:
        - `self.execute_script('return window.pageYOffset')`
        """
        return self.execute_script('return window.pageYOffset')
    

    @property
    def page_height(
        self
    ) -> int:
        """
        Get the page height of the current web page,
        which is the amount of pixels from top to bottom.

        The command:
        - `self.execute_script('return document.body.scrollHeight')`
        """
        return self.execute_script('return document.body.scrollHeight')
    

    @property
    def page_size(
        self
    ) -> tuple[int, int]:
        """
        Get the size of the current screen as a
        `(width, height)` tuple. This depends on the
        screen used within the web navigator.
        """
        size = self.driver.get_window_size()

        # TODO: Is this 'height' the same as 'page_height' (?)
        return (size['width'], size['height'])
    

    @property
    def cookies(
        self
    ) -> dict:
        """
        Get the cookies of the navigator as a dict
        including the `name` and the `value`.
        """
        return {
            cookie['name']: cookie['value']
            for cookie in self.driver.get_cookies()
        }
    

    @property
    def is_using_gui(
        self
    ) -> bool:
        """
        Check if this instance is using GUI or not.
        """
        return not self._has_option_argument(HeadlessChromeOptionsArgument)
    
    """
    TODO: It would be very interesting to have
    more properties indicating if using ad
    blocker or if blocking popups and that...
    But, considering how we are using now the
    options, it could be a bit more difficult.
    By now I'm not adding it :)
    """


    def __init__(
        self,
        option_arguments: list[_ChromeOptionsArgument],
        experimental_options: list[_ChromeExperimentalOption],
        loading_page_timeout: float = 10.0
    ):
        # TODO: Validate options (?)
        self._option_arguments: list[_ChromeOptionsArgument] = option_arguments
        """
        *For internal use only*

        The option arguments we applied on the driver,
        but in our custom format.
        """
        self._experimental_options: list[_ChromeExperimentalOption] = experimental_options
        """
        *For internal use only*

        The experimental options we applied on the
        driver, but in our custom format.
        """
        
        # TODO: Init options code block
        self._options = self._prepare_options(
            option_arguments = option_arguments,
            experimental_options = experimental_options
        )
        """
        *For internal use only*

        The `Options` instance built to be used with
        the driver instance.
        """
        self.driver: webdriver.Chrome = webdriver.Chrome(
            options = self._options
        )
        """
        The `ChromeDriver` instance that we will use 
        to navigate.
        """
        self.loading_page_timeout: float = loading_page_timeout
        """
        The maximum amount of time that the system will
        spend when waiting for a web page to be loaded
        until it is rejected and aborts the execution.
        """

    def _has_option_argument(
        self,
        option_class: type[_ChromeOptionsArgument]
    ) -> bool:
        """
        *For internal use only*

        Check if this instance has the option associated
        to the `option_class` provided.
        """
        return any(
            isinstance(option, option_class)
            for option in self._option_arguments
        )
    

    def _has_experimental_option(
        self,
        option_class: type[_ChromeExperimentalOption],
        value: Union[any, None] = None
    ) -> bool:
        """
        *For internal use only*

        Check if this instance has the experimental
        option associated to the `option_class`
        provided, with also the `value` given (if
        given).

        Giving `value=None` will only check if the
        experimental option is set.
        """
        for option in self._experimental_options:
            if not isinstance(option, option_class):
                continue

            if value is None:
                return True

            return option.value == value

        return False


    def _prepare_options(
        self,
        option_arguments: list[_ChromeOptionsArgument],
        experimental_options: list[_ChromeExperimentalOption]
    ) -> Options:
        """
        *For internal use only*

        Prepare the `Options` instance to be passed to
        the driver instance when creating it.
        """
        # TODO: Validate options (?)
        options = Options()

        for option_argument in option_arguments:
            options.add_argument(option_argument.value)

        if len(experimental_options) > 0:
            # TODO: Check this: https://groups.google.com/g/chromedriver-users/c/gq9P0wPTmTY/m/1IdCDUkfBgAJ
            prefs = {}
            for experimental_option in experimental_options:
                prefs[experimental_option.name] = experimental_option.value

            options.add_experimental_option('prefs', prefs)

        return options
        

    @staticmethod
    def init(
        window_size: tuple[int, int] = (1920, 1080),
        do_use_gui: bool = False,
        do_use_ad_blocker: bool = True,
        do_disable_popups_and_cookies: bool = True,
        additional_options: list[Union[_ChromeExperimentalOption, _ChromeOptionsArgument]] = [],
        loading_page_timeout: float = 10
    ) -> 'ChromeScraper':
        """
        Get a `ChromeScraper` instance with the options
        associated to the parameters given.

        These are the parameters and their consequences:
        - `do_use_gui`: Flag to indicate if the scraper
        is using the GUI or not. Using the GUI will show
        the web navigator in the system screen.
        - `do_use_ad_blocker`: Flag to indicate if the
        scraper is using the ad blocker add-on or not.
        - `do_disable_popup_and_cookies`: Flag to
        indicate if the scraper is disabling the popups
        and cookies or not.
        """
        option_arguments = []
        experimental_options = []

        option_arguments.append(WindowSizeChromeOptionsArgument(
            width = window_size[0],
            height = window_size[1]
        ))

        if not do_use_gui:
            option_arguments.append(HeadlessChromeOptionsArgument())

        # TODO: This must be dynamic and/or given by user


        if (
            do_use_ad_blocker and
            AD_BLOCK_ABSOLUTEPATH
        ):
            # This loads the ad block 'uBlock' extension that is installed in my pc
            option_arguments.append(LoadExtensionChromeOptionsArgument(
                extension_abspath = AD_BLOCK_ABSOLUTEPATH
            ))

        # Options that I want, yes or yes
        if CHROME_USER_DATA_ABSPATH:
            option_arguments.append(LoadChromeUserProfileChromeOptionArgument(
                chrome_user_profile_abspath = CHROME_USER_DATA_ABSPATH
            ))

        option_arguments.append(IgnoreCertificateErrorsChromeOptionsArgument())
        option_arguments.append(IgnoreSslErrorsChromeOptionsArgument())
        option_arguments.append(IgnoreCertificateErrorsSpkiListChromeOptionsArgument())

        if do_disable_popups_and_cookies:
            # TODO: This shouldn't be the 3 switches but I don't
            # know exactly what does each one do
            experimental_options.append(ExcludeSwitchesChromeExperimentalOption(
                switches = ['enable-automation', 'load-extension', 'disable-popup-blocking']
            ))
            # TODO: These are not because of the popup option
            experimental_options.append(EnableDownloadsChromeExperimentalOption())
            experimental_options.append(EnableMicrophoneChromeExperimentalOption())
            experimental_options.append(EnableClipboardChromeExperimentalOption())

        if additional_options:
            for additional_option in additional_options:
                if isinstance(additional_option, _ChromeOptionsArgument):
                    option_arguments.append(additional_option)
                elif isinstance(additional_option, _ChromeExperimentalOption):
                    experimental_options.append(additional_option)

        # TODO: Implement 'loading_page_timeout'
        return ChromeScraper(
            option_arguments = option_arguments,
            experimental_options = experimental_options,
            loading_page_timeout = loading_page_timeout
        )


    def __del__(
        self
    ):
        """
        *Python core*

        This will be executed automatically to force the
        driver to be closed by killing the task, or it
        would be running in the background for nothing.
        """
        self._close()


    def reload(
        self
    ) -> 'ChromeScraper':
        """
        Reload the current web page.
        """
        self.driver.refresh()

        return self


    def go_backward(
        self,
        times: int = 1
    ) -> 'ChromeScraper':
        """
        Go backwards the amount of times provided as `times`
        in the browser history.
        """
        for _ in range(times):
            self.driver.back()

        return self


    def go_forward(
        self,
        times: int = 1
    ) -> 'ChromeScraper':
        """
        Go forward the amount of times provided as `times`
        in the browser history.
        """
        for _ in range(times):
            self.driver.forward()

        return self


    def go_to_web_and_wait_until_loaded(
        self,
        url: str
    ) -> Union[bool, None]:
        """
        Navigate to the `url` url provided and start checking
        continuously if the web page has been loaded or not,
        waiting the maximum time set for this ChromeScraper
        instance

        This method will return True in the moment the page
        is loaded, or None if something bad happens.
        """
        self._validate_url(url)

        CHECK_TIME = 0.25

        try:
            self.driver.get(url)

            cont = 0
            while (
                not self.is_page_loaded and
                cont < (self.loading_page_timeout / CHECK_TIME)
            ):
                time.sleep(CHECK_TIME)
                cont += 1

            return self.is_page_loaded

        except:
            self._close()

        return None


    def wait(
        self,
        seconds: float = 1.0,
    ) -> 'ChromeScraper':
        """
        Wait the `seconds` amount of seconds provided.

        There is no limit in the waiting time so
        please, use it carefully.
        """
        time.sleep(seconds)

        return self


    def wait_random(
        self,
        min_seconds: float = 0.5,
        max_seconds: float = 1.5
    ) -> 'ChromeScraper':
        """
        Wait a random amount of seconds in between
        the `min_seconds` and the `max_seconds`
        provided.

        There is no limit in the waiting time so
        please, use it carefully.
        """
        seconds = get_random(
            min_value = min_seconds,
            max_value = max_seconds
        )

        time.sleep(seconds)

        return self


    def press_ctrl_letter(
        self,
        letter: str = 'c'
    ) -> 'ChromeScraper':
        """
        Hold the `CTRL` key down, press the `letter` key provided
        and releases the `CTRL` key.

        This is useful for `CTRL` + `C` or `CTRL` + `V` combinations.
        """
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(letter[0]).key_up(Keys.CONTROL).perform()

        return self


    def press_ctrl_letter_on_element(
        self,
        letter: str,
        element: WebElement
    ) -> 'ChromeScraper':
        """
        Press the `CTRL` + `letter` keys while focus on the `element`
        provided.

        This is useful to pase text into text elements.
        """
        element.send_keys(Keys.CONTROL, letter[0])

        return self


    def press_ctrl_c(
        self
    ) -> 'ChromeScraper':
        """
        Press the `CTRL` + `C` keys.
        """
        self.press_ctrl_letter('c')

        return self


    def press_ctrl_c_on_element(
        self,
        element: WebElement
    ) -> 'ChromeScraper':
        """
        Press the `CTRL` + `C` keys while focus on the `element`
        provided.
        """
        self.press_ctrl_letter_on_element('c', element)

        return self


    def press_ctrl_x(
        self
    ) -> 'ChromeScraper':
        """
        Press the `CTRL` + `X` keys.
        """
        self.press_ctrl_letter('x')

        return self


    def press_ctrl_x_on_element(
        self,
        element: WebElement
    ) -> 'ChromeScraper':
        """
        Press the `CTRL` + `X` keys while focus on the `element`
        provided.
        """
        self.press_ctrl_letter_on_element('x', element)

        return self


    def press_ctrl_v(
        self
    ) -> 'ChromeScraper':
        """
        Press the `CTRL` + `V` keys.
        """
        self.press_ctrl_letter('v')

        return self


    def press_ctrl_v_on_element(
        self,
        element: WebElement
    ) -> 'ChromeScraper':
        """
        Press the `CTRL` + `V` keys while focus on the `element`
        provided.
        """
        self.press_ctrl_letter_on_element('v', element)

        return self


    def press_ctrl_a(
        self
    ) -> 'ChromeScraper':
        self.press_ctrl_letter('a')

        return self


    def press_ctrl_a_on_element(
        self,
        element: WebElement
    ) -> 'ChromeScraper':
        self.press_ctrl_letter_on_element('a', element)

        return self


    def press_key_x_times(
        self,
        key: Keys,
        times: int
    ) -> 'ChromeScraper':
        """
        Presses the provided 'key' 'times' times one behind
        the other one. This method is useful to use TAB,
        ENTER or keys like that a lot of times.
        """
        actions_chain = ActionChains(self.driver)
        for _ in range(times):
            actions_chain.send_keys(key)

        actions_chain.perform()

        return self


    def find_element_by_id(
        self,
        id: str,
        element: Union[WebElement, None] = None
    ) -> Union[WebElement, None]:
        """
        This method returns the first WebElement found with
        the provided 'id' or None if not found.

        If you provide the 'element' parameter, the search will 
        be in that element instead of the whole web page.
        """
        elements = self.find_elements_by_id(id, element)

        return (
            elements[0]
            if len(elements) > 0 else
            None
        )
    

    # TODO: Deprecated, remove soon
    def find_element_by_id_waiting(
        self,
        id: str,
        timeout: float = TIMEOUT
    ) -> Union[WebElement, None]:
        """
        *Use `find_element_by_id_waiting_until_in_dom`
        instead*

        Wait until the WebElement with the `id` provided
        is in the dom and return it if it is detected in
        less than `timeout` seconds.

        It will return None if not found.
        """
        return self.find_element_by_id_waiting_until_in_dom(By.ID, id, timeout)


    def find_elements_by_id(
        self,
        id: str,
        element: Union[WebElement, None] = None
    ) -> list[WebElement]:
        """
        This method returns an array containing the WebElements
        found with the provided 'id'.

        If you provide the 'element' parameter, the search will 
        be in that element instead of the whole web page.
        """
        return self.find_elements(
            by = By.ID,
            by_value = id,
            element = element
        )


    def find_element_by_text(
        self,
        # TODO: Create Enum for ElementType (.BUTTON, .INPUT, etc.)
        element_type: str,
        text: str,
        element: Union[WebElement, None] = None
    ) -> Union[WebElement, None]:
        """
        This method uses the 'By.XPATH' finding elements method
        with the '//element_type[contains(text(), 'text')]' 
        structure to find the element, useful for buttons that 
        have 'Save' text or things similar.

        You can use 'element_type' = 'button' and 'text' =
        'Guardar' to find the elements like this one:
        <button>Guardar</button>

        You can also use the wildcard '*'  to find any type of
        element with the specific provided 'text'.

        If you provide the 'element' parameter, the search will 
        be in that element instead of the whole web page.

        This method returns the first found WebElement if 
        existing or None if not found.
        """
        elements = self.find_elements_by_text(element_type, text, element)
        
        return (
            elements[0]
            if len(elements) > 0 else
            None
        )


    # TODO: Deprecated, remove soon
    def find_element_by_text_waiting(
        self,
        element_type: str,
        text: str,
        timeout: float = TIMEOUT
    ) -> Union[WebElement, None]:
        """
        *Use `find_element_by_text_waiting_until_in_dom`
        instead*

        Wait until the WebElement of the `element_type`
        and with the `text` provided is in the dom and
        return it if it is detected in less than
        `timeout` seconds.

        It will return None if not found.
        """
        return self.find_element_by_id_waiting_until_in_dom(
            By.XPATH,
            f"//{element_type}[contains(text(), '{text}')]",
            #"//" + element_type + "[contains(text(), '" + text + "')]",
            timeout
        )
    

    def find_elements_by_text(
        self,
        element_type: str,
        text: str,
        element: Union[WebElement, None] = None
    ) -> list[WebElement]:
        """
        This method uses the 'By.XPATH' finding elements method
        with the '//element_type[contains(text(), 'text')]' 
        structure to find the element, useful for buttons that 
        have 'Save' text or things similar.

        You can use 'element_type' = 'button' and 'text' =
        'Guardar' to find the elements like this one:
        <button>Guardar</button>

        You can also use the wildcard '*'  to find any type of
        element with the specific provided 'text'.

        If you provide the 'element' parameter, the search will 
        be in that element instead of the whole web page.

        This method returns an array with all the found elements
        or empty if not found.
        """
        root = (
            element
            if element is not None else
            self.driver
        )

        return root.find_elements(
            By.XPATH,
            f"//{element_type}[contains(text(), '{text}')]"
        )
    

    def find_element_by_class(
        self,
        element_type: str,
        class_str: str,
        element: Union[WebElement, None] = None
    ) -> Union[WebElement, None]:
        """
        This method uses the 'By.XPATH' finding elements method
        with the '//element_type[contains(@class, 'class_str')]' 
        structure to find the element, useful for divs with a
        specific class or similar.

        You can use 'element_type' = 'div' and 'class_str' =
        'container-xl' to find the elements like this one:
        <div class='container-xl'>content</div>

        You can also use the wildcard '*'  to find any type of
        element with the specific provided 'class_str'.

        If you provide the 'element' parameter, the search will 
        be in that element instead of the whole web page.

        This method returns the first found WebElement if 
        existing or None if not found.
        """
        elements = self.find_elements_by_class(element_type, class_str, element)
        
        return (
            elements[0]
            if len(elements) > 0 else
            None
        )
    

    # TODO: Deprecated, remove soon
    def find_element_by_class_waiting(
        self,
        element_type: str,
        class_str: str,
        timeout: float = TIMEOUT
    ) -> Union[WebElement, None]:
        """
        *Use `find_element_by_class_waiting_until_in_dom`
        instead*

        Wait until the WebElement of the `element_type`
        and with the `class_str` provided is in the dom
        and return it if it is detected in less than
        `timeout` seconds.

        It will return None if not found.
        """
        return self.find_element_by_id_waiting_until_in_dom(
            By.XPATH,
            f"//{element_type}[contains(@class, '{class_str}')]",
            #"//" + element_type + "[contains(@class, '" + class_str + "')]",
            timeout
        )


    def find_elements_by_class(
        self,
        element_type: str,
        class_str: str,
        element: Union[WebElement, None] = None
    ) -> list[WebElement]:
        """
        This method uses the 'By.XPATH' finding elements method
        with the '//element_type[contains(@class, 'class_str')]' 
        structure to find the element, useful for divs with a
        specific class or similar.

        You can use 'element_type' = 'div' and 'class_str' =
        'container-xl' to find the elements like this one:
        <div class='container-xl'>content</div>

        You can also use the wildcard '*'  to find any type of
        element with the specific provided 'class_str'.

        If you provide the 'element' parameter, the search will 
        be in that element instead of the whole web page.

        This method returns an array with all the found elements
        or empty if not found.
        """
        root = (
            element
            if element is not None else
            self.driver
        )

        return root.find_elements(
            By.XPATH,
            f"//{element_type}[contains(@class, '{class_str}')]"
        )


    def find_element_by_custom_tag(
        self,
        element_type: str,
        custom_tag: str,
        custom_tag_value: str,
        element: Union[WebElement, None] = None
    ) -> Union[WebElement, None]:
        """
        This method uses the 'By.XPATH' finding elements method
        with the '//element_type[@custom-tag='custom_value')]' 
        structure to find the element, useful for divs with a
        specific tag or similar.

        You can use the wildcard '*'  to find any type of
        element with the specific provided 'custom_tag'.

        If you provide the 'element' parameter, the search will 
        be in that element instead of the whole web page.

        This method returns the first found WebElement if 
        existing or None if not found.
        """
        elements = self.find_elements_by_custom_tag(element_type, custom_tag, custom_tag_value, element)
        
        return (
            elements[0]
            if len(elements) > 0 else
            None
        )


    # TODO: Deprecated, remove soon
    def find_element_by_custom_tag_waiting(
        self,
        element_type: str,
        custom_tag: str,
        custom_tag_value: str,
        timeout: float = TIMEOUT
    ) -> Union[WebElement, None]:
        """
        *Use `find_element_by_custom_tag_waiting_until_in_dom`
        instead*

        Wait until the WebElement of the `element_type`
        and with the `custom_tag` and `custom_tag_value`
        provided is in the dom and return it if it is
        detected in less than `timeout` seconds.

        It will return None if not found.
        """
        tag = (
            f'@{custom_tag}'
            if custom_tag_value == '' else
            f"@{custom_tag}='{custom_tag_value}'"
        )

        return self.find_element_waiting_until_in_dom(
            by = By.XPATH,
            by_value = f'//{element_type}[{tag}]',
            #"//" + element_type + "[" + tag + "]"
            timeout = timeout
        )


    def find_elements_by_custom_tag(
        self,
        element_type: str,
        custom_tag: str,
        custom_tag_value: str,
        element: Union[WebElement, None] = None
    ) -> list[WebElement]:
        """
        This method uses the 'By.XPATH' finding elements method
        with the '//element_type[@custom-tag='custom_value')]' 
        structure to find the element, useful for divs with a
        specific tag or similar.

        You can use the wildcard '*'  to find any type of
        element with the specific provided 'custom_tag'.
        
        If you provide the 'element' parameter, the search will 
        be in that element instead of the whole web page.

        This method returns an array with all the found elements
        or empty if not found.
        """
        # @custom-tag or @custom-tag='something'
        tag = (
            f'@{custom_tag}'
            if custom_tag_value == '' else
            f"@{custom_tag}='{custom_tag_value}'"
        )
        
        root = (
            element
            if element is not None else
            self.driver
        )

        return root.find_elements(
            By.XPATH,
            f'//{element_type}[{tag}]'
        )


    def find_element_by_element_type(
        self,
        element_type: str,
        element: Union[WebElement, None] = None
    ) -> Union[WebElement, None]:
        """
        Returns the elements found with the provided 'element_type' tag, that
        is the tag name ('span', 'div', etc.). If you provide the 'element' 
        parameter, the search will be in that element instead of the whole
        web page.
        """
        elements = self.find_elements_by_element_type(element_type, element)
        
        return (
            elements[0]
            if len(elements) > 0 else
            None
        )
    

    # TODO: Deprecated, remove soon
    def find_element_by_element_type_waiting(
        self,
        element_type: str,
        timeout: float = TIMEOUT
    ) -> Union[WebElement, None]:
        """
        *Use `find_element_by_element_type_waiting_until_in_dom`
        instead*

        Wait until the WebElement of the `element_type`
        provided is in the dom and return it if it is
        detected in less than `timeout` seconds.

        It will return None if not found.
        """
        return self.find_element_by_id_waiting_until_in_dom(
            By.TAG_NAME,
            element_type,
            timeout
        )
        

    def find_elements_by_element_type(
        self,
        element_type: str,
        element: Union[WebElement, None] = None,
        do_search_only_in_first_level: bool = False
    ) -> list[WebElement]:
        """
        Returns the web elements with the provided 'element_type' tag. 
        This method will search in the 'element' if provided, or in 
        the whole web page if not. It will look for elements only on
        the first level y 'only_first_level' is True, or in any level
        if False.

        If 'do_search_only_in_first_level' is True, this will look
        only in the first child level, horizontally, so a child of
        a child tag won't be returned.
        """
        root = (
            self.driver
            if element is None else
            element
        )

        element_type = (
            f'./{element_type}'
            if do_search_only_in_first_level else
            element_type
        )

        return root.find_elements(
            By.XPATH,
            element_type
        )
    

    # TODO: Deprecated, remove soon
    def find_element_by_xpath_waiting(
        self,
        xpath: str,
        timeout: float = TIMEOUT
    ) -> Union[WebElement, None]:
        """
        *Use `find_element_by_xpath_waiting_until_in_dom`
        instead*

        Waits until the WebElement corresponding to the provided `xpath`
        is visible and returns it if it becomes visible in the `timeout` 
        seconds of waiting. It returns None if not.
        """
        return self.find_element_by_id_waiting_until_in_dom(
            By.XPATH,
            xpath,
            timeout
        )
    

    def find_elements_by_xpath(
        self,
        xpath: str,
        element: Union[WebElement, None] = None
    ) -> list[WebElement]:
        """
        Wait until the WebElement matching the given XPath
        is found, looking for it in the `element` provided
        or in the `self.driver` if not, waiting a maximum
        time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <div>
            <span class="review">First review</span>
            <span class="review">Second review</span>
        </div>
        ```

        The following call will return the matching WebElements:
        ```
        self.find_elements_by_xpath_waiting_until_in_dom(
            "//span[@class='review']"
        )
        ```
        """
        return self.find_elements(
            by = By.XPATH,
            by_value = xpath,
            element = element
        )




    """
            NEW METHODS BELOW
    """

    def find_elements(
        self,
        by: By,
        by_value: str,
        element: Union[WebElement, None] = None
    ) -> list[WebElement]:
        """
        Find the elements with the `by` and
        `by_value` provided, inside the `element`
        given, or the `self.driver` if not.
        """
        root = (
            self.driver
            if element is None else
            element
        )

        return root.find_elements(
            by = by,
            value = by_value
        )


    def find_element_waiting_until_in_dom(
        self,
        by: By,
        by_value: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> Union[WebElement, None]:
        """
        Wait until the WebElement with the `by`
        and the `by_value` provided is present in
        the DOM, looking for it in the `element`
        provided or in the `self.driver` if not,
        waiting a maximum time of `timeout`
        seconds.
        """
        return self.wait_until(
            condition = EC.presence_of_element_located(
                (by, by_value)
            ),
            element = element,
            timeout = timeout,
        )

    def find_element_by_id_waiting_until_in_dom(
        self,
        id: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement with the given `id`
        is found, looking for it in the `element` provided
        or in the `self.driver` if not, waiting a maximum
        time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <input id="search-input" type="text">
        ```

        The following call will return the input WebElement:
        ```
        self.find_element_by_id_waiting_until_in_dom(
            "search-input"
        )
        ```
        """
        return self.find_element_waiting_until_in_dom(
            By.ID,
            id,
            element,
            timeout,
        )


    def find_element_by_css_selector_waiting_until_in_dom(
        self,
        css_selector: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement matching the given
        CSS selector is found, looking for it in the
        `element` provided or in the `self.driver` if not,
        waiting a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <input class="search-input" type="text">
        ```

        The following call will return the input WebElement:
        ```
        self.find_element_by_css_selector_waiting_until_in_dom(
            ".search-input"
        )
        ```
        """
        return self.find_element_waiting_until_in_dom(
            By.CSS_SELECTOR,
            css_selector,
            element,
            timeout,
        )


    def find_element_by_xpath_waiting_until_in_dom(
        self,
        xpath: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement matching the given
        XPath is found, looking for it in the `element`
        provided or in the `self.driver` if not, waiting
        a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <button class="submit-button">
            Submit
        </button>
        ```

        The following call will return the button WebElement:
        ```
        self.find_element_by_xpath_waiting_until_in_dom(
            "//button[@class='submit-button']"
        )
        ```
        """
        return self.find_element_waiting_until_in_dom(
            By.XPATH,
            xpath,
            element,
            timeout,
        )


    def find_element_by_class_name_waiting_until_in_dom(
        self,
        class_name: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement with the given class
        name is found, looking for it in the `element`
        provided or in the `self.driver` if not, waiting
        a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <div class="reviews-container">
            Reviews
        </div>
        ```

        The following call will return the div WebElement:
        ```
        self.find_element_by_class_name_waiting_until_in_dom(
            "reviews-container"
        )
        ```
        """
        return self.find_element_waiting_until_in_dom(
            By.CLASS_NAME,
            class_name,
            element,
            timeout,
        )


    def find_element_by_custom_tag_waiting_until_in_dom(
        self,
        element_type: str,
        custom_tag: str,
        custom_tag_value: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement with the given `custom_tag`
        and `custom_tag_value` is in the dom, looking for it
        in the `element` provided or in the `self.driver` if
        not, waiting a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <div data-testid="reviews-container">
            Reviews
        </div>
        ```

        The following call will return the visible div WebElement:
        ```
        self.find_element_by_custom_tag_waiting_until_visible(
            "div",
            "data-testid",
            "reviews-container"
        )
        ```

        You can use '*' as `element_type` to find any type
        of visible element with the given custom tag.
        """
        # @custom-tag or @custom-tag='something'
        tag = (
            f'@{custom_tag}'
            if custom_tag_value == '' else
            f"@{custom_tag}='{custom_tag_value}'"
        )

        return self.find_element_waiting_until_in_dom(
            By.XPATH,
            f'//{element_type}[{tag}]',
            element,
            timeout,
        )


    def find_element_by_element_type_waiting_until_in_dom(
        self,
        element_type: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement with the given element type
        is in the dom, looking for it in the `element`
        provided or in the `self.driver` if not, waiting a
        maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <button>
            Submit
        </button>
        ```

        The following call will return the visible button
        WebElement:
        ```
        self.find_element_by_element_type_waiting_until_visible(
            "button"
        )
        ```
        """
        return self.find_element_waiting_until_in_dom(
            by = By.TAG_NAME,
            by_value = element_type,
            element = element,
            timeout = timeout
        )


    def find_element_by_class_waiting_until_in_dom(
        self,
        element_type: str,
        class_str: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement with a class containing the
        given `class_str` is found, looking for it in the
        `element` provided or in the `self.driver` if not,
        waiting a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <div class="reviews-container active">
            Reviews
        </div>
        ```

        The following call will return the div WebElement:
        ```
        self.find_element_by_class_waiting_until_in_dom(
            "div",
            "reviews-container"
        )
        ```
        """
        by_value = f"//{element_type}[contains(@class, '{class_str}')]"

        return self.find_element_waiting_until_in_dom(
            by = By.XPATH,
            by_value = by_value,
            element = element,
            timeout = timeout
        )


    def find_element_by_text_waiting_until_in_dom(
        self,
        element_type: str,
        text: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> Union[WebElement, None]:
        """
        Wait until the WebElement containing the given `text`
        is found, looking for it in the `element` provided
        or in the `self.driver` if not, waiting a maximum
        time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <button>
            Submit review
        </button>
        ```

        The following call will return the button WebElement:
        ```
        self.find_element_by_text_waiting_until_in_dom(
            "button",
            "Submit review"
        )
        ```
        """
        by_value = f"//{element_type}[contains(text(), '{text}')]"

        return self.find_element_by_id_waiting_until_in_dom(
            by = By.XPATH,
            by_value = by_value,
            element = element,
            timeout = timeout
        )


    def find_element_waiting_until_visible(
        self,
        by: By,
        by_value: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> Union[WebElement, None]:
        """
        Wait until the WebElement with the `by`
        and the `by_value` provided is found,
        looking for it in the `element` provided
        or in the `self.driver` if not, waiting
        a maximum time of `timeout` seconds.
        """
        return self.wait_until(
            condition = EC.visibility_of_element_located(
                (by, by_value)
            ),
            element = element,
            timeout = timeout,
        )


    def find_element_by_id_waiting_until_visible(
        self,
        id: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement with the given `id`
        is visible, looking for it in the `element`
        provided or in the `self.driver` if not, waiting
        a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <input id="search-input" type="text">
        ```

        The following call will return the visible
        input WebElement:
        ```
        self.find_element_by_id_waiting_until_visible(
            "search-input"
        )
        ```
        """
        return self.find_element_waiting_until_visible(
            By.ID,
            id,
            element,
            timeout,
        )

    
    def find_element_by_css_selector_waiting_until_visible(
        self,
        css_selector: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement matching the given
        CSS selector is visible, looking for it in the
        `element` provided or in the `self.driver` if not,
        waiting a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <button class="submit-button">
            Submit
        </button>
        ```

        The following call will return the visible
        button WebElement:
        ```
        self.find_element_by_css_selector_waiting_until_visible(
            ".submit-button"
        )
        ```
        """
        return self.find_element_waiting_until_visible(
            By.CSS_SELECTOR,
            css_selector,
            element,
            timeout,
        )


    def find_element_by_xpath_waiting_until_visible(
        self,
        xpath: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement matching the given
        XPath is visible, looking for it in the `element`
        provided or in the `self.driver` if not, waiting
        a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <button class="submit-button">
            Submit
        </button>
        ```

        The following call will return the visible
        button WebElement:
        ```
        self.find_element_by_xpath_waiting_until_visible(
            "//button[@class='submit-button']"
        )
        ```
        """
        return self.find_element_waiting_until_visible(
            By.XPATH,
            xpath,
            element,
            timeout,
        )


    def find_element_by_class_name_waiting_until_visible(
        self,
        class_name: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement with the given class
        name is visible, looking for it in the `element`
        provided or in the `self.driver` if not, waiting
        a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <div class="reviews-container">
            Reviews
        </div>
        ```

        The following call will return the visible
        div WebElement:
        ```
        self.find_element_by_class_name_waiting_until_visible(
            "reviews-container"
        )
        ```
        """
        return self.find_element_waiting_until_visible(
            By.CLASS_NAME,
            class_name,
            element,
            timeout,
        )


    def find_element_by_custom_tag_waiting_until_visible(
        self,
        element_type: str,
        custom_tag: str,
        custom_tag_value: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement with the given `custom_tag`
        and `custom_tag_value` is visible, looking for it
        in the `element` provided or in the `self.driver` if
        not, waiting a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <div data-testid="reviews-container">
            Reviews
        </div>
        ```

        The following call will return the visible div WebElement:
        ```
        self.find_element_by_custom_tag_waiting_until_visible(
            "div",
            "data-testid",
            "reviews-container"
        )
        ```

        You can use '*' as `element_type` to find any type
        of visible element with the given custom tag.
        """
        # @custom-tag or @custom-tag='something'
        tag = (
            f'@{custom_tag}'
            if custom_tag_value == '' else
            f"@{custom_tag}='{custom_tag_value}'"
        )

        return self.find_element_waiting_until_visible(
            by = By.XPATH,
            by_value = f'//{element_type}[{tag}]',
            element = element,
            timeout = timeout,
        )


    def find_element_by_element_type_waiting_until_visible(
            self,
            element_type: str,
            element: Union[WebElement, None] = None,
            timeout: float = TIMEOUT,
        ) -> WebElement:
            """
            Wait until the WebElement with the given element type
            is visible, looking for it in the `element` provided
            or in the `self.driver` if not, waiting a maximum
            time of `timeout` seconds.

            For example, given the following DOM:
            ```
            <button>
                Submit
            </button>
            ```

            The following call will return the visible button
            WebElement:
            ```
            self.find_element_by_element_type_waiting_until_visible(
                "button"
            )
            ```
            """
            return self.find_element_waiting_until_visible(
                by = By.TAG_NAME,
                by_value = element_type,
                element = element,
                timeout = timeout
            )


    def find_element_by_class_waiting_until_visible(
        self,
        element_type: str,
        class_str: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> WebElement:
        """
        Wait until the WebElement with a class containing the
        given `class_str` is visible, looking for it in the
        `element` provided or in the `self.driver` if not,
        waiting a maximum time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <div class="reviews-container active">
            Reviews
        </div>
        ```

        The following call will return the div WebElement:
        ```
        self.find_element_by_class_waiting_until_in_dom(
            "div",
            "reviews-container"
        )
        ```
        """
        by_value = f"//{element_type}[contains(@class, '{class_str}')]"

        return self.find_element_waiting_until_visible(
            by = By.XPATH,
            by_value = by_value,
            element = element,
            timeout = timeout
        )

    
    def find_element_by_text_waiting_until_visible(
        self,
        element_type: str,
        text: str,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ) -> Union[WebElement, None]:
        """
        Wait until the WebElement containing the given `text`
        is visible, looking for it in the `element` provided
        or in the `self.driver` if not, waiting a maximum
        time of `timeout` seconds.

        For example, given the following DOM:
        ```
        <button>
            Submit review
        </button>
        ```

        The following call will return the button WebElement:
        ```
        self.find_element_by_text_waiting_until_in_dom(
            "button",
            "Submit review"
        )
        ```
        """
        by_value = f"//{element_type}[contains(text(), '{text}')]"

        return self.find_element_by_id_waiting_until_visible(
            by = By.XPATH,
            by_value = by_value,
            element = element,
            timeout = timeout
        )


    def switch_to_iframe_waiting(
        self,
        by: By,
        by_value: str,
        timeout: float = TIMEOUT
    ):
        """
        Switch the driver to the iframe with the
        given `by` and `by_value` conditions. This
        will let you get the elements inside that
        iframe.
        
        You can also use the `.page_source` to get
        the whole block of content.
        """
        return self.wait_until(
            condition = EC.frame_to_be_available_and_switch_to_it(
                (
                    by,
                    by_value
                )
            ),
            element = None,
            timeout = timeout,
        )


    def wait_for_url_changes(
        self,
        number_of_changes: int = 1,
        timeout: float = TIMEOUT
    ):
        initial_url = self.current_url
        current_url = initial_url

        changes = 0
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            new_url = self.current_url

            if new_url != current_url:
                changes += 1
                current_url = new_url

                if changes >= number_of_changes:
                    return current_url

            time.sleep(TIME_INTERVAL)

        raise TimeoutException(f'We expected {str(number_of_changes)} changes in {str(timeout)} seconds but there were {str(changes)} changes in that period of time')


    def wait_until(
        self,
        condition,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ):
        """
        Wait until the `condition` is happening, by
        waiting a maximum `timeout` time.

        The `condition` must be a callable compatible
        with `WebDriverWait`.

        The condition's result is returned when it
        becomes truthy.

        This method will use a `WebDriverWait`
        instance.

        If `element` is provided, the `element` will
        be passed to the `WebDriverWait` instance
        instead of the `self.driver`.

        Here is an example of use:
        ```
        # Find element and return it when visible
        self.wait_until(
            condition = EC.visibility_of_element_located(
                (by, by_value)
            ),
            element = element,
            timeout = timeout,
        )
        ```
        """
        root = (
            element
            if element is not None else
            self.driver
        )

        return WebDriverWait(
            driver = root,
            timeout = timeout
        ).until(
            condition
        )


    def wait_until_lambda(
        self,
        condition,
        element: Union[WebElement, None] = None,
        timeout: float = TIMEOUT,
    ):
        """
        Wait until the `condition` lambda function is happening,
        by waiting a maximum time of `timeout` seconds.

        The condition's result is returned when it becomes truthy.

        If `element` is provided, the `element` will be passed
        to the `WebDriverWait` instance instead of the
        `self.driver`.

        Here is an example of use:
        ```
        self.wait_until_lambda(
            condition=lambda: self.current_page_y_offset == pixels,
            timeout=timeout,
        )
        ```
        """
        root = (
            element
            if element is not None else
            self.driver
        )

        def selenium_condition(_):
            result = condition()
            # Debug only
            # print("Condition result:", result)
            return result

        return WebDriverWait(
            driver = root,
            timeout = timeout
        ).until(
            selenium_condition
        )



    # TODO: When an element is hidden and you cannot interact you
    # can change the style.display
    # driver.execute_script("arguments[0].style.display = 'block';", field)

    def set_file_input(
        self,
        element: WebElement,
        abspath: str
    ) -> 'ChromeScraper':
        """
        Sends the file to a 'type=file' input web element. The 
        provided 'abspath' must be the absolute path to the file
        you want to send.
        """
        # TODO: Check that it is a valid abspath

        element.send_keys(abspath)

        return self
    

    # TODO: Refactor if possible
    def scroll_down(
        self,
        pixels: int,
        micro_pause_time: float = 0.2,
        do_behave_like_human: bool = True
    ) -> 'ChromeScraper':
        """
        Scroll down the web page by the amount of pixels provided
        as the `pixels` parameter, starting from the current position.

        The scroll is performed through multiple irregular
        movements with short random waiting intervals to simulate
        a more natural mouse wheel movement.

        If the page reaches the bottom but loads more content
        dynamically, the method will wait for the new content
        to be loaded and continue scrolling.

        The `micro_pause_time` will be used to wait
        a specific and random amount of time in 
        between the mini scrolls this method does,
        being a value around it (+-65%).

        The method will stop when the requested amount of pixels
        has been scrolled or when the page can no longer be
        scrolled after several attempts.
        """
        pixels = abs(pixels)

        scrolled_pixels = 0
        no_progress_attempts = 0

        max_no_progress_attempts = 3
        load_timeout = 3

        while scrolled_pixels < pixels:
            pixels_to_scroll = min(
                int(get_random(200, 350)),
                pixels - scrolled_pixels
            )

            previous_y_offset = self.current_page_y_offset

            previous_scroll_height = self.execute_script(
                'return document.documentElement.scrollHeight'
            )

            if do_behave_like_human:
                """
                We will try to simulate scrolling by using
                the mouse wheel as a human...
                """
                movements = self._get_scroll_movements(pixels_to_scroll)

                for pixels_to_scroll_per_movement in movements:
                    self.execute_script(
                        """
                        window.scrollTo(
                            0,
                            window.scrollY + arguments[0]
                        );
                        """,
                        pixels_to_scroll_per_movement
                    )

                    # Minimal pause in between
                    self.wait_random(0.01, 0.03)
            else:
                self.execute_script(
                    """
                    window.scrollTo(
                        0,
                        arguments[0] + arguments[1]
                    );
                    """,
                    previous_y_offset,
                    pixels_to_scroll
                )

            self.wait_until_lambda(
                condition = lambda: (
                    self.current_page_y_offset != previous_y_offset
                    or
                    self.execute_script(
                        'return document.documentElement.scrollHeight'
                    ) != previous_scroll_height
                ),
                timeout = load_timeout,
            )

            current_y_offset = self.current_page_y_offset

            current_scroll_height = self.execute_script(
                'return document.documentElement.scrollHeight'
            )

            moved_pixels = (
                current_y_offset - previous_y_offset
            )

            if moved_pixels > 0:
                scrolled_pixels += moved_pixels
                no_progress_attempts = 0
            elif current_scroll_height != previous_scroll_height:
                # New content was loaded. Try scrolling again.
                no_progress_attempts = 0
            else:
                no_progress_attempts += 1

                if no_progress_attempts >= max_no_progress_attempts:
                    break

            self.wait(get_random(micro_pause_time * 0.65, micro_pause_time * 1.35))

        return self


    # TODO: Refactor if possible
    def scroll_up(
        self,
        pixels: int,
        micro_pause_time: float = 0.05,
        do_behave_like_human: bool = True
    ) -> 'ChromeScraper':
        """
        Scroll up the web page by the amount of pixels provided
        as the `pixels` parameter, starting from the current position.

        The scroll is performed through multiple irregular
        movements with short random waiting intervals to simulate
        a more natural mouse wheel movement.

        The `micro_pause_time` will be used to wait
        a specific and random amount of time in
        between the mini scrolls this method does,
        being a value around it (+-65%).

        The method will stop when the requested amount of pixels
        has been scrolled or when the page can no longer be
        scrolled after several attempts.
        """
        pixels = abs(pixels)

        scrolled_pixels = 0
        no_progress_attempts = 0

        max_no_progress_attempts = 3
        scroll_timeout = 0.5

        while scrolled_pixels < pixels:
            pixels_to_scroll = min(
                int(get_random(200, 350)),
                pixels - scrolled_pixels
            )

            previous_y_offset = self.current_page_y_offset

            if previous_y_offset == 0:
                break

            if do_behave_like_human:
                """
                We will try to simulate scrolling by using
                the mouse wheel as a human...
                """
                movements = self._get_scroll_movements(
                    pixels_to_scroll
                )

                for pixels_to_scroll_per_movement in movements:
                    self.execute_script(
                        """
                        window.scrollTo(
                            0,
                            window.scrollY - arguments[0]
                        );
                        """,
                        pixels_to_scroll_per_movement
                    )

                    # Minimal pause in between
                    self.wait_random(0.01, 0.03)

            else:
                self.execute_script(
                    """
                    window.scrollTo(
                        0,
                        arguments[0] - arguments[1]
                    );
                    """,
                    previous_y_offset,
                    pixels_to_scroll
                )

            try:
                self.wait_until_lambda(
                    condition = lambda: (
                        self.current_page_y_offset != previous_y_offset
                        or
                        self.current_page_y_offset == 0
                    ),
                    timeout = scroll_timeout,
                )
            except TimeoutException:
                # The page did not move. This is a valid
                # situation when there is no more scroll available.
                pass

            current_y_offset = self.current_page_y_offset

            moved_pixels = previous_y_offset - current_y_offset

            if moved_pixels > 0:
                scrolled_pixels += moved_pixels
                no_progress_attempts = 0
            else:
                no_progress_attempts += 1

                if no_progress_attempts >= max_no_progress_attempts:
                    break

            if current_y_offset == 0:
                break

            self.wait(
                get_random(
                    micro_pause_time * 0.65,
                    micro_pause_time * 1.35
                )
            )

        return self
    

    # TODO: Transform and use 'scroll_up' or 'scroll_down' (?)
    def scroll_to_element(
        self,
        element: WebElement
    ) -> 'ChromeScraper':
        """
        Scroll to 50 pixels above the element provided as the
        `element` parameter to ensure it is in the middle of
        the web page.

        This is very useful to take screenshots.

        This method will make a pasive waiting until the new
        position is reached.
        """
        element_y = element.location['y']
        y = (
            element_y - 50
            if element_y > 50 else
            0
        )

        self.execute_script(f'window.scrollTo(0, {str(y)}')

        self._wait_until(
            condition = lambda: self.current_page_y_offset != y
        )

        return self
    

    def screenshot(
        self,
        do_include_alpha: bool = True,
        output_filename: Union[str, None] = None
    ) -> Union[str, bytes]:
        """
        Takes a screenshot of the whole page and returns 
        it as binary data if no 'output_filename' provided.

        The `do_include_alpha` will force the background to
        be alpha if this is necessary.

        If 'output_filename' is provided, it will be stored 
        locally with that name.
        """
        # TODO: Make this method return the image as binary
        # data always and store if 'output_filename' is 
        # provided, but you cannot do the 'save_screenshot'
        # twice because the webpage can change in the time
        # elapsed between both screenshots.
        
        if do_include_alpha:
            self._set_transparent_background()

        # We are using this because it preserves the alpha
        # channel
        screenshot_bytes = self.driver.get_screenshot_as_png()

        if do_include_alpha:
            self._reset_background()

        if output_filename is not None:
            with open(output_filename, 'wb') as f:
                f.write(screenshot_bytes)

            return output_filename

        return screenshot_bytes
    
    
    def screenshot_element(
        self,
        element: WebElement,
        do_include_alpha: bool = True,
        output_filename: str = None
    ) -> Union[str, bytes]:
        """
        Takes a screenshot of the provided 'element', that
        means that only the area occupied by that element
        is shown in the screenshot, and returns it as 
        binary data if no 'output_filename' provided or
        will be stored locally if provided.

        Any element of the web page that is over the 
        element will appear in the screenshot blocking it.

        This method will return the 'output_filename' if it
        was provided, so the file has been stored locally,
        or a dict containing 'size' (width, height) and 
        'data' fields.
        """
        # TODO: Make this method return the image as binary
        # data always and store if 'output_filename' is 
        # provided, but you cannot do the 'save_screenshot'
        # twice because the webpage can change in the time
        # elapsed between both screenshots.
        if do_include_alpha:
            self._set_transparent_background()

        # We are using this because it preserves the alpha
        # channel
        element_screenshot_bytes = element.screenshot_as_png

        if do_include_alpha:
            self._reset_background()

        if output_filename is not None:
            with open(output_filename, 'wb') as f:
                f.write(element_screenshot_bytes)

            return output_filename

        return element_screenshot_bytes


    def screenshot_web_page(
        self,
        url: Union[str, None] = None
    ) -> list[bytes]:
        """
        This method will take screenshots of the whole
        web page. It will do in the current page if
        no `url` is provided, or will navigate to the
        provided `url` and do it in that one.

        This method returns a list of screenshots as
        bytes elements.
        """
        if url:
            self.go_to_web_and_wait_until_loaded(url)

        # TODO: Here we are not setting the background
        # as transparent

        FPS = 60
        # Maybe this should be a parameter
        # TODO: We want to make screenshots for a video
        # so depending on 'duration' it will be slower
        # or more dynamic. This method need testing
        duration = 5

        # TODO: Maybe we want to scroll more, or maybe
        # we should pass this a parameter to make it
        # more customizable
        page_height = (
            self.page_height
            if self.page_height <= 1000 else
            1000
        )

        screenshots = []
        number_of_screenshots = int(duration * FPS)
        # window_size = self.driver.get_window_size()

        # TODO: How much should we scroll?
        new_height = 0
        for _ in range(number_of_screenshots):
            screenshots.append(self.driver.get_screenshot_as_png())
            height = self.current_page_y_offset
            new_height += page_height / number_of_screenshots
            # We scroll down the difference
            self.scroll_down(new_height - height)

        # TODO: What if we end before the page is finished (?)
        # TODO: I think we should refactor this to do more things

        # TODO: These should be streamed instead (?)
        return screenshots


    def execute_script(
        self,
        script: str,
        *args
    ) -> any:
        """
        Executes the provided `script` synchronously with
        the given `args` if provided.

        You can make a call like this:
        ```
        chrome_scraper.execute_script(
            'arguments[0].scrollTop += arguments[1];',
            arg1,
            arg2
        )
        ```
        """
        return self.driver.execute_script(script, *args)


    def remove_element(
        self,
        element: WebElement
    ) -> any:
        """
        Remove the provided `element`.

        The command:
        - `self.execute_script('arguments[0].remove()', element)`
        """
        return self.execute_script('arguments[0].remove()', element)
    
    
    def set_element_width(
        self,
        element: WebElement,
        width: int
    ) -> any:
        """
        Set the width provided as `width` to the also given
        element `element`.

        The command:
        - `self.execute_script(f'arguments[0].style = "width: {str(width)}px;"', element)`
        """
        return self.execute_script(f'arguments[0].style = "width: {str(width)}px;"', element)
    

    def set_element_style(
        self,
        element: WebElement,
        style: str
    ) -> any:
        """
        Set the style provided as `style` to the also given
        element `element`.

        The command:
        - `self.execute_script(f"arguments[0].style = '{style}'", element)`
        """
        
        return self.execute_script(f"arguments[0].style = '{style}'", element)
    

    def set_element_attribute(
        self,
        element: WebElement,
        attribute: str,
        value: str
    ) -> any:
        """
        Set the attribute provided as `attribute`, with the given
        `value`, to the also provided element `element`.

        The command:
        - `self.execute_script(f"arguments[0].setAttribute('{attribute}', '{value}')", element)`
        """
        return self.execute_script(f"arguments[0].setAttribute('{attribute}', '{value}')", element)
    

    def set_element_inner_text(
        self,
        element: WebElement,
        inner_text: str
    ) -> any:
        """
        Set the given `inner_text` as the inner text of the
        also provided element `element`.

        The command:
        - `self.execute_script(f"arguments[0].innerText = '{str(inner_text)}';", element)`
        """
        return self.execute_script(f"arguments[0].innerText = '{str(inner_text)}';", element)
    

    def set_page_size(
        self,
        width: int = 1920,
        height: int = 1080
    ) -> 'ChromeScraper':
        """
        This method resizes the web navigator to the provided
        width and height. It is useful to take screenshots from
        webpages or to validate different screen sizes.
        """
        self.driver.set_window_size(width, height)

        return self
    

    def add_to_clipboard(
        self,
        text: str
    ) -> 'ChromeScraper':
        """
        Adds the provided 'text' to the clipboard to be able to 
        paste it. This method will create a 'textarea' element,
        write the provided 'text' and copy it to the web
        scrapper clipboard.
        """
        TEXT_AREA_ID = 'textarea_to_copy_912312' # a random one
        # I create a new element to put the text, copy it and be able to paste
        js_code = "var p = document.createElement('textarea'); p.setAttribute('id', '" + TEXT_AREA_ID + "'); p.value = '" + text + "'; document.getElementsByTagName('body')[0].appendChild(p);"
        self.execute_script(js_code)

        # Focus on textarea
        textarea = self.find_element_by_id(TEXT_AREA_ID)
        textarea.click()
        self.press_ctrl_a_on_element(textarea)
        self.press_ctrl_c_on_element(textarea)
        # TODO: I can use 'textarea.send_keys(Keys.CONTROL, 'c') to copy, validate
        # actions.key_down(Keys.CONTROL).send_keys('A').key_up(Keys.CONTROL).perform()
        # actions.key_down(Keys.CONTROL).send_keys('C').key_up(Keys.CONTROL).perform()

        # Remove the textarea, it is no longer needed
        js_code = "var element = document.getElementById('" + TEXT_AREA_ID + "'); element.parentNode.removeChild(element);"
        # TODO: Update this with the new version
        self.execute_script(js_code)

        return self


    def _close(
        self
    ):
        """
        Force the driver to be closed and the 
        'self.driver' attribute to be None.

        For internal use only.
        """
        try:
            self.driver.close()
        finally:
            self.driver = None


    def _validate_url(
        self,
        url: str
    ):
        """
        *For internal use only*

        Validate the `url` provided, raising an exception
        if it is not valid.
        """
        
        """
        When using 'www.google.es' instead of
        'https://www.google.es' it raises an Exception
        showing this in the console:
        [9192:8160:0309/174912.456:ERROR:new_tab_page_handler.cc(1306)] NewTabPage loaded into a non-browser-tab context
        and setting self.driver = None

        Thats why we are validating with this specific
        url regexp.
        """
        if not GeneralRegularExpression.URL.is_valid_regex(url):
            raise Exception('The "url" provided is not a valid url.')


    def _get_scroll_movements(
        self,
        pixels: int
    ) -> list[int]:
        """
        *For internal use only*

        Get the pixel movements that compose a single
        scroll wheel gesture.

        The returned movements follow an acceleration
        and deceleration pattern, starting and ending
        with short movements and reaching a larger
        movement in the middle.

        It generates 5 movements with the next
        distribution:
        - 0.10
        - 0.20
        - 0.40
        - 0.20
        - 0.10
        """
        pixels = abs(pixels)

        proportions = (
            0.10,
            0.20,
            0.40,
            0.20,
            0.10,
        )

        movements = [
            int(pixels * proportion)
            for proportion in proportions
        ]

        movements[-1] += pixels - sum(movements)

        return movements


    def _wait_until(
        self,
        condition,
        timeout: float = TIMEOUT,
    ):
        """
        *For internal use only*

        Wait until the `condition` is happening, by
        waiting a maximum `timeout` time.

        The `condition` must be a lambda function
        to be able to evaluate it.

        This method will use the `time` module.

        The condition's result is returned when it
        becomes truthy.

        Here is an example of use:
        ```
        self._wait_until(
            lambda: self.current_page_y_offset == pixels
        )
        ```
        """
        remaining_time = timeout

        while remaining_time > 0:
            result = condition()

            if result:
                return result

            self.wait(TIME_INTERVAL)
            remaining_time -= TIME_INTERVAL

        return condition()
    
    
    def _set_transparent_background(
        self
    ) -> 'ChromeScraper':
        """
        *For internal use only*

        Set the background as transparent.
        
        This code is useful when we are taking screenshots of
        elements with a transparent background and we want to
        keep that alpha transparency in the image.

        The command:
        - `self.driver.execute_cdp_cmd(
            'Emulation.setDefaultBackgroundColorOverride',
            {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}}
        )`
        """
        self.driver.execute_cdp_cmd(
            'Emulation.setDefaultBackgroundColorOverride',
            {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}}
        )

        return self


    def _reset_background(
        self
    ) -> 'ChromeScraper':
        """
        *For internal use only*

        Reset the background.
        
        This code is useful when we are taking screenshots of
        elements with a transparent background and we want to
        keep that alpha transparency in the image.

        The command:
        - `self.driver.execute_cdp_cmd(
            'Emulation.setDefaultBackgroundColorOverride',
            {}
        )`
        """
        self.driver.execute_cdp_cmd(
            'Emulation.setDefaultBackgroundColorOverride',
            # If empty, it will remove the 'override'
            # condition, recovering the original value
            {}
        )

        return self

    # TODO: Maybe automate some 'execute_javascript' to change
    # 'innerHTML' and that stuff (?)




# # TODO: Move this method below to the main class
# def get_redicted_url(url, expected_url = None, wait_time = 5):
#     """
#     Navigates to the provided url and waits for a redirection. This method will wait
#     until the 'expected_url' is contained in the new url (if 'expected_url' parameter
#     is provided), or waits 'wait_time' seonds to return the current_url after that.
#     """
#     redirected_url = ''

#     try:
#         options = Options()
#         options.add_argument("--start-maximized")
#         # Remove this line below for debug
#         options.add_argument("--headless=new") # for Chrome >= 109
#         driver = webdriver.Chrome(options = options)
#         driver.get(url)

#         wait = WebDriverWait(driver, 10)

#         if not expected_url:
#             time.sleep(wait_time)
#         else:
#             wait.until(EC.url_contains(expected_url))

#         redirected_url = driver.current_url
#     finally:
#         driver.close()

#     return redirected_url
