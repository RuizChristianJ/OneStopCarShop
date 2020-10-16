## This file will be used to scrape the car gurus webpages for the data.

import requests
import json
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=options, executable_path=r"C:\bin\chromedriver_win32\chromedriver.exe")
driver.get(URL)
time.sleep(3)
page = driver.page_source
driver.quit()
soup = BeautifulSoup(page, 'html.parser')

script = soup.find_all('script')

listings = ''
counter = 0
while listings == '':
    if 'window.__PREFLIGHT__ = ' in str(script[counter]):
        listings = str(script[counter])
    counter += 1

# listings = listings.split(' window.__PREFLIGHT__')[1].strip()[2:-1]
# listings = json.loads(listings)
# listings = listings['listings']

span = soup.find_all('span')

for val in span:
    if 'page-navigation-number-of-listings' in str(val):
        print(val)
        break
