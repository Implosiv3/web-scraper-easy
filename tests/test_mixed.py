from web_scraper_easy import ChromeScraper
from pytest_easy import does_file_exist

import pytest


@pytest.mark.mandatory
def test_chrome_scraper():
    from web_scraper_easy.chrome import Keys
    from web_scraper_easy.chrome.dataclasses.options_argument import StartMaximizedChromeOptionsArgument
    from tests.common import WEB_URL, WEB_URL_2

    chrome = ChromeScraper.init(
        additional_options = [
            StartMaximizedChromeOptionsArgument
        ]
    )
    assert not chrome.is_using_gui
    assert chrome.go_to_web_and_wait_until_loaded(WEB_URL)
    assert chrome.find_element_by_class('div', 'card thumbnail') is not None
    assert chrome.page_height == 981 #1026
    assert chrome.page_size == (1920, 1080)
    assert chrome.current_page_y_offset == 0
    assert chrome.active_element.tag_name == 'body'
    assert chrome.current_url == WEB_URL
    assert chrome.is_page_loading == False
    assert chrome.is_page_loaded == True
    assert len(chrome.cookies) >= 0

    assert chrome.current_page_y_offset == 0
    chrome.scroll_down(20)
    assert chrome.current_page_y_offset == 20
    chrome.scroll_up(10)
    assert chrome.current_page_y_offset == 10

    chrome.go_to_web_and_wait_until_loaded(WEB_URL_2)
    assert chrome.current_url == WEB_URL_2
    chrome.go_backward()
    assert chrome.current_url == WEB_URL
    chrome.go_forward()
    assert chrome.current_url == WEB_URL_2

    assert len(chrome.find_elements_by_text('h1', 'Test Sites')) > 0
    title_element = chrome.find_element_by_text('h1', 'Test Sites')
    assert title_element is not None
    assert len(chrome.find_elements_by_custom_tag('img', 'itemprop', 'image')) > 0
    assert chrome.find_element_by_custom_tag('img', 'itemprop', 'image') is not None

    assert chrome.press_key_x_times(
        key = Keys.TAB,
        times = 3
    ) == chrome

    assert chrome.screenshot() is not None
    output_filename = 'test_files/screenshot.png'
    assert chrome.screenshot(
        output_filename = output_filename
    ) == output_filename
    assert does_file_exist(output_filename)
    assert chrome.screenshot_element(title_element) is not None

    chrome.remove_element(title_element)
    assert chrome.find_element_by_text('h1', 'Test Sites') is None