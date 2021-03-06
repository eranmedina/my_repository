#!/usr/bin/env python
import os
import logging
import time
import glob
from banks.base_wps import BaseWps
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

script_path = os.path.abspath(__file__)
script_folder = os.path.dirname(script_path)
screenshots_folder = os.path.join(script_folder, 'Screesnshots')
downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')


class Otsar(BaseWps):
    def __init__(self, driver, opt_dict, bank_dict):
        super(Otsar, self).__init__(driver, opt_dict, bank_dict)

    def login(self):
        logging.info('Login started')
        frame = self.driver.find_element_by_id('LoginIframeTag')
        self.driver.switch_to.frame(frame)
        self.driver.find_element_by_id('username').send_keys(''.join(self.opt_dict['cred'][1:][::3]))
        self.driver.find_element_by_id('password').send_keys(''.join(self.opt_dict['cred'][0:][::3]))
        self.driver.find_element_by_id('login_btn').click()
        # WebDriverWait(driver, 15).until(ec.presence_of_element_located((By.CLASS_NAME, 'fibi_branch')))
        # WebDriverWait(driver, 15).until(ec.presence_of_element_located((By.CLASS_NAME, 'acc_num')))

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
