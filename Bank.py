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

# --bank_code 12 --user_name 123 --pass 6879Focus08 --cred oVatNbs8ca3dr7820f05g --date_from 01/06/2017 --date_to 01/08/2017 --branch_no 547 --account_no 225156 -m
# --bank_code 14 --user_name 123 --pass 456 --cred oVatNbs2ca8dr8e42f05g0 --date_from 01/06/2017 --branch_no 363 --account_no 646462 -m

script_path = os.path.abspath('__file__')
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


from banks.otsar import Otsar
from banks.poalim import Poalim
#from banks.leumi import Leumi
#from banks.poalim import Poalim
#from banks.discont import Discont
#from banks.igud import Igud
#from banks.benleumi import Benleumi
#from banks.marcantil import Marcantil
#from banks.mizrahi_tefahot import Mizrahi_Tefahot
#from banks.ubank import Ubank
#from banks.masad import Masad
#from banks.jerusalem import Jerusalem
#from banks.yahav import Yahav

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
        '12': {'name': 'poalim', 'login_url': 'https://www.bankhapoalim.co.il', 'title': 'בנק הפועלים', 'main_url': 'https://login.bankhapoalim.co.il/portalserver'},
        '20': {'name': 'mizrahi_tefahot', 'login_url': 'https://www.mizrahi-tefahot.co.il', 'title': 'מזרחי-טפחות'},
        '04': {'name': 'yahav', 'login_url': 'https://www.bank-yahav.co.il', 'title': 'בנק יהב'},
        '54': {'name': 'jerusalem', 'login_url': 'https://services.bankjerusalem.co.il/Pages/Login.aspx', 'title': 'בנק ירושלים'},

        '14': {'name': 'otsar', 'login_url': 'https://online.bankotsar.co.il/wps/portal', 'main_url': 'https://online.bankotsar.co.il/wps/myportal/FibiMenu/Online', 'title': 'בנק אוצר החייל'},
        '26': {'name': 'ubank', 'login_url': 'https://online.u-bank.net/wps/portal', 'title': 'U-Bank'},
        '46': {'name': 'masad', 'login_url': 'https://online.bankmassad.co.il/wps/portal', 'title': 'בנק מסד'},
        '31': {'name': 'benleumi', 'login_url': 'https://online.fibi.co.il/wps/portal', 'title': 'הבנק הבינלאומי'},

        #'11': {'name': 'discont', 'login_url': 'https://www.discountbank.co.il', 'title': 'בנק דיסקונט'},
        '11': {'name': 'discont', 'login_url': 'https://start.telebank.co.il/LoginPages/Logon?bank=d', 'title': 'בנק דיסקונט לישראל'},
        '17': {'name': 'marcantil', 'login_url': 'https://start.telebank.co.il/LoginPages/Logon?bank=m', 'title': 'מרכנתיל'},

        '10': {'name': 'leumi', 'login_url': 'https://hb2.bankleumi.co.il', 'title': 'בנק לאומי'},
        '13': {'name': 'igud', 'login_url': 'https://hb.unionbank.co.il', 'title': 'כניסה לחשבונך'}
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
    parser.add_argument('--date_to', dest='date_to', default=None, help='', metavar='(string)')
    parser.add_argument('-m', dest='maximize', default=False, help='Maximize browser', action='store_true')
    opt_dict = vars(parser.parse_args())
    none_set = {key for key in opt_dict if opt_dict[key] is None and key not in ('user_id', 'cred', 'ident_code', 'date_to')}
    if none_set:
        parser.print_help()
        raise ValueError('Missing arguments: %s' % list(none_set))

    try:
        delete_previous_files()

        if opt_dict['maximize']:
            logging.info('Maximizing browser')
            driver.maximize_window()
        else:
            driver.set_window_position(-2000, 0)

        bank_module = eval(bank_dict[opt_dict['bank_code']]['name'].title())
        bank = bank_module(driver, opt_dict, bank_dict)
        bank.navigate_to_login()
        bank.login()
        bank.navigate_to('last_trxs')
        bank.show_last_trxs()
        file = bank.export_data()
        bank.read_last_trxs_from_excel(file)
        bank.navigate_to('credit_cards')
        file = bank.export_data()
        bank.read_credit_cards_charges_from_excel(file)
        bank.navigate_to('loans')
        file = bank.export_data()
        bank.read_loans_from_excel(file)
        dump_json(bank.results_dict, bank.name)

    except Exception as e:
        logging.info('%s: %s\n%s' % (e.__class__.__name__, e, traceback.format_exc()))
    finally:
        driver.quit()


def dump_json(res_dict, bank_name):
    logging.info('Creating JSON dump')
    #return json.dump(res_dict)
    output_path = os.path.join(output_folder, 'bank_%s_output.json' % bank_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with open(output_path, "w") as f:
        json.dump(res_dict, f, ensure_ascii=False, sort_keys=True, indent=4, )
    f.close()

    logging.info('JSON file was created successfully - %s' % output_path)


def delete_previous_files():
    if not os.path.exists(os.path.join(downloads_folder, 'old')):
        os.mkdir(os.path.join(downloads_folder, 'old'))
        logging.info('Creating old folder in %s' % downloads_folder)

    for type in ('csv', 'xlsx'):
        for file in glob.glob(os.path.join(downloads_folder, '*.%s' % type)):
            # os.rename(file, os.path.join(downloads_folder, 'old', os.path.basename(file)))
            os.remove(file)
            logging.info('Move previous excel file to old folder - %s' % file)

if __name__ == '__main__':
    sys.exit(main())
