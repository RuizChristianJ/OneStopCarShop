## This file will be used to scrape the car gurus webpages for the data.

import requests
import json
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import math
from enum import Enum
import random


zip_code = '06066'
distance = ['10', '25', '50', '75', '100', '150', '200', '500', '50000']
transmission = ['', '&transmission=']
transmission_type = ['A', 'M']
max_mileage = ['', '&maxMileage=']
mileage = '50000'
max_year = 'c27605'
min_year = 'c24781'


make_id_URL = f'https://www.cargurus.com'
# model_id_URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?' \
#               f'sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity={make_id}'
query_URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=' \
      f'{zip_code}&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel&distance={distance[8]}&' \
      f'entitySelectingHelper.selectedEntity2={max_year}&sortType=AGE_IN_DAYS&' \
      f'entitySelectingHelper.selectedEntity={min_year}{max_mileage[1]}{mileage}{transmission[1]}{transmission_type[1]}'


class SelectionEnum(Enum):
    allMakes = 'All Makes'
    popMakes = 'Popular Makes'

    Models = ['Popular Models', 'Other Models']

    Listing = 'window.__PREFLIGHT__ = '

    pageNo = 'page-navigation-number-of-listings'


#TODO Add option for two grouping types. Comes in handy for listing getter.
def get_soup_group(grouping: str, url: str):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=options, executable_path=r"C:\bin\chromedriver_win32\chromedriver.exe")
    driver.get(url)
    sleep_timer = random.randint(3, 15)
    time.sleep(sleep_timer)
    page = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page, 'html.parser')
    groups = soup.find_all(grouping)

    if len(groups) == 0:
        raise KeyError

    return soup


#TODO Add option for two grouping types. Comes in handy for listing getter.
def get_selection(url: str, selection_type: SelectionEnum):
    optgroup = get_soup_group('optgroup', url)

    selection = []
    if selection_type == SelectionEnum.Models:
        for i in range(0, len(selection_type.value)):
            for group in optgroup:
                if selection_type.value[i] in str(group):
                    selection.append(str(group))
                    break
        return selection
    else:
        for group in optgroup:
            if selection_type.value in str(group):
                selection.append(str(group))
                break
        return selection


def clean_selection(selection: str):
    selection_cleaned = selection.split('option value=')
    for i in range(0, len(selection_cleaned)):
        selection_cleaned[i] = selection_cleaned[i].replace('"', '')
        selection_cleaned[i] = selection_cleaned[i].replace('>', ' ')
        selection_cleaned[i] = selection_cleaned[i].split('<')[0]
    selection_cleaned = selection_cleaned[1:]
    selection_dict = {}
    for value in selection_cleaned:
        ssplit = value.split(' ')
        selection_dict[ssplit[1]] = ssplit[0]
    return selection_dict


def get_make_id(selection_type: SelectionEnum):
    # Get all makes or just the "popular" ones (as defined by CarGurus).
    if selection_type not in [SelectionEnum.allMakes, SelectionEnum.popMakes]:
        raise KeyError

    make_url = f'https://www.cargurus.com'

    makes = get_selection(make_url, selection_type)[0]
    makes = clean_selection(makes)

    return makes


def get_model_id(make_id: str = None):

    model_url = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?' \
          f'sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity={make_id}'

    models = get_selection(model_url, SelectionEnum.Models)
    models_dict = clean_selection(models[0])
    models_dict.update(clean_selection(models[1]))

    return models_dict


def get_listings(soup):
    scripts = soup.find_all('script')
    listings = ''
    for script in scripts:
        if 'window.__PREFLIGHT__ = ' in str(script):
            listings = str(script)
            break
    listings = listings.split(' window.__PREFLIGHT__')[1].strip()[2:-1]
    listings = json.loads(listings)
    listings = listings['listings']
    return listings


def get_car_data(zip: str, min_year_id: str, max_year_id: str, distance: int, transmission: str=None,
                 max_mileage: str=None):

    page_no = 1
    transmission_str = ''
    max_mileage_str = ''
    if transmission is not None:
        transmission_str = f'&transmission={transmission}'
    if max_mileage is not None:
        max_mileage_str = f'&maxMileage={max_mileage}'

    URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=' \
          f'{zip_code}&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel' \
          f'&distance={distance}&entitySelectingHelper.selectedEntity2={max_year_id}&sortType=AGE_IN_DAYS&' \
          f'entitySelectingHelper.selectedEntity={min_year_id}{max_mileage_str}{transmission_str}#resultsPage={page_no}'

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=options, executable_path=r"C:\bin\chromedriver_win32\chromedriver.exe")
    driver.get(URL)
    time.sleep(3)
    page = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page, 'html.parser')

    listings = get_listings(soup)

    span = soup.find_all('span')

    num_listings = 0
    for val in span:
        if 'page-navigation-number-of-listings' in str(val):
            num_listings = int(str(val).split('<strong>')[-1].split('<')[0])
            break

    num_pages = 0
    if num_listings > 0:
        num_pages = math.ceil(num_listings/15.0)

    page_no += 1
    while page_no <= num_pages:
        URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=' \
              f'{zip_code}&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel' \
              f'&distance={distance}&entitySelectingHelper.selectedEntity2={max_year_id}&sortType=AGE_IN_DAYS&' \
              f'entitySelectingHelper.selectedEntity={min_year_id}{max_mileage_str}{transmission_str}' \
              f'#resultsPage={page_no}'

        page = requests.get(URL)
        soup = BeautifulSoup(page, 'html.parser')
        scripts = soup.find_all('script')
        listings = ''
        for script in scripts:
            if 'window.__PREFLIGHT__ = ' in str(script):
                listings = str(script)
                break
        listings = listings.split(' window.__PREFLIGHT__')[1].strip()[2:-1]
        listings = json.loads(listings)
        listings = listings['listings']
    return None


test = get_model_id('m42')
print(json.dumps(test, indent=3))
