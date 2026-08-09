# Web scraper, but made easy

The easiest way to scrape the Internet.


# Functionality
Scrape the Internet to get the information or perform the actions you need. By now we only have a `ChromeScraper` class to scrape using Google Chrome.

# Usage
Use the driver like this:

1. Create an instance, go to a website and wait until loaded, without GUI:
```
from web_scraper_easy import ChromeScraper
from web_scraper_easy.chrome.dataclasses.options_argument import StartMaximizedChromeOptionsArgument

# Initialize it, full screen but no GUI
chrome = ChromeScraper.init(
    do_use_gui = False,
    additional_options = [
        StartMaximizedChromeOptionsArgument
    ]
)
chrome.go_to_web_and_wait_until_loaded('https://webscraper.io/test-sites/e-commerce/allinone/product/146')
# Get the card to interact with it
card_thumbnail = chrome.find_element_by_class('div', 'card thumbnail')
```

Check the `tests` files to see more examples.