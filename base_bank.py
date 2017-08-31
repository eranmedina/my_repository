# !/usr/bin/env python
import os
import logging
import time
from collections import defaultdict
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

script_path = os.path.abspath(__file__)
script_folder = os.path.dirname(script_path)
screenshots_folder = os.path.join(script_folder, 'Screesnshots')
downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')


class BaseBank(object):
    def __init__(self, driver, opt_dict, bank_dict):
        """Return a Bank object whose name is *name*."""
        self.driver = driver
        self.name = bank_dict[opt_dict['bank_code']]['name']
        self.login_url = bank_dict[opt_dict['bank_code']]['login_url']
        self.main_url = bank_dict[opt_dict['bank_code']]['main_url']
        self.title = bank_dict[opt_dict['bank_code']]['title']
        self.opt_dict = opt_dict
        self.results_dict = defaultdict(dict)
        self.results_dict['user_data']['account_no'] = opt_dict['account_no']
        self.results_dict['user_data']['branch_no'] = opt_dict['branch_no']
        self.results_dict['user_data']['bank_code'] = opt_dict['bank_code']

    def login(self):
        pass

    def navigate_to_login(self, **kwargs):
        logging.info('Navigate to login started')
        self.driver.get(self.login_url)
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.ID, kwargs['sync_obj'])))
        assert self.title in self.driver.title
        logging.info('Navigate to login finished')

    def verify_login(self):
        body_text = ''
        for i in range(10):  # waiting for excel export production
            body_text = self.driver.find_element_by_tag_name('body').text
            if 'מספר חשבון' in body_text:
                logging.info('Login succeeded')
                break
            logging.debug('Waiting for page load')
            time.sleep(1)

        if 'מספר חשבון' not in body_text:
            self.driver.save_screenshot(os.path.join(screenshots_folder, 'login_failed.png'))
            raise RuntimeError('Login failed')
        elif self.opt_dict['account_no'] not in body_text or self.opt_dict['branch_no'] not in body_text:
            self.driver.save_screenshot(os.path.join(screenshots_folder, 'login_wrong.png'))
            raise ValueError('Wrong branch/account - %s/%s' % (self.opt_dict['branch_no'], self.opt_dict['account_no']))

    logging.info('Login finished')
