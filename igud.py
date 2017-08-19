# !/usr/bin/env python
import os
import logging
import time
import glob

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

script_path = os.path.abspath(__file__)
script_folder = os.path.dirname(script_path)
screenshots_folder = os.path.join(script_folder, 'Screesnshots')
downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')


class Igud(object):
    def __init__(self, driver, opt_dict, bank_dict):
        """Return a Bank object whose name is *name*."""
        self.driver = driver
        self.name = bank_dict[opt_dict['bank_code']]['name']
        self.url = bank_dict[opt_dict['bank_code']]['url']
        self.title = bank_dict[opt_dict['bank_code']]['title']
        self.opt_dict = opt_dict

    def navigate_to_login(self):
        logging.info('Navigate to login started')
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.ID, 'login')))
        assert self.title in self.driver.title
        logging.info('Navigate to login finished')

    def login(self):
        logging.info('Login started')
        self.driver.find_element_by_id('uid').send_keys(self.opt_dict['user_name'])
        self.driver.find_element_by_id('password').send_keys(self.opt_dict['pass'])
        self.driver.find_element_by_id('enter').click()

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

    def navigate_to_last_trxs(self):
        logging.info('Navigate to last trxs started')
        self.driver.get("%s/OnAccountMngment/OnlnAccMostUsed/OnMUPrivAccFlow" % self.driver.current_url)
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, 'dates_range')))
        logging.info('Navigate to last trxs finished')

    def show_last_trxs(self):
        logging.info('Showing last trxs started')
        if self.opt_dict['date_from']:
            logging.info('Entering start date')
            self.driver.find_element_by_class_name("dates_range").click()
            self.driver.find_element_by_id("fromDate").clear()
            self.driver.find_element_by_id("fromDate").send_keys(self.opt_dict['date_from'])

        logging.info('Clicking on show results')
        self.driver.find_elements_by_class_name("fibi_btn")[0].click()  # show results
        logging.info('Showing last trxs finished')

    def export_last_trxs(self):
        logging.info('Exporting last trxs started')
        logging.info('Clicking on export results')
        self.driver.find_elements_by_class_name("fibi_btn")[1].click()  # export to xls

        files = []
        for i in range(10):  # waiting for excel export production
            files = glob.glob(os.path.join(downloads_folder, '*.xls'))
            if len(files) == 1:
                break
            time.sleep(1)
            logging.info('Exporting results to excel - %d seconds' % i)

        if len(files) == 0:
            raise RuntimeError('Failed to export data to excel file')
        logging.info('Exporting last trxs finished')
        return files[0]
