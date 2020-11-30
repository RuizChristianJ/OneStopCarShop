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


# zip_code = '06066'
# distance = ['10', '25', '50', '75', '100', '150', '200', '500', '50000']
# transmission = ['', '&transmission=']
# transmission_type = ['A', 'M']
# max_mileage = ['', '&maxMileage=']
# mileage = '50000'
# max_year = 'c27605'
# min_year = 'c24781'
#
#
# make_id_URL = f'https://www.cargurus.com'
# # model_id_URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?' \
# #               f'sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity={make_id}'
# query_URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=' \
#       f'{zip_code}&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel&distance={distance[8]}&' \
#       f'entitySelectingHelper.selectedEntity2={max_year}&sortType=AGE_IN_DAYS&' \
#       f'entitySelectingHelper.selectedEntity={min_year}{max_mileage[1]}{mileage}{transmission[1]}{transmission_type[1]}'


class SelectionEnum(Enum):
    """
    Enum class for html parsing
    """
    allMakes = 'All Makes'
    popMakes = 'Popular Makes'

    Models = ('Popular Models', 'Other Models')

    allYears = 'All Years'

    Listing = 'window.__PREFLIGHT__ = '

    pageNo = 'page-navigation-number-of-listings'


def get_soup_group(url: str):
    """
    Returns the soup from BeautifulSoup for the given URL.

    :param url: URL to return the soup for
    :return: soup of the URL
    """
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

    return soup


def get_selection(soup, selection_type: SelectionEnum, grouping: str):
    """
    Gets the string representation of a dict from the soup group containing the specified strings.
    i.e. gets the string containing make name and id's to be cleaned into proper dict.

    :param soup: soup from using the get_soup_group method on specified URL.
    :param selection_type: Enum object for parsing html is soup.
    :param grouping: String to find in soup object.
    :return: String representation of dict to be cleaned.
    """
    groups = soup.find_all(grouping)
    if len(groups) == 0:
        raise KeyError

    selection = []
    if selection_type == SelectionEnum.Models:
        for i in range(0, len(selection_type.value)):
            for group in groups:
                if selection_type.value[i] in str(group):
                    selection.append(str(group))
                    break
        return selection
    else:
        for group in groups:
            if selection_type.value in str(group):
                selection.append(str(group))
                break
        return selection


def clean_selection(selection: str):
    """
    Cleans dict represented as string and transforms into a dictionary.
    Used for the make and model ID's.

    :param selection: Unclean, string representation of dict. Returned from get_selection().
    :return: Cleaned dictionary parsed from the selection string.
    """
    selection_cleaned = selection.split('option value=')
    for i in range(0, len(selection_cleaned)):
        selection_cleaned[i] = selection_cleaned[i].replace('"', '')
        selection_cleaned[i] = selection_cleaned[i].replace('>', ' ')
        selection_cleaned[i] = selection_cleaned[i].split('<')[0]
    selection_cleaned = selection_cleaned[1:]
    selection_dict = dict()
    for value in selection_cleaned:
        ssplit = value.split(' ', 1)
        selection_dict[ssplit[0]] = ssplit[1]
    return selection_dict


def get_make_id(selection_type: SelectionEnum):
    """
    Get all or 'popular' make id's from cargurus.

    :param selection_type: Enum indicating to return all or just 'popular' makes
    :return: A dict where the keys are the make names and the values are the carguru's ID.
    """
    if selection_type not in [SelectionEnum.allMakes, SelectionEnum.popMakes]:
        raise KeyError

    make_url = f'https://www.cargurus.com'

    soup = get_soup_group(make_url)
    makes = get_selection(soup, selection_type, 'optgroup')
    makes = clean_selection(makes[0])

    return makes


def get_model_id(make_id: str = None):
    """
    Get all model id's from cargurus.

    :param make_id: The carguru's make ID.
    :return: A dict where the keys are the model names and the values are the carguru's ID.
    """
    make_url = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?' \
                f'sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity={make_id}'

    soup = get_soup_group(make_url)
    models = get_selection(soup, SelectionEnum.Models, 'optgroup')
    models_dict = clean_selection(models[0])
    models_dict.update(clean_selection(models[1]))
    # models_dict = {make_id: models_dict}

    return models_dict


def get_year_id(model_id: str = None):
    """
    Get all year id's from cargurus for the specified model.

    :param model_id: The carguru's model ID.
    :return: A dict where the keys are the years and the values are the carguru's ID.
    """
    model_url = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?' \
                f'sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity={model_id}'

    soup = get_soup_group(model_url)
    years = get_selection(soup, SelectionEnum.allYears, 'select')
    years = clean_selection(years[0])

    return years


def get_listings(soup):
    """
    Gets the car listings from the provided soup.

    :param soup: Soup returned from 'get_soup_group()' after being provided query URL
    :return: A dict containing the ID's for the lisitng as keys and the listing details as the values.
    """
    listings_dict = {'id': {}}
    scripts = soup.find_all('script')
    listings = ''
    for script in scripts:
        if 'window.__PREFLIGHT__ = ' in str(script):
            listings = str(script)
            break
    listings = listings.split(' window.__PREFLIGHT__')[1].strip()[2:-1]
    listings = json.loads(listings)
    listings = listings['listings']
    for listing in listings:
        listing_keys = list(listing.keys())
        listings_dict['id'][listing['id']] = {key: listing[key] for key in listing_keys[1:]}
    return listings_dict


# def get_car_data(zip: str, min_year_id: str, max_year_id: str, distance: int, transmission: str=None,
#                  max_mileage: str=None):
#
#     page_no = 1
#     transmission_str = ''
#     max_mileage_str = ''
#     if transmission is not None:
#         transmission_str = f'&transmission={transmission}'
#     if max_mileage is not None:
#         max_mileage_str = f'&maxMileage={max_mileage}'
#
#     URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=' \
#           f'{zip_code}&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel' \
#           f'&distance={distance}&entitySelectingHelper.selectedEntity2={max_year_id}&sortType=AGE_IN_DAYS&' \
#           f'entitySelectingHelper.selectedEntity={min_year_id}{max_mileage_str}{transmission_str}#resultsPage={page_no}'
#
#     options = Options()
#     options.add_argument('--headless')
#     options.add_argument('--disable-gpu')
#     driver = webdriver.Chrome(chrome_options=options, executable_path=r"C:\bin\chromedriver_win32\chromedriver.exe")
#     driver.get(URL)
#     time.sleep(3)
#     page = driver.page_source
#     driver.quit()
#     soup = BeautifulSoup(page, 'html.parser')
#
#     listings = get_listings(soup)
#
#     span = soup.find_all('span')
#
#     num_listings = 0
#     for val in span:
#         if 'page-navigation-number-of-listings' in str(val):
#             num_listings = int(str(val).split('<strong>')[-1].split('<')[0])
#             break
#
#     num_pages = 0
#     if num_listings > 0:
#         num_pages = math.ceil(num_listings/15.0)
#
#     page_no += 1
#     while page_no <= num_pages:
#         URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=' \
#               f'{zip_code}&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel' \
#               f'&distance={distance}&entitySelectingHelper.selectedEntity2={max_year_id}&sortType=AGE_IN_DAYS&' \
#               f'entitySelectingHelper.selectedEntity={min_year_id}{max_mileage_str}{transmission_str}' \
#               f'#resultsPage={page_no}'
#
#         page = requests.get(URL)
#         soup = BeautifulSoup(page, 'html.parser')
#         scripts = soup.find_all('script')
#         listings = ''
#         for script in scripts:
#             if 'window.__PREFLIGHT__ = ' in str(script):
#                 listings = str(script)
#                 break
#         listings = listings.split(' window.__PREFLIGHT__')[1].strip()[2:-1]
#         listings = json.loads(listings)
#         listings = listings['listings']
#     return None


# test = get_model_id('m42')
# test = get_year_id('d215')
# test = get_listings(get_soup_group('https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=06066&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel&distance=50&sortType=DEAL_SCORE&entitySelectingHelper.selectedEntity=d214'))
# print(json.dumps(test, indent=3))
# print(len(test))

if __name__ == '__main__':
    create_makes = False
    create_models = False
    create_years = False
    test_year = 'm42'

    if create_makes:
        makes = get_make_id(SelectionEnum.popMakes)
        with open('makes.json', 'w') as outfile:
            json.dump(makes, outfile, indent=3)
    else:
        with open('makes.json') as f:
            makes = json.load(f)

    makes_keys = makes.keys()

    if create_models:
        models_dict = dict()
        for key in makes_keys:
            models = get_model_id(key)
            models_dict[key] = models
        with open('models.json', 'w') as outfile:
            json.dump(models_dict, outfile, indent=3)
    else:
        with open('models.json') as f:
            models_dict = json.load(f)

    if create_years:
        years_dict = dict()
        if test_year is not None:
            models_keys = models_dict[test_year].keys()
            for model_id in models_keys:
                years = get_year_id(model_id)
                years_dict[model_id] = years
            with open('mazda_years.json', 'w') as outfile:
                json.dump(years_dict, outfile, indent=3)
