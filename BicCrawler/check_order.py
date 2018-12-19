#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created by Weiwei Jiang on 20181219
# Crawling Bic
#

import os
import re
import time
import random
import pickle
from collections import OrderedDict
import getpass
import requests
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


class BICCrawler:
    """Crawling the information of bic query to guess the ID."""

    def __init__(self):
        self.homeurl = "https://www.biccamera.com/bc/member/CSfBcSpOrderForm.jsp"
        self.session = requests.Session()
        self.response = None
        self.headers = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache"
        }

        # Start web browser.
        self.options = Options()
        # self.options.add_argument("--headless")
        self.browser = webdriver.Chrome(chrome_options=self.options)
        # self._load_cookies()

    def _load_cookies(self):
        """Load cookies."""
        if os.path.exists("./cookies"):
            with open("./cookies", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.browser.add_cookie(cookie)

    def _save_cookies(self):
        """Save cookies."""
        cookies = self.browser.get_cookies()
        with open("./cookies", "wb") as f:
            pickle.dump(cookies, f)

    def run(self, slip_number):
        """Run crawler.

        Args:
            slip_number (str): Slip number.
        """
        
        # Generate IDs. 
        login_ids = ["{:03d}".format(item) for item in range(1000)]
        # login_ids = ["121", "221"]
        random.shuffle(login_ids)

        # Fetching drug information.
        for idx, lid in enumerate(login_ids):

            print("{:03d}/{:04d}: {:s}".format(idx, len(login_ids), lid))

            self.browser.get(self.homeurl)

            # Fill in query info.
            e_slip_number = self.browser.find_element_by_name("SLIP_NO")
            e_login_id = self.browser.find_element_by_name("REG_ID")
            e_slip_number.clear()
            e_login_id.clear()
            e_slip_number.send_keys(slip_number)
            e_login_id.send_keys(lid)

            # Send query.
            e_query_button = self.browser.find_elements_by_class_name("ordercheckBtn")[0].find_elements_by_tag_name("input")[0]
            e_query_button.submit()

            # Get results.
            try:
                e_error = self.browser.find_element_by_class_name("error")
            except NoSuchElementException as e:
                print(lid)
                break
            
            time.sleep(1)

        # Close browser can clean up.
        self._save_cookies()
        # self.browser.close()

if __name__ == "__main__":
    bc = BICCrawler()

    # Getting login info.
    slip_number = input("伝票番号: ")
    
    input()
    bc.run(slip_number)
    bc.browser.close()

