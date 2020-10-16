## This file will be used to scrape the car gurus webpages for the data.

import requests
import json
from bs4 import BeautifulSoup

zip_code = '06066'
distance = ['10', '25', '50', '75', '100', '150', '200', '500', '50000']
transmission = ['', '&transmission=']
transmission_type = ['A', 'M']
max_mileage = ['', '&maxMileage=']
mileage = '50000'
max_year = 'c27605'
min_year = 'c24781'

URL = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=' \
      f'{zip_code}&showNegotiable=true&sortDir=ASC&sourceContext=carGurusHomePageModel&distance={distance[-1]}&' \
      f'entitySelectingHelper.selectedEntity2={max_year}&sortType=AGE_IN_DAYS&' \
      f'entitySelectingHelper.selectedEntity={min_year}{max_mileage[1]}{mileage}{transmission}{transmission_type[1]}'

page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

script = soup.find_all('script')

listings = ''
counter = 0
while listings == '':
    if 'window.__PREFLIGHT__ = ' in str(script[counter]):
        listings = str(script[counter])
    counter += 1

listings = listings.split(' window.__PREFLIGHT__')[1].strip()[2:-1]
listings = json.loads(listings)
listings = listings['listings']
