"""
A simple test to verify that pytes is working and
the tests are being detected.
"""
import pytest


@pytest.mark.additional
def test_scroll():
    from web_scraper_easy import ChromeScraper
    from web_scraper_easy.chrome.dataclasses.options_argument import StartMaximizedChromeOptionsArgument

    chrome = ChromeScraper.init(
        do_use_gui = True,
        do_use_ad_blocker = False,
        do_disable_popups_and_cookies = False,
        additional_options = [
            StartMaximizedChromeOptionsArgument
        ]
    )

    chrome.go_to_web_and_wait_until_loaded('http://marca.com')
    chrome.scroll_down(1000, 0.2, True)
    chrome.scroll_up(1000, 0.2, True)
