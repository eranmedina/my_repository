#!/usr/bin/env python
import os
import logging
import time
import glob
import csv
from collections import defaultdict
from banks.base_bank import BaseBank
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

script_path = os.path.abspath(__file__)
script_folder = os.path.dirname(script_path)
screenshots_folder = os.path.join(script_folder, 'Screesnshots')
downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')


class BaseWps(BaseBank):
    def __init__(self, driver, opt_dict, bank_dict):
        super(BaseWps, self).__init__(driver, opt_dict, bank_dict)

    def navigate_to_login(self):
        super(BaseWps, self).navigate_to_login(sync_obj='LoginIframeTag')

    def login(self):
        logging.info('Login started')
        frame = self.driver.find_element_by_id('LoginIframeTag')
        self.driver.switch_to.frame(frame)
        self.driver.find_element_by_id('username').send_keys(self.opt_dict['user'])
        self.driver.find_element_by_id('password').send_keys(self.opt_dict['pass'])
        self.driver.find_element_by_id('login_btn').click()
        # WebDriverWait(driver, 15).until(ec.presence_of_element_located((By.CLASS_NAME, 'fibi_branch')))
        # WebDriverWait(driver, 15).until(ec.presence_of_element_located((By.CLASS_NAME, 'acc_num')))

        super(BaseWps, self).login()

    def navigate_to(self, page):
        pages_dict = {
            'last_trxs': {'url': 'OnAccountMngment/OnlnAccMostUsed/OnMUPrivAccFlow', 'by_type': 'class_name', 'by_val': 'dates_range'},
            'credit_cards': {'url': 'OnCreditCardsMenu/OnlnCCMostUsed/OnMUCCChrgDetF', 'by_type': 'class_name', 'by_val': 'normal_select'},
            'loans': {'url': 'OnLoansMortgageMenu/OnlnLoanMostUsed/OnMULoanDets'}
        }

        logging.info('Navigate to %s page' % page)
        self.driver.get("%s/%s" % (self.main_url, pages_dict[page]['url']))
        if 'by_type' in pages_dict[page] and 'by_val' in pages_dict[page]:
            if pages_dict[page]['by_type'] == 'class_name':
                WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, pages_dict[page]['by_val'])))  # list of credit cards
            elif pages_dict[page]['by_type'] == 'id':
                    WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.ID, pages_dict[page]['by_val'])))  # list of credit cards
            elif pages_dict[page]['by_type'] == 'css':
                    WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, pages_dict[page]['by_val'])))  # list of credit cards

    def show_last_trxs(self):
        logging.info('Showing last trxs started')
        if self.opt_dict['date_from']:
            logging.info('Entering start date')
            self.driver.find_element_by_class_name("dates_range").click()
            self.driver.find_element_by_id("fromDate").clear()
            self.driver.find_element_by_id("fromDate").send_keys(self.opt_dict['date_from'])
        if self.opt_dict['date_to']:
            logging.info('Entering end date')
            self.driver.find_element_by_id("tillDate").clear()
            self.driver.find_element_by_id("tillDate").send_keys(self.opt_dict['date_to'])

        logging.info('Clicking on show results')
        self.driver.find_elements_by_class_name("fibi_btn")[0].click()  # show results
        logging.info('Showing last trxs finished')

    def export_data_click(self):
        logging.info('Clicking on export results')
        WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'a.excell')))
        self.driver.find_element_by_css_selector('a.excell').click()  # export to csv

    def export_data(self):
        self.export_data_click()

        files = []
        for i in range(10):  # waiting for excel export production
            files = glob.glob(os.path.join(downloads_folder, '*.csv'))
            if len(files) == 1:
                break
            time.sleep(1)
            logging.info('Exporting results to excel - %d seconds' % i)

        if len(files) == 0:
            raise RuntimeError('Failed to export data to excel file')
        logging.info('Exporting last trxs finished')
        return files[0]

    def read_last_trxs_from_excel(self, file):
        logging.info('Reading data from excel file')
        self.results_dict['last_trxs'] = defaultdict(dict)
        col_headers = []
        with open(os.path.join(downloads_folder, file)) as f:
            for row_num, row_data in enumerate(f):
                if row_num > 0:  # data rows
                    row_data = [col.strip() for col in row_data[1:-3].split('\",\"')]
                    for col_num, col_data in enumerate(row_data):
                        self.results_dict['last_trxs'][row_num]['%s' % col_headers[col_num]] = col_data
                elif row_num == 0:  # headers row
                    col_headers = [col.strip() for col in row_data[1:-3].split('\",\"')]
        os.remove(os.path.join(downloads_folder, file))
        # Read data from table
        # all_rows = driver.find_elements_by_tag_name("tr")
        # for row in all_rows:
        #   cells = row.find_elements_by_tag_name("td")
        #   dict_value = {'0th': cells[0].text}

        # table = driver.find_element_by_id("dataTable077")
        # row = 1
        # col_headers = {0: 'date', 1: 'desc', 2: 'id', 3: 'plus', 4: 'minus', 5: 'balance'}
        # for i, cell in enumerate(table.find_elements_by_tag_name("td")):
        #     results_dict[row]['%s' % col_headers[i % 6]] = cell.text
        #     if i > 0 and (i+1) % 6 == 0:
        #         row += 1

    def read_credit_cards_charges_from_excel(self, file):
        logging.info('Reading data from excel file')
        #self.results_dict['credit_cards_charges'] = defaultdict(dict)
        last_row_data = ''
        with open(os.path.join(downloads_folder, file)) as f:
            for row_num, row_data in enumerate(f):
                if row_num > 8 and 'חיובים עתידיים' in row_data:
                    last_row_data = row_data.strip().split('\"')[3]
        self.results_dict['credit_cards_charges'] = last_row_data
        os.remove(os.path.join(downloads_folder, file))

    def read_loans_from_excel(self, file):
        logging.info('Reading data from excel file')
        #self.results_dict['credit_cards_charges'] = defaultdict(dict)
        last_row_data = ''
        with open(os.path.join(downloads_folder, file)) as f:
            for row_num, row_data in enumerate(f):
                if row_num > 8 and 'חיובים עתידיים' in row_data:
                    last_row_data = row_data.strip().split('\"')[3]
        self.results_dict['loans'] = last_row_data
        os.remove(os.path.join(downloads_folder, file))
