#!/usr/bin/env python
import os
import logging
import time
import glob
from .base_wps import BaseWps
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

script_path = os.path.abspath(__file__)
script_folder = os.path.dirname(script_path)
screenshots_folder = os.path.join(script_folder, 'Screesnshots')
downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')


class Ubank(BaseWps):
    def __init__(self, driver, opt_dict, bank_dict):
        super(Ubank, self).__init__(driver, opt_dict, bank_dict)
