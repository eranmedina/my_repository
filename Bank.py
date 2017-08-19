#!/usr/bin/env python

import json
from argparse import ArgumentParser
from collections import defaultdict
import sys
import os
import logging
import traceback
import glob

from selenium import webdriver

script_path = os.path.abspath(__file__)
script_folder = os.path.dirname(script_path)
sys.path.append(os.path.join(script_folder, 'Packages'))  # Adding Packages folder to system path
screenshots_folder = os.path.join(script_folder, 'Screesnshots')
output_folder = os.path.join(script_folder, 'Output')
downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-infobars')
driver_folder = os.path.join(downloads_folder, 'chromedriver.exe')
driver = webdriver.Chrome(driver_folder, chrome_options=chrome_options)
driver.implicitly_wait(30)

from otsar import Otsar
from leumi import Leumi
from poalim import Poalim
from discont import Discont
from igud import Igud

logging.root.handlers = []
log_format = '[%(asctime)s]| %(levelname)-7s| %(message)-100s| {%(name)s|%(funcName)s|%(lineno)-3s}'
date_format = '%d-%m-%Y %H:%M:%S'
logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=date_format, filename='bank.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(log_format, datefmt=date_format)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)
# caps = chrome_options.to_capabilities()
# driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=caps)

bank_dict = {
        '10': {'name': 'leumi', 'url': 'https://hb2.bankleumi.co.il', 'title': 'בנק לאומי'},
        #'11': {'name': 'discont', 'url': 'https://www.discountbank.co.il', 'title': 'בנק דיסקונט'},
        '11': {'name': 'discont', 'url': 'https://start.telebank.co.il/LoginPages/Logon', 'title': 'בנק דיסקונט לישראל'},
        '12': {'name': 'poalim', 'url': 'https://www.bankhapoalim.co.il', 'title': 'בנק הפועלים'},
        '13': {'name': 'igud', 'url': 'https://hb.unionbank.co.il', 'title': 'כניסה לחשבונך'},
        '14': {'name': 'otsar', 'url': 'https://online.bankotsar.co.il/wps/portal', 'title': 'בנק אוצר החייל'},
        #'17': {'name': 'marcantil', 'url': 'https://online.bankotsar.co.il/wps/portal', 'title': 'בנק לאומי'},
        #'20': {'name': 'mizrahi', 'url': 'https://online.bankotsar.co.il/wps/portal', 'title': 'בנק לאומי'},
        #'26': {'name': 'ubank', 'url': 'https://online.bankotsar.co.il/wps/portal', 'title': 'בנק לאומי'},
        #'31': {'name': 'benleumi', 'url': 'https://online.bankotsar.co.il/wps/portal', 'title': 'בנק לאומי'},
        #'46': {'name': 'masad', 'url': 'https://online.bankotsar.co.il/wps/portal', 'title': 'בנק לאומי'},
        #'54': {'name': 'jerusalem', 'url': 'https://online.bankotsar.co.il/wps/portal', 'title': 'בנק לאומי'}
}


def main():
    parser = ArgumentParser()
    parser.add_argument('--bank_code', dest='bank_code', default=10, help='', metavar='(string)')
    parser.add_argument('--user_name', dest='user_name', default=None, help='', metavar='(string)')
    parser.add_argument('--user_id', dest='user_id', default=None, help='', metavar='(string)')
    parser.add_argument('--pass', dest='pass', default=None, help='', metavar='(string)')
    parser.add_argument('--cred', dest='cred', default=None, help='', metavar='(string)')
    parser.add_argument('--ident_code', dest='ident_code', default=None, help='', metavar='(string)')
    parser.add_argument('--branch_no', dest='branch_no', default=None, help='', metavar='(string)')
    parser.add_argument('--account_no', dest='account_no', default=None, help='', metavar='(string)')
    parser.add_argument('--date_from', dest='date_from', default=None, help='', metavar='(string)')
    parser.add_argument('-m', dest='maximize', default=False, help='Maximize browser', action='store_true')
    opt_dict = vars(parser.parse_args())
    none_set = {key for key in opt_dict if opt_dict[key] is None and key not in ('a', 'b')}
    if none_set:
        parser.print_help()
        raise ValueError('Missing arguments: %s' % list(none_set))

    try:
        if not os.path.exists(os.path.join(downloads_folder, 'old')):
            os.mkdir(os.path.join(downloads_folder, 'old'))
            logging.info('Creating old folder in %s' % downloads_folder)
        for file in glob.glob(os.path.join(downloads_folder, '*.xls')):
            os.rename(file, os.path.join(downloads_folder, 'old', os.path.basename(file)))
            logging.info('Move previous excel file to old folder - %s' % file)

        if opt_dict['maximize']:
            logging.info('Maximizing browser')
            driver.maximize_window()
        else:
            driver.set_window_position(-2000, 0)

        bank_module = eval(bank_dict[opt_dict['bank_code']]['name'].title())
        bank = bank_module(driver, opt_dict, bank_dict)
        bank.navigate_to_login()
        bank.login()
        bank.navigate_to_last_trxs()
        bank.show_last_trxs()
        file = bank.export_last_trxs()
        res_dict = read_data_from_excel(file)
        dump_json(res_dict, bank.name)

        # Read data from table
        # all_rows = table.find_elements_by_tag_name("tr")
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

    except Exception as e:
        logging.info('%s: %s\n%s' % (e.__class__.__name__, e, traceback.format_exc()))
    finally:
        driver.quit()


def read_data_from_excel(file):
    logging.info('Reading data from excel file')
    results_dict = defaultdict(dict)
    col_headers = []
    with open(os.path.join(downloads_folder, file)) as f:
        for row_num, row_data in enumerate(f):
            if row_num == 0:  # headers row
                col_headers = [col.strip() for col in row_data.split('\t')]
            elif row_num > 1:  # data rows
                row_data = [col.strip() for col in row_data.split('\t')]
                for col_num, col_data in enumerate(row_data[:-1]):
                    results_dict[row_num - 1]['%s' % col_headers[col_num]] = col_data
    return results_dict


def dump_json(res_dict, bank_name):
    logging.info('Creating JSON dump')
    output_path = os.path.join(output_folder, 'bank_%s_output.json' % bank_name)
    with open(output_path, "w") as f:
        json.dump(res_dict, f, ensure_ascii=False, sort_keys=True, indent=4, )
    f.close()

    logging.info('JSON file was created successfully - %s' % output_path)

if __name__ == '__main__':
    sys.exit(main())
