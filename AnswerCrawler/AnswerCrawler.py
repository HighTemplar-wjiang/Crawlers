#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created by Weiwei Jiang on 20170901
#
# Crawling

import re
from time import sleep
import random
import requests


class AnswerCrawler:

    libStrSlicing = 10

    def __init__(self):

        self.session = requests.Session()
        self.response = None
        self.curPath = ''
        self.questionLib = {}

        self.headers = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
            "Referer": "https://edu.citiprogram.jp/defaultjapan.asp?language=japanese",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4"
        }

    def _update_cur_url(self):
        # Note: regular expression uses longest matching
        self.curPath = re.compile('(.*)/.*').findall(self.response.url)[0]

    def _get_url(self, relativeUrl):

        absoluteUrl = self.curPath + '/' + relativeUrl
        self.headers["Referer"] = absoluteUrl
        self.response = self.session.get(absoluteUrl)
        self._update_cur_url()

    def _set_answer(self):

        answerForm = {
            'submit': 'submit',
            'btnSubmit': '送信(Submit)'
        }

        try:
            questionRecords = list(self.questionLib.keys())
            questionContents = re.compile(
                'Question&nbsp;(?:[0-9])(?:.*\s)+?.*? >(.*)\s<.*?green;').findall(self.response.content.decode())

            for idxQuestion, questionContent in enumerate(questionContents):

                # find question ID
                questionID, answerValue = re.compile(
                    '{}(?:.*\s)+?.*label.*answer([0-9]+)_([0-9])'.format(questionContent[:self.libStrSlicing])).findall(
                        self.response.content.decode())[0]

                # if not in the lib
                if questionContent[:self.libStrSlicing] not in questionRecords:
                    answerForm.update({'intChosenAnswer' + questionID: str(round(random.uniform(1.0, 2.9)))})
                    continue

                # get all answers
                answerContentsValues = re.compile(
                    'label.*answer{}_([0-9]).*\"> ?(.*)\s'.format(questionID)).findall(self.response.content.decode())
                for answerValue, answerContent in answerContentsValues:
                    if answerContent[:self.libStrSlicing] == self.questionLib[questionContent[:self.libStrSlicing]]:
                        answerForm.update({'intChosenAnswer' + questionID: str(answerValue)})

            print(answerForm)

            return answerForm
        except Exception as e:
            pass  # debug

    def login(self, urlLogin, user, password):

        # set post data
        postData = {
            "action": "login",
            "strUsername": user,
            "strPassword": password,
            "submit": "ログイン(Log In)"
        }

        # post and get cookie
        self.response = self.session.post(urlLogin, data=postData, headers=self.headers)
        self._update_cur_url()

        return dict(self.response.cookies) if not isinstance(self.response.cookies, dict) else self.response.cookies

    def get_gradebook_page(self):

        nextUrl = re.compile('Required.*href=\"(.+?)\".*Start').findall(self.response.content.decode())[0]
        self._get_url(nextUrl)

    def get_article_page(self, articleName):

        nextUrl = re.compile('href=\"(.+?)\".*' + articleName).findall(ac.response.content.decode())[0]
        self._get_url(nextUrl)

    def get_quiz_page(self):

        nextUrl = re.compile('href=\"(.+?)\".*Take the quiz').findall(ac.response.content.decode())[0]
        self._get_url(nextUrl)

    def post_quiz_answer(self):

        postUrl = self.curPath + '/' + re.compile('post.*action=\"(.+?)\"').findall(self.response.content.decode())[0]
        postData = self._set_answer()
        self.response = self.session.post(postUrl, data=postData, headers=self.headers)
        self._update_cur_url()

        return self.parse_quiz_answer()

    def parse_quiz_answer(self):

        try:
            full, have = re.compile('取得可能なポイント([0-9])中([0-9])ポイントを取得しました').findall(self.response.content.decode())[0]
            print("\tGrade: {}/{}".format(have, full))

            questions = re.compile('Question&nbsp;([0-9]).*? (.*)').findall(self.response.content.decode())
            # correctAnswers = re.compile('Correct Answer.*\s.*\s.*\s.*green;\">(.*).').findall(self.response.content.decode())
            correctAnswers = re.compile('Correct Answer(?:.*\s){2}\s*(.*)\r').findall(self.response.content.decode())

            for question, answer in zip(questions, correctAnswers):
                print('Question {}: {}\nCorrect Answer: {}'.format(str(question[0]), str(question[1]), answer))
                if question[1] not in self.questionLib:
                    self.questionLib.update({question[1][:self.libStrSlicing]: answer[:self.libStrSlicing]})

            return int(have)
        except Exception as e:
            pass  # debug

    def run(self, urlLogin, user, password, articleName):

        # proceed to the exam page
        self.login(urlLogin, user, password)
        self.get_gradebook_page()
        self.get_article_page(articleName)

        # trying
        for idxTry in range(0, 5):
            print('\n\nTrying round ({}/{})'.format(idxTry, 5))
            self.get_quiz_page()
            print(self.response.url)
            sleep(round(random.uniform(1, 10)))
            score = self.post_quiz_answer()
            print(self.response.url)
            if score == 5:
                print("Winner winner, chicken dinner!")
                break
            else:  # return to the article page
                self._get_url(re.compile('href=\"(.+?)\".*View this module again').findall(self.response.content.decode())[0])


if __name__ == "__main__":

    user = 'xxx'
    password = 'xxx'
    urlLogin = 'https://edu.citiprogram.jp/loginjapan.asp?action=login&language=japanese'

    ac = AnswerCrawler()
    ac.run(urlLogin, user, password, 'Whistleblowing and the Obligation to Protect the Public')

    print(ac.response.url)

