#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created by Weiwei Jiang on 20180808
# Crawling Medicine Information
#

import os
import re
import pickle
from collections import OrderedDict
import getpass
import requests
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


class AMHCrawler:
    """Crawling medicine information from Australian Medicine Handbook."""

    def __init__(self):
        self.homeurl = "https://amhonline-amh-net-au.ezp.lib.unimelb.edu.au/"
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

    def _login(self, username, password):
        """Direct to the login page, and post login.

        Args:
            username (str): Unimelb user name, not email address.
            password (str): Password.
        """

        # First attempt to request homepage.
        self.browser.get(self.homeurl)

        # Get elements.
        e_username = self.browser.find_element_by_id("usernameInput")
        e_password = self.browser.find_element_by_id("passwordInput")
        e_submitbutton = self.browser.find_element_by_class_name("button")

        # Take login action.
        e_username.send_keys(username)
        e_password.send_keys(password)
        e_submitbutton.click()

    def run(self, username, password, druglist):
        """Run crawler.

        Args:
            username (str): Unimelb user name, not email address.
            password (str): Password.
        """
        self._login(username, password)

        # Fetching drug information.
        for drugname in druglist:
            # Navigate to the drug list page.
            e_drughome = self.browser.find_element_by_link_text("Drugs")
            e_drughome.click()
            # Navigate to the drug page.
            try:
                e_druglink = self.browser.find_element_by_partial_link_text(drugname)
                e_druglink.click()
            except NoSuchElementException as e:
                try:
                    # Search lower case.
                    e_druglink = self.browser.find_element_by_partial_link_text(drugname.lower())
                    e_druglink.click()
                except NoSuchElementException as e:
                    print(e)
                    continue
            # Getting structured data.
            e_html = self.browser.page_source
            # Dump page source.
            with open("../output/{}.html".format(drugname), "w", encoding="utf-8") as f:
                f.write(str(e_html).replace("\xa0", u" "))

        # Close browser can clean up.
        self._save_cookies()
        self.browser.close()

if __name__ == "__main__":
    amh = AMHCrawler()

    # Getting login info.
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    druglist = ["Doxorubicin",
                "Vincristine",
                "Cisplatin",
                "Paclitaxel",
                "Vancomycin",
                "Meropenem",
                "Gentamicin",
                "Micafungin",
                "Amphotericin",
                "Hydromorphone",
                "Morphine",
                "Dopamine",
                "Epinephrine",
                "Norepinephrine",
                "Dobutamine",
                "Thimerosal"]

    amh.run(username, password, druglist)

