import os
import logging, sys
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

#TODO
# Add refresh when stack
# spool results to file

#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
path = os.path.join('C:/', 'Users', 'Admin', 'Downloads', 'chromedriver.exe')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-infobars")
driver = webdriver.Chrome(path, chrome_options=chrome_options)
driver.implicitly_wait(180)
# driver.get('https://he-il.facebook.com')
# driver.maximize_window()
# driver.get_screenshot_as_file('facebook_launch.png')
# driver.find_element_by_id('email').send_keys('eran.medina@gmail.com')
# driver.find_element_by_name('pass').send_keys('facebook1')
# driver.find_element_by_id('loginbutton').click()
# driver.get_screenshot_as_file('facebook_after_login.png')
data = {}
lst = []
driver.get('https://www.b144.co.il')
driver.maximize_window()
driver.set_window_position(-2000, 0)
driver.find_element_by_id('txtCategoryInput').send_keys('גינון')
driver.find_element_by_id('b_BusinessSearch').click()
results_num = int(driver.find_elements_by_class_name('search-results-num')[0].text[:3])
start_page = 1
num = 1

if start_page > 1:
    for i in range(start_page - 1):
        driver.find_elements_by_class_name('inner-nav-arrow')[1].click()  # move to next page
        num += 15

while num < results_num:
    for item in driver.find_elements_by_class_name('card-number--blue'):  # for every result in page
        #try:
        #driver.find_element_by_id('goToMember%s' % num).click()  # get into details page
        element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, 'goToMember%s' % num)))  # wait for link to be clickable
        try:
            element.click()
        except Exception as e:
            logging.error("Can't find item %d" % num)
            driver.refresh()
            driver.find_element_by_id('goToMember%s' % num).click()
        #title = driver.find_elements_by_class_name('business-card-hdl')
        title = driver.find_elements_by_css_selector('h1.business-card-hdl.section-hdl')
        if len(title) > 0:
            data['title'] = title[0].text
            data['phone'] = driver.find_element_by_id('membersTelephone').text
            data['mobile'] = driver.find_elements_by_class_name('bp-mobile-phone')[1].text
            data['address'] = driver.find_elements_by_class_name('bp-business-location')[0].text
            data['email'] = driver.find_elements_by_class_name('bp-mail-link')[0].get_attribute('href')[7:]

            lst.append(dict(data))
            logging.debug('Go back to main window')
            driver.back()
            print('%03d) Title: %s, Address: %s, Phone: %s, Mobile: %s, Email: %s, (Page %d)'
                  % (num, data['title'], data['address'], data['phone'], data['mobile'], data['email'], start_page))
        #except Exception as err:
        #    print("Error: %s" % err)
        #    pass
        num += 1
    #driver.find_elements_by_class_name('inner-nav-arrow inner-nav-arrow--left m-text-hide')
    logging.debug('Move to next page')
    driver.find_elements_by_class_name('inner-nav-arrow')[1].click()  # move to next page
    start_page += 1
    current_url = driver.current_url()
    driver.close()
    driver.get(current_url)
    driver.maximize_window()
pass
