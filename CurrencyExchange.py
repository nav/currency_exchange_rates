# -*- coding: utf-8 -*-
import re
import os
import urllib
import datetime
from HTMLParser import HTMLParser


class BOCCurrencyExchange(object):
    main_page_url = 'http://www.bankofcanada.ca/rates/exchange/daily-converter/#cfee'
    rates_page_url = 'http://www.bankofcanada.ca/stats/assets/js/daily_curr_data.js'

    def __init__(self):
        self.main_page_content = ''
        self.rates_page_content = ''
        self.fetch_data()

    def fetch_data(self):
        main_file = '{}_boc_main.dat'.format(datetime.datetime.now().today().date())
        rates_file = '{}_boc_rates.dat'.format(datetime.datetime.now().today().date())

        if os.path.isfile(main_file):
            with open(main_file, 'r') as fsock:
                self.main_page_content = fsock.read()
        else:
            main_page_content = urllib.urlopen(self.main_page_url).read()
            with open(main_file, 'w') as fsock:
                fsock.write(main_page_content)
            self.main_page_content = main_page_content
        
        if os.path.isfile(rates_file):
            with open(rates_file, 'r') as fsock:
                self.rates_page_content = fsock.read()
        else:
            rates_page_content = urllib.urlopen(self.rates_page_url).read()
            with open(rates_file, 'w') as fsock:
                fsock.write(rates_page_content)
            self.rates_page_content = rates_page_content

    def get_code_name_mapping(self):
        content = self.main_page_content

        class CodeParser(HTMLParser):
            mapping = dict()
            current_currency = None
            current_name = None    

            def handle_starttag(self, tag, attrs):
                if tag == "option":
                    for attr in attrs:
                        if attr[0] == "value" and attr[1].startswith('LOOKUPS'):
                            self.current_currency = attr[1]
                else:
                    self.current_currency = None

            def handle_data(self, data):
                if self.current_currency:
                    self.current_name = data.strip()

            def handle_endtag(self, tag):
                if self.current_currency and self.current_name:
                    self.mapping[self.current_currency] = self.current_name

            def get_mapping(self):
                self.feed(content)
                return self.mapping

        parser = CodeParser()
        code_name_mapping = parser.get_mapping()

        return code_name_mapping

    def get_code_rate_mapping(self):
        code_pattern = r'\["(.*)"\]'
        rate_pattern = r'rate:"(.*)",\sdate_en'
        code_rate_mapping = dict()
        currency_rate_mapping = dict()

        for line in self.rates_page_content.split('\n'):
            code = re.findall(code_pattern, line)
            rate = re.findall(rate_pattern, line)
            if code and rate:
                code_rate_mapping[code[0]] = float(rate[0])

        return code_rate_mapping

    def get_rates(self):
        rates = dict()
        code_name_mapping = self.get_code_name_mapping()
        for code, rate in self.get_code_rate_mapping().items():
            rates[code_name_mapping[code]] = rate

        return rates