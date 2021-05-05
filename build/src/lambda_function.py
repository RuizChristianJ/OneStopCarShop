import time

# from webdriver_wrapper import WebDriverWrapper
from selenium.webdriver.common.keys import Keys
from scraper import SelectionEnum, WebDriverWrapper


def lambda_handler(*args, **kwargs):
    driver = WebDriverWrapper()
    makes = driver.get_make_id(SelectionEnum.allMakes)

    return makes
