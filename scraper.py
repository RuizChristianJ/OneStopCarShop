## This file will be used to scrape the car gurus webpages for the data.

import requests
import json
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import math

zip_code = '06066'
distance = ['10', '25', '50', '75', '100', '150', '200', '500', '50000']
transmission = ['', '&transmission=']
transmission_type = ['A', 'M']
max_mileage = ['', '&maxMileage=']
mileage = '50000'
max_year = 'c27605'
min_year = 'c24781'

URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=' \
      f'{zip_code}&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel&distance={distance[8]}&' \
      f'entitySelectingHelper.selectedEntity2={max_year}&sortType=AGE_IN_DAYS&' \
      f'entitySelectingHelper.selectedEntity={min_year}{max_mileage[1]}{mileage}{transmission[1]}{transmission_type[1]}'

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




