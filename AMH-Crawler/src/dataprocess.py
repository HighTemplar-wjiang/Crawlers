#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Created by Weiwei Jiang on 20180808
# Processed crawled data.
#


import os
import re
from collections import OrderedDict
import pandas as pd
from lxml import html


class MedicineExtractor:

    def __init__(self):
        # Structured data.
        self.itemdict = OrderedDict([
            ("Alias", "also-known"),
            ("Mode of action", "mode-action"),
            ("Indication", "indication"),
            ("Precautions", "precautions"),
            ("Adverse effects", "adv-eff"),
            ("Dosage", "dosage"),
            ("Administration advice", "administration-advice"),
            ("Counselling", "counsel"),
            ("Practice points", "prac-pts"),
            ("Products", "products")
        ])

        self.structreddata = pd.DataFrame(columns=["Name"] + list(self.itemdict.keys()))

    def _structurize_html(self, innerHTML):
        """Processing HTML file to structured data.

        Args:
            innerHTML (str): String of inner HTML.
        """

        # Converting data.
        page = html.document_fromstring(innerHTML)
        content = page.get_element_by_id("content")
        datadict = {"Name": content.find("article/header/h1").text_content()}
        drugid = page.get_element_by_id("content").find("article/header").attrib["id"]

        for key in self.itemdict.keys():
            classname = self.itemdict[key]
            e_section = content.find_class(classname)
            if len(e_section) > 0:
                textcontent = e_section[0].text_content()
                textcontent = textcontent.replace("\xa0", u" ")
                textcontent = re.sub(" +", " ", textcontent)
                textcontent = re.sub("[\n][ +]", "\n", textcontent)
                textcontent = re.sub("\n+", "\n", textcontent)
                textcontent = re.sub("^\n", "", textcontent)
                textcontent = re.sub("\n", "\\n", textcontent)
                datadict[key] = textcontent

        self.structreddata = self.structreddata.append(datadict, ignore_index=True)

    def run(self, path="../output/"):
        """Process fetched html data into structured data.

        Args:
             path (str, optional): Directory path to html files.
        """
        filelist = os.listdir(path)
        reexp = "(.*).html"
        refilter = re.compile(reexp)

        for filename in filelist:
            re_result = refilter.match(filename)
            if re_result:
                drugname = re_result[1]
                with open(os.path.join(path, filename), "r", encoding="utf-8") as f:
                    pagesource = f.read()
                    self._structurize_html(pagesource)

        with open(os.path.join(path, "output.csv"), "w", encoding="utf-8") as f:
            self.structreddata.to_csv(f)


if __name__ == "__main__":
    me = MedicineExtractor()
    me.run()
