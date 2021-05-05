import os
import shutil
import logging
from selenium import webdriver
import json
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import math
from enum import Enum
import random
import uuid

logger = logging.getLogger()

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


class WebDriverWrapper:
    def __init__(self):

        chrome_options = webdriver.ChromeOptions()
        # self._tmp_folder = '/tmp/{}'.format(uuid.uuid4())
        #
        # if not os.path.exists(self._tmp_folder):
        #     os.makedirs(self._tmp_folder)
        #
        # if not os.path.exists(self._tmp_folder + '/user-data'):
        #     os.makedirs(self._tmp_folder + '/user-data')
        #
        # if not os.path.exists(self._tmp_folder + '/data-path'):
        #     os.makedirs(self._tmp_folder + '/data-path')
        #
        # if not os.path.exists(self._tmp_folder + '/cache-dir'):
        #     os.makedirs(self._tmp_folder + '/cache-dir')

        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280x1696')
        # chrome_options.add_argument('--user-data-dir={}'.format(self._tmp_folder + '/user-data'))
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        chrome_options.add_argument('--v=99')
        chrome_options.add_argument('--single-process')
        # chrome_options.add_argument('--data-path={}'.format(self._tmp_folder + '/data-path'))
        chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--homedir={}'.format(self._tmp_folder))
        # chrome_options.add_argument('--disk-cache-dir={}'.format(self._tmp_folder + '/cache-dir'))
        # chrome_options.add_argument(
        #     'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

        BIN_DIR = "/tmp/bin"
        # BIN_DIR = "/usr/bin"
        CURR_BIN_DIR = "/var/task/bin"

        if not os.path.exists(BIN_DIR):
            os.makedirs(BIN_DIR)
        currfile = os.path.join(CURR_BIN_DIR, "headless-chromium")
        newfile = os.path.join(BIN_DIR, "headless-chromium")
        shutil.copy2(currfile, newfile)
        os.chmod(newfile, 0o777)
        currfile = os.path.join(CURR_BIN_DIR, "chromedriver")
        newfile = os.path.join(BIN_DIR, "chromedriver")
        shutil.copy2(currfile, newfile)
        os.chmod(newfile, 0o777)

        chrome_options.binary_location = "/tmp/bin/headless-chromium"
        self._driver = webdriver.Chrome(chrome_options=chrome_options)

    def get_soup_group(self, url: str):
        """
        Returns the soup from BeautifulSoup for the given URL.

        :param url: URL to return the soup for
        :return: soup of the URL
        """

        self._driver.get(url)
        sleep_timer = random.randint(3, 15)
        time.sleep(sleep_timer)
        page = self._driver.page_source
        self._driver.quit()
        soup = BeautifulSoup(page, 'html.parser')

        return soup

    def get_selection(self, soup, selection_type: SelectionEnum, grouping: str):
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

    def clean_selection(self, selection: str):
        """
        Cleans dictionary represented as a string and transforms into a proper dictionary.
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
            selection_dict[ssplit[1]] = ssplit[0]
            # selection_dict[ssplit[0]] = ssplit[1]
        return selection_dict

    def get_make_id(self, selection_type: SelectionEnum):
        """
        Get all or 'popular' make id's from cargurus.

        :param selection_type: Enum indicating to return all or just 'popular' makes
        :return: A dict where the keys are the make names and the values are the carguru's ID.
        """
        if selection_type not in [SelectionEnum.allMakes, SelectionEnum.popMakes]:
            raise KeyError

        make_url = f'https://www.cargurus.com'

        soup = self.get_soup_group(make_url)
        makes = self.get_selection(soup, selection_type, 'optgroup')
        makes = self.clean_selection(makes[0])

        return makes

    def get_model_id(self, make_id: str = None):
        """
        Get all model id's from cargurus.

        :param make_id: The carguru's make ID.
        :return: A dict where the keys are the model names and the values are the carguru's ID.
        """
        make_url = f'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?' \
                   f'sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity={make_id}'

        soup = self.get_soup_group(make_url)
        models = self.get_selection(soup, SelectionEnum.Models, 'optgroup')
        models_dict = self.clean_selection(models[0])
        models_dict.update(self.clean_selection(models[1]))
        # models_dict = {make_id: models_dict}

        return models_dict


if __name__ == '__main__':
    create_makes = True
    # create_models = True
    # create_years = False
    # test_year = 'm42'

    driver = WebDriverWrapper()
    if create_makes:
        makes = driver.get_make_id(SelectionEnum.allMakes)
        with open('../makes.json', 'w') as outfile:
            json.dump(makes, outfile, indent=3)
    else:
        with open('../makes.json') as f:
            makes = json.load(f)

    makes_keys = makes.keys()
    print(makes_keys)
