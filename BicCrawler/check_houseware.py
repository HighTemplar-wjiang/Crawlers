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
from selenium.webdriver.support.ui import Select


class BICCrawler:
    """Crawling the information of bic query to guess the ID."""

    def __init__(self):
        self.homeurl = "https://www.biccamera.com/bc/tenpo/CSfBcToriokiList.jsp?GOODS_NO={:s}"
        self.searchurl = r"https://www.biccamera.com/bc/category/?q=macbook%2Bpro%2B2018&entr_nm=%83%41%83%62%83%76%83%8B%81%40Apple"
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

        # Goods to search.
        self.goods_dict = OrderedDict({})

        # Start web browser.
        self.options = Options()
        self.options.add_argument("--headless")
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

    def get_goods_numbers(self):
        self.browser.get(self.searchurl)
        all_items = self.browser.find_elements_by_class_name("bcs_title")
        for item in all_items:
            link = item.find_elements_by_tag_name("a")[0].get_attribute("href")
            re_result = re.match(".*?/item/(\d+)/", link)
            if re_result:
                goods_name = item.find_elements_by_tag_name("a")[0].get_attribute("innerHTML")
                goods_number = re_result.group(1)
                self.goods_dict[goods_number] = goods_name

        # Show results.
        print("{} goods retrieved.".format(len(self.goods_dict)))
        for key, value in self.goods_dict.items():
            print("{}: {}".format(key, value))
        print()

    def status_dict_to_str(self, all_status_dict):
        """Convert status dict to string.
        """
        status_str = ""

        # Update time.
        status_str = status_str + "Last updated: " + time.strftime("%Y%m%d-%H%M", time.localtime()) + "\n"
        for key, value in self.goods_dict.items():
            status_str = status_str + "{}: {}\n{}\n".format(key, value, all_status_dict[key])

        return status_str

    def run_once(self):
        """Run once of the crawler.
        """

        all_status_dict = {}

        # Fetching houseware information.
        for key, value in self.goods_dict.items():

            url = self.homeurl.format(key)
            print("{}: {}\n{}".format(key, value, url))

            # Start a query.
            self.browser.get(url)

            # Select area
            select = Select(self.browser.find_element_by_id("toriki_shop_area"))
            select.select_by_visible_text("東京都")

            # Get results.
            try:
                stock_info_root = self.browser.find_element_by_id("jpShopList")
                stock_list = stock_info_root.find_elements_by_tag_name("li")
                status_dict = OrderedDict({
                    "△": 0,  # お取り寄せ
                    "○": 0,  # 在庫残少
                    "◎": 0   # 在庫あり
                })
                for stock in stock_list:
                    area_name = stock.find_element_by_class_name("bcs_KST_Area").get_attribute("innerHTML")
                    if area_name != "東京都":
                        continue
                
                    store_name = stock.find_elements_by_class_name("bcs_KST_Store")[0].find_elements_by_tag_name("a")[0].get_attribute("innerHTML")
                    stock_status = stock.find_elements_by_class_name("bcs_KST_Stock")[0].get_attribute("innerHTML")[0]
                    # print("{}: {}".format(store_name, stock_status))
                    if stock_status in status_dict:
                        status_dict[stock_status] += 1
                    else:
                        pass
                
                # Aggregating.
                all_status_dict[key] = " ".join(["{:s}{:2d}".format(s, n) for s, n in status_dict.items()])
                print(all_status_dict[key])

            except NoSuchElementException as e:
                break
            
            time.sleep(1)
        
        # Print results.
        print(self.status_dict_to_str(all_status_dict))

        return all_status_dict

    def run_repeat(self, dump_path=None):
        """Repeatly run crawler.

        Args:
            dump_path(str, optional): File path to dump results.
        """

        while(True):
            all_status_dict = self.run_once()
            if dump_path:
                with open(dump_path, "w") as f:
                    f.write(self.status_dict_to_str(all_status_dict).replace("\n", "<br>"))

            sleep_sec = random.randint(600, 1200)
            time.sleep(sleep_sec)

        # Close browser can clean up.
        self._save_cookies()
        # self.browser.close()

if __name__ == "__main__":
    bc = BICCrawler()

    bc.get_goods_numbers()
    bc.run_repeat("./bicmac.html")
    bc.browser.close()

