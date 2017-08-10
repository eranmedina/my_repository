#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import sys
import os
import logging
import traceback

script_path = os.path.abspath(__file__)
script_folder = os.path.dirname(script_path)
sys.path.append(os.path.join(script_folder, 'Packages'))  # Adding Packages folder to system path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#TODO
# Add logging - debug/info + timestamp
# classes - 144 / yellow pages
# packages
# report

logging.basicConfig(level=logging.INFO,
                    #format='[%(asctime)s %(levelname)-3s]: %(message)s',
                    #datefmt='%d %b %Y %H:%M:%S')#,
                    format='[%(asctime)s]| %(levelname)-7s| %(message)-150s| {%(name)s|%(funcName)s|%(lineno)-3s}',
                    datefmt='%d-%m-%y %H:%M:%S')
                    #filename=('144.log'),
                    #filemode='w')

logger = logging.getLogger(__name__)
path = os.path.join('C:/', 'Users', 'Admin', 'Downloads', 'chromedriver.exe')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-infobars")
driver = webdriver.Chrome(path, chrome_options=chrome_options)
driver.implicitly_wait(30)


def main():
    '''A module that deals with plugin XML
    Written by eranm@waves.com'''

    parser = ArgumentParser()
    parser.add_argument('--branch', dest='branch', default=None, help='branch name', metavar='(string)')

    #opt_dict = vars(parser.parse_args())
    #none_set = {key for key in opt_dict if opt_dict[key] is None and key not in ('mode', 'exp_files_list')}
    #if none_set:
    #    parser.print_help()
    #    raise ValueError('Missing arguments: %s' % list(none_set))

    try:
        lst = []
        output_path = '144_output.txt'
        driver.get('https://www.b144.co.il')
        #driver.maximize_window()
        #driver.set_window_position(-2000, 0)
        #driver.find_element_by_id('txtCategoryInput').send_keys('גינון')
        driver.find_element_by_id('txtCategoryInput').send_keys('חשמלאים')
        driver.find_element_by_id('b_BusinessSearch').click()
        main_page = driver.current_url
        results_in_page = 15
        total_results_num = int(driver.find_elements_by_class_name('search-results-num')[0].text[:-7])
        start_page = 1
        end_page = int(total_results_num / results_in_page) + 1
        logging.info('Total results found: %d in %d pages' % (total_results_num, end_page))

        # pages loop
        for cur_page in range(end_page):
            cur_page += start_page
            if cur_page > 1:
                logging.info('Navigate to page number %s' % cur_page)
                driver.get('%s&_page_no=%s' % (main_page, cur_page))
            if cur_page % 10 == 0:  # refresh browser every 10 pages
                logging.info('Refreshing browser every 10 pages...')
                driver.refresh()
            links = []
            for item in driver.find_elements_by_link_text('לפרטים נוספים'):  # get all links in page
                links.append(item.get_property('href'))
            try:
                # links loop
                for link_num, link in enumerate(links):
                    if link_num == results_in_page:
                        break  # stop in case of partial parsing was request
                    try:
                        data = {}
                        data['id'] = results_in_page * (cur_page - 1) + link_num + 1
                        get_business_card_page_and_sync(link)

                        data['title'] = driver.find_element_by_css_selector('h1.business-card-hdl.section-hdl').text
                        try:
                            data['phone'] = driver.find_element_by_id('membersTelephone').text
                            if data['phone'] == 'הצג מספר':
                                logging.info('Clicking on show phone button')
                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'showPhoneBtn'))).click()
                                driver.find_element_by_id('showPhoneBtn').click()
                                data['phone'] = driver.find_element_by_id('showPhoneBtn').text
                            data['mobile'] = driver.find_elements_by_class_name('bp-mobile-phone')[1].text
                            data['address'] = driver.find_element_by_class_name('bp-business-location').text
                            data['email'] = driver.find_element_by_class_name('bp-mail-link').get_attribute('href')[7:]
                            res_str = 'Title: %s, Address: %s, Phone: %s, Mobile: %s, Email: %s (Result %d, Page %d)' \
                                      % (data['title'], data['address'], data['phone'], data['mobile'], data['email'],
                                         data['id'], cur_page)
                            logging.info(res_str)
                        except Exception as e:
                            logging.info('%s: %s\n%s' % (e.__class__.__name__, e, traceback.format_exc()))
                            logging.info('Failed to read data - %s' % data)

                        lst.append(dict(data))
                        if data['id'] % results_in_page > 0:
                            logging.info('Go back to main window')
                            driver.back()

                    except Exception as e:  # go to next link
                        logging.info('%s: %s\n%s' % (e.__class__.__name__, e, traceback.format_exc()))
                        logging.info('Continue to the next link - %s' % (data['id'] + 1))
                        continue
            except Exception as e:
                logging.info('%s: %s\n%s' % (e.__class__.__name__, e, traceback.format_exc()))
                logging.info('Continue to the next page - %s' % (cur_page + 1))
                continue  # go to next page
    except Exception as e:
        logging.info('%s: %s\n%s' % (e.__class__.__name__, e, traceback.format_exc()))
    finally:
        #with open(output_path, "w", encoding="utf-8") as f:
            # json.dump(lst, f)
        f = open(output_path, "w", encoding="utf-8")
        for row_num, row in enumerate(lst):
            if row['id'] == row_num + 1:
                f.write('%s\n' % row)
            else:
                f.write('FAILURE\n')
        f.close()


def get_business_card_page_and_sync(link):
    while True:
        try:
            driver.get(link)
            WebDriverWait(driver, 2).until(lambda s: len(s.find_elements(By.CSS_SELECTOR, 'h1.business-card-hdl.section-hdl')) == 1)
            break  # it will break from the loop once the specific element will be present.
        except TimeoutException:
            logging.info('Loading took too much time!-Try again')
            driver.refresh()


def restart_browser():
    driver.delete_all_cookies()
    driver.close()
    driver = webdriver.Chrome(path, chrome_options=chrome_options)
    driver.implicitly_wait(30)


def move_to_next_page(cur_page, end_page):
    if cur_page < end_page:
        logging.info('Move to next page (%s)' % (cur_page + 1))
        current_url = driver.current_url
        if cur_page == 1:
            driver.get('%s&_page_no=2' % current_url)
        else:
            driver.get(current_url.replace('&_page_no=%s' % cur_page, '&_page_no=%s' % (cur_page + 1)))

        if '&_page_no=%s' % (cur_page + 1) in driver.current_url:
            cur_page += 1
            driver.refresh()
            return True
        logging.info("Error: failed in navigation to next page %s" % cur_page)
        return False

        # next_btn = driver.find_element_by_css_selector('a.inner-nav-arrow.inner-nav-arrow--left.m-text-hide')
        # if next_btn is None:
        #     logging.warning('Refreshing 3...')
        #     driver.refresh()
        #     next_btn = driver.find_element_by_css_selector('a.inner-nav-arrow.inner-nav-arrow--left.m-text-hide')
        # if next_btn:
        #     next_btn.click()

if __name__ == '__main__':
    sys.exit(main())
