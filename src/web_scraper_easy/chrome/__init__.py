from web_scraper_easy.chrome.dataclasses.options_argument import HeadlessChromeOptionsArgument, LoadExtensionChromeOptionsArgument, _ChromeOptionsArgument, WindowSizeChromeOptionsArgument, IgnoreCertificateErrorsChromeOptionsArgument, IgnoreCertificateErrorsSpkiListChromeOptionsArgument, IgnoreSslErrorsChromeOptionsArgument, LoadChromeUserProfileChromeOptionArgument
from web_scraper_easy.chrome.dataclasses.experimental_options import ExcludeSwitchesChromeExperimentalOption, EnableDownloadsChromeExperimentalOption, EnableMicrophoneChromeExperimentalOption, EnableClipboardChromeExperimentalOption, _ChromeExperimentalOption
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
from typing import Union

import time


"""
TODO: Is all this needed? Could we do
something to make it work without (?)
"""
CHROME_EXTENSIONS_ABSPATH = getenv('CHROME_EXTENSIONS_ABSPATH')
AD_BLOCK_ABSOLUTEPATH = getenv('AD_BLOCK_ABSOLUTEPATH')
CHROME_USER_DATA_ABSPATH = getenv('CHROME_USER_DATA_ABSPATH')

if not CHROME_EXTENSIONS_ABSPATH:
    raise Exception('The "CHROME_EXTENSIONS_ABSPATH" environment variable is not defined.')

if not AD_BLOCK_ABSOLUTEPATH:
    raise Exception('The "AD_BLOCK_ABSOLUTEPATH" environment variable is not defined.')

if not CHROME_USER_DATA_ABSPATH:
    raise Exception('The "CHROME_USER_DATA_ABSPATH" environment variable is not defined.')

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

        if do_use_ad_blocker:
            # This loads the ad block 'uBlock' extension that is installed in my pc
            option_arguments.append(LoadExtensionChromeOptionsArgument(
                extension_abspath = AD_BLOCK_ABSOLUTEPATH
            ))
        
        # Options that I want, yes or yes
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
        seconds: float
    ) -> 'ChromeScraper':
        """
        Waits for the provided 'time' seconds. There is
        no limit in the waiting time, so please use it
        carefully.
        """
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
    

    def find_element_by_id_waiting(
        self,
        id: str,
        time: int = 30
    ) -> Union[WebElement, None]:
        """
        Waits until the WebElement corresponding to the provided 
        'element_type' with also provided 'id' is visible and 
        returns it if it becomes visible in the 'time' seconds 
        of waiting. It returns None if not.
        """
        return self._find_element_by_waiting(By.ID, id, time)


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
        root = (
            element
            if element is not None else
            self.driver
        )

        return root.find_elements(By.ID, id)


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


    def find_element_by_text_waiting(
        self,
        element_type: str,
        text: str,
        time: int = 30
    ) -> Union[WebElement, None]:
        """
        Waits until the WebElement corresponding to the provided 
        'element_type' and 'text' is visible and returns it if 
        it becomes visible in the 'time' seconds of waiting. It 
        returns None if not.
        """
        return self._find_element_by_waiting(
            By.XPATH,
            f"//{element_type}[contains(text(), '{text}')]",
            #"//" + element_type + "[contains(text(), '" + text + "')]",
            time
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
    

    def find_element_by_class_waiting(
        self,
        element_type: str,
        class_str: str,
        time: int = 30
    ) -> Union[WebElement, None]:
        """
        Waits until the WebElement corresponding to the provided 
        'element_type' and class is visible and returns it if it
        becomes visible in the 'time' seconds of waiting. It 
        returns None if not.
        """
        return self._find_element_by_waiting(
            By.XPATH,
            f"//{element_type}[contains(@class, '{class_str}')]",
            #"//" + element_type + "[contains(@class, '" + class_str + "')]",
            time
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


    def find_element_by_custom_tag_waiting(
        self,
        element_type: str,
        custom_tag: str,
        custom_tag_value: str,
        time: int = 30
    ) -> Union[WebElement, None]:
        """
        Waits until the WebElement corresponding to the provided 
        'element_type' and custom tag is visible and returns it 
        if it becomes visible in the 'time' seconds of waiting.
        It returns None if not.
        """
        tag = (
            f'@{custom_tag}'
            if custom_tag_value == '' else
            f"@{custom_tag}='{custom_tag_value}'"
        )

        return self._find_element_by_waiting(
            By.XPATH,
            f'//{element_type}[{tag}]',
            #"//" + element_type + "[" + tag + "]"
            time
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
    

    def find_element_by_element_type_waiting(
        self,
        element_type: str,
        time: int = 30
    ) -> Union[WebElement, None]:
        """
        Waits until the WebElement corresponding to the provided 
        'element_type' tag is visible and returns it if it becomes
        visible in the 'time' seconds of waiting. It returns None
        if not.
        """
        return self._find_element_by_waiting(
            By.TAG_NAME,
            element_type,
            time
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
    

    def find_element_by_xpath_waiting(
        self,
        xpath: str,
        time: int = 30
    ) -> Union[WebElement, None]:
        """
        Waits until the WebElement corresponding to the provided 'xpath'
        is visible and returns it if it becomes visible in the 'time' 
        seconds of waiting. It returns None if not.
        """
        return self._find_element_by_waiting(
            By.XPATH,
            xpath,
            time
        )
    

    def find_elements_by_xpath(
        self,
        xpath: str,
        element: Union[WebElement, None] = None
    ) -> list[WebElement]:
        """
        This method uses the 'By.XPATH' finding elements method.

        If you provide the 'element' parameter, the search will 
        be in that element instead of the whole web page.

        This method returns an array with all the found elements
        or empty if not found.
        """
        root = (
            self.driver
            if element is None else
            element
        )

        return root.find_elements(
            By.XPATH,
            xpath
        )
    

    def _find_element_by_waiting(
        self,
        by: By,
        by_value: str,
        time: int = 30
    ) -> Union[WebElement, None]:
        """
        *For internal use only*

        Internal method to simplify the way we try to find
        an element, by using the `by` parameter provided,
        waiting until it is visible (or until the `time`
        amount of time waited is reached).
        """
        wait = WebDriverWait(self.driver, time)
        element = wait.until(EC.visibility_of_element_located((by, by_value)))

        return (
            None
            if not element else
            element
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
    

    def scroll_down(
        self,
        pixels: int
    ) -> 'ChromeScraper':
        """
        Scroll down the web page the amount of pixels provided as
        the `pixels` parameter, starting from the current position.

        This method will make a passive waiting until the new
        position is reached.
        """
        pixels = abs(pixels) + self.current_page_y_offset

        self.execute_script(f'window.scrollTo(0, {str(pixels)})')

        self._wait_until(
            condition = lambda: self.current_page_y_offset != pixels
        )

        return self


    def scroll_up(
        self,
        pixels: int
    ) -> 'ChromeScraper':
        """
        Scroll up the web page the amount of pixels provided as
        the `pixels` parameter, starting from the current position.

        This method will make a passive waiting until the new
        position is reached.
        """
        pixels = abs(pixels)
        current_y = self.current_page_y_offset

        pixels = current_y - pixels
        if pixels < 0:
            pixels = 0

        self.execute_script(f'window.scrollTo(0, {str(pixels)})')

        self._wait_until(
            condition = lambda: self.current_page_y_offset != pixels
        )

        return self
    

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
    

    def _wait_until(
        self,
        condition,
        timeout: float = 30.0,
    ) -> bool:
        """
        *For internal use only*

        Wait until the `condition` is happening, by
        waiting a maximum `timeout` time.

        The `condition` must be a lambda function
        to be able to evaluate it.

        Here is an example of use:
        ```
        self._wait_until(
            lambda: self.current_page_y_offset == pixels
        )
        ```
        """
        TIME_INTERVAL = 0.1
        remaining_time = timeout

        while (
            not condition() and
            remaining_time > 0
        ):
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

    # TODO: Maybe automate some 'execute_javascript' to change
    # 'innerHTML' and that stuff (?)



# TODO: Remove all this below when all refactored.
# By now I'm commenting them
# def download_fake_call_image(name, output_filename):
#     # TODO: Move this to the faker
#     URL = 'https://prankshit.com/fake-iphone-call.php'

#     try:
#         driver = start_chrome()
#         go_to_and_wait_loaded(driver, URL)

#         inputs = driver.find_elements(By.TAG_NAME, 'input')
#         name_textarea = driver.find_element(By.TAG_NAME, 'textarea')

#         #operator_input = inputs[4]
#         #hour_input = inputs[5]

#         name_textarea.clear()
#         name_textarea.send_keys(name)

#         image = driver.find_element(By.XPATH, '//div[contains(@class, "modal-content tiktok-body")]')
#         image.screenshot(output_filename)
#     finally:
#         driver.close()

# # Other fake generators (https://fakeinfo.net/fake-twitter-chat-generator) ad (https://prankshit.com/fake-whatsapp-chat-generator.php)
# def download_discord_message_image(text, output_filename):
#     URL = 'https://message.style/app/editor'

#     try:
#         driver = start_chrome()
#         go_to_and_wait_loaded(driver, URL)
        
#         time.sleep(3)

#         clear_embed_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Clear Embeds')]")
#         clear_embed_button.click()

#         time.sleep(3)

#         input_elements = driver.find_elements(By.TAG_NAME, 'input')
#         username_input = input_elements[3]
#         avatar_url_input = input_elements[4]

#         username_input.clear()
#         username_input.send_keys('botsito')

#         avatar_url_input.clear()
#         avatar_url_input.send_keys('https://cdn.pixabay.com/photo/2016/11/18/23/38/child-1837375_640.png')

#         textarea_input = driver.find_element(By.TAG_NAME, 'textarea')
#         textarea_input.clear()
#         textarea_input.send_keys(text)

#         time.sleep(3)

#         # get element div class='discord-message'
#         discord_message = driver.find_element(By.XPATH, "//div[contains(@class, 'discord-message')]")
#         discord_message.screenshot(output_filename)
#     finally:
#         driver.close()



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


# def get_youtube_summary(video_id):
#     """
#     Searchs into 'summarize.tech' web to obtain the summary of the video with the 
#     provided 'video_id'. This method returns the summary in English, as it is 
#     provided by that website.
#     """
#     url = f'https://www.summarize.tech/www.youtube.com/watch?v={video_id}'

#     try:
#         options = Options()
#         options.add_argument("--start-maximized")
#         # Remove this line below for debug
#         options.add_argument("--headless=new") # for Chrome >= 109
#         driver = webdriver.Chrome(options = options)
#         driver.get(url)

#         summary = driver.find_element_by_tag_name('section').find_element_by_tag_name('p').get_attribute('innerText')
#     finally:
#         driver.close()

#     return summary

def google_translate(text, input_language = 'en', output_language = 'es') -> str:
    url = 'https://translate.google.com/?hl=es'
    """
    https://translate.google.com/?hl=es&sl=en&tl=es&text=Aporta%20una%20unidad%20de%20traducci%C3%B3n%20(segmento%20y%20traducci%C3%B3n)%20en%20alg%C3%BAn%20par%20de%20idiomas%20a%20MyMemory.%0ASin%20especificar%20ning%C3%BAn%20par%C3%A1metro%20clave%2C%20la%20contribuci%C3%B3n%20est%C3%A1%20disponible%20para%20todos%20(%C2%A1Gracias!).&op=translate

    https://translate.google.com/?hl=es&tab=TT&sl=en&tl=es&op=translate

    https://translate.google.com/?hl=es&tab=TT&sl=en&tl=es&text=La%20%C3%BAnica%20forma%20de%20saberlo%20es%20lo%20que%20t%C3%BA%20digas&op=translate
    """

    url = 'https://translate.google.com/?hl=' + output_language + '&tab=TT&sl=' + input_language + '&tl=' + output_language + '&text=' + text + '&op=translate'

    translation = ''

    # TODO: Verify that this below is working
    driver = ChromeScraper()
    driver.go_to_web_and_wait_until_loaded(url)
    translation = driver.find_element_by_xpath_waiting('//*[@jscontroller="JLEx7e"]', 10).get_attribute('innerText')
    # TODO: Maybe make a method to obtain the inner text from a WebElement (?)
    return translation

    # TODO: Refactor this as we have a better chrome driver lib now
    try:
        options = Options()
        options.add_argument("--start-maximized")
        # Comment this line below for debug (enables GUI)
        options.add_argument("--headless=new") # for Chrome >= 109
        driver = webdriver.Chrome(options = options)
        driver.get(url)

        tries = 0
        while True:
            if tries < 20:
                try:
                    # We try until it doesn't fail (so we have the text)
                    # TODO: This 'jscontroller' changes from time to time, pay atention
                    translation = driver.find_elements('xpath', '//*[@jscontroller="JLEx7e"]')[0].get_attribute('innerText')
                    tries = 20
                except Exception as e:
                    # TODO: Uncomment this to see if code error or scrapper error
                    #print(e)
                    tries += 1
                    time.sleep(0.250)
            else:
                break
    finally:
        driver.close()

    return translation

    """
    # Intersting options: https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1726
    # Also this: https://stackoverflow.com/questions/19211006/how-to-enable-cookies-in-chromedriver-with-webdriver
    # What about this: options.AddUserProfilePreference("profile.cookie_controls_mode", 0);
    """