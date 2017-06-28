#!/usr/bin/env python

from argparse import ArgumentParser
import sys
import os
import re
import traceback
import time
import glob
import json
import yaml
import logging

script_path = os.path.abspath(__file__)
script_folder = os.path.dirname(script_path)
sys.path.append(os.path.join(script_folder, os.pardir, 'Packages'))  # Adding Packages folder to system path

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

#TODO
# Add refresh when stack
# spool results to file
# Add logging - debug/info + timestamp
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s %(levelname)-3s]: %(message)s',
                    datefmt='%d %b %Y %H:%M:%S')#,
                    #filename='c:/144.log',
                    #filemode='w')
logger = logging.getLogger(__name__)

path = os.path.join('C:/', 'Users', 'Admin', 'Downloads', 'chromedriver.exe')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-infobars")
driver = webdriver.Chrome(path, chrome_options=chrome_options)
driver.implicitly_wait(15)

# driver.get('https://he-il.facebook.com')
# driver.maximize_window()
# driver.get_screenshot_as_file('facebook_launch.png')
# driver.find_element_by_id('email').send_keys('eran.medina@gmail.com')
# driver.find_element_by_name('pass').send_keys('facebook1')
# driver.find_element_by_id('loginbutton').click()
# driver.get_screenshot_as_file('facebook_after_login.png')


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
        data = {}
        lst = []
        driver.get('https://www.b144.co.il')
        #driver.maximize_window()
        #driver.set_window_position(-2000, 0)
        driver.find_element_by_id('txtCategoryInput').send_keys('חשמלאים')
        driver.find_element_by_id('b_BusinessSearch').click()
        total_results_num = int(driver.find_elements_by_class_name('search-results-num')[0].text[:3])
        results_in_page = 15
        cur_page = 1
        start_page = 1
        end_page = int(total_results_num/results_in_page) + 1
        cur_res_num = 1

        if start_page > 1:
            driver.get('%s&_page_no=%s' % (driver.current_url, start_page))
            cur_res_num = results_in_page * (start_page - 1) + 1
            cur_page = start_page
            #for i in range(start_page):
            #    driver.find_element_by_css_selector('a.inner-nav-arrow.inner-nav-arrow--left.m-text-hide').click()  # move to next page
            #    cur_res_num += results_in_page

        while cur_res_num < total_results_num:
            #for item in driver.find_elements_by_class_name('card-number--blue'):  # for every result in page
            #for i in range(results_in_page):
            #for item in driver.find_elements_by_class_name('card-list-item'):
            #for item in driver.find_elements_by_class_name('card-hdr'):
            links = []
            for item in driver.find_elements_by_link_text('לפרטים נוספים'):
                links.append(item.get_property('href'))

            for link in links:
                #try:
                # element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, 'goToMember%s' % num)))  # wait for link to be clickable
                try:
                    #driver.find_element_by_id('goToMember%s' % cur_res_num).click()
                    #driver.find_element_by_id('MoreDetails%s' % cur_res_num).click()
                    #results_list[i].click()
                    driver.get(link)
                #except NoSuchElementException as e:
                except NoSuchElementException as e:
                    driver.refresh()
                    #driver.find_element_by_id('goToMember%s' % cur_res_num).click()
                except Exception as e:
                    pass
                    #logging.info('Refreshing 1...')
                    #driver.refresh()
                    #try:
                    #    element = driver.find_element_by_id('goToMember%s' % cur_res_num)
                    #except NoSuchElementException as e:
                    #    driver.back
                    #    #prev_btn = driver.find_element_by_css_selector('a.inner-nav-arrow.inner-nav-arrow--right.m-text-hide')
                    #    #prev_btn.click()
                    #    element = driver.find_element_by_id('goToMember%s' % cur_res_num)
                #try:

                #except Exception as e:
                #    logging.info("Error - Can't find item %d" % cur_res_num)
                #    if 'The requested URL was rejected' in driver.find_element_by_tag_name("body").text:
                #        logging.info('The requested URL was rejected, going back...')
                #        driver.back
                #    else:
                #        driver.refresh()
                #    driver.find_element_by_id('goToMember%s' % cur_res_num).click()
                try:
                    title = driver.find_element_by_css_selector('h1.business-card-hdl.section-hdl')
                except NoSuchElementException as e:
                    driver.refresh()
                    title = driver.find_element_by_css_selector('h1.business-card-hdl.section-hdl')
                except Exception as e:
                    pass
                #if title is None:
                #    driver.refresh()
                #    logging.info('Refreshing 2...')
                #    title = driver.find_element_by_css_selector('h1.business-card-hdl.section-hdl')
                if title:
                    title = title.text
                    try:
                        phone = driver.find_element_by_id('membersTelephone').text
                    except NoSuchElementException as e:
                        driver.find_element_by_id('showPhoneBtn').click()
                        phone = driver.find_element_by_id('showPhoneBtn').text
                        if phone == 'הצג מספר':
                            driver.find_element_by_id('showPhoneBtn').click()
                            phone = driver.find_element_by_id('showPhoneBtn').text
                    try:
                        mobile = driver.find_elements_by_class_name('bp-mobile-phone')[1].text
                        address = driver.find_element_by_class_name('bp-business-location').text
                        email = driver.find_element_by_class_name('bp-mail-link').get_attribute('href')[7:]
                    except NoSuchElementException as e:
                        raise

                    data['title'] = title
                    data['phone'] = phone
                    data['mobile'] = mobile
                    data['address'] = address
                    data['email'] = email

                    logging.info('Title: %s, Address: %s, Phone: %s, Mobile: %s, Email: %s (Result %03d, Page %d)'
                                 % (title, address, phone, mobile, email, cur_res_num, cur_page))
                    lst.append(dict(data))
                    logging.info('Go back to main window')
                    driver.back()
                #except Exception as err:
                #    print("Error: %s" % err)
                #    pass
                cur_res_num += 1
            logging.info('Move to next page')
            current_url = driver.current_url
            if cur_page == 1:
                driver.get('%s&_page_no=2' % current_url)
            elif cur_page < end_page:
                driver.get(current_url.replace('&_page_no=%s' % cur_page, '&_page_no=%s' % (cur_page + 1)))

            if '&_page_no=%s' % (cur_page + 1) in driver.current_url:
                cur_page += 1
                driver.refresh()
            else:
                logging.info("Error: failed in navigation to next page %s" % cur_page)

            # next_btn = driver.find_element_by_css_selector('a.inner-nav-arrow.inner-nav-arrow--left.m-text-hide')
            # if next_btn is None:
            #     logging.warning('Refreshing 3...')
            #     driver.refresh()
            #     next_btn = driver.find_element_by_css_selector('a.inner-nav-arrow.inner-nav-arrow--left.m-text-hide')
            # if next_btn:
            #     next_btn.click()
    except Exception as e:
        pass
pass


def is_product_ignored(file_path):
    ignore_list = []
    for item in ignore_list:
        if item in file_path:
            return True
    return False

if __name__ == '__main__':
    sys.exit(main())
