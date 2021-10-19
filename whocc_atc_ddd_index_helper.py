from lxml import etree
import requests
from bs4 import BeautifulSoup
import asyncio

VALUE_ERROR_INFO = "Your code_list is None or empty."


class AtcDddIndex:
    def __init__(self):
        self.atc_ddd_root = "https://www.whocc.no/atc_ddd_index"
        self.atc_ddd_url = self.atc_ddd_root + "/?code="
        self.requests = requests.session()
        self.level_index = [[] for _ in range(5)]
        self.level_1_data = None
        self.level_2_data = None
        self.level_3_data = None
        self.level_4_data = None
        self.level_5_data = None
        self.loop = asyncio.get_event_loop()

    def _requests_to_soup(self, code):
        response = self.requests.get(self.atc_ddd_url + code)
        return BeautifulSoup(response.text, 'lxml')

    async def async_requests_to_soup(self, code):
        response = self.requests.get(self.atc_ddd_url + code)
        return BeautifulSoup(response.text, 'lxml')

    def _wash_a_element(self, a_element):
        text = a_element.text
        href = self.atc_ddd_root + a_element.get("href")[1:]
        code_name = a_element.get("href").split("&")[0].split("=")[-1]
        return {"code_name": code_name, "href": href, "text": text, "edges": {}}

    async def job(self, code, level):
        parsing = await self.async_requests_to_soup(code)
        data_list = [self._wash_a_element(i) for i in parsing.select('b a')]
        data_list = data_list[:level] if level == 1 else data_list[level - 1:]
        return data_list

    def _jobs(self, code_list, level, async_=False):
        temp = []
        if async_:

            tasks = [
                asyncio.ensure_future(self.job(code, level))
                for code in code_list
            ]
            self.loop.run_until_complete(asyncio.wait(tasks))
        else:
            for code in code_list:
                print(f"Runung {code} Code...")
                parsing = self._requests_to_soup(code)
                data_list = [self._wash_a_element(i) for i in parsing.select('b a')]
                data_list = data_list[:level] if level == 1 else data_list[level - 1:]
                temp.extend(data_list)
        return temp

    def get_table_to_dict(self, parsing):
        ul_table = parsing.select_one('ul table')
        parsed_html = etree.HTML(str(ul_table).replace("\xa0", ""))
        html_table = parsed_html.find("body/table")
        table_as_list = list(html_table)
        table_headers = [col.text for col in table_as_list[0]]
        table_list_dict = [dict(zip(table_headers, [col.text for col in row])) for row in table_as_list[1:]]
        return [dictionary for dictionary in table_list_dict]

    def _detail(self, code_list):
        temp = []
        for code in code_list:
            print(f"Runung {code} Code...")
            parsing = self._requests_to_soup(code)
            temp.extend(self.get_table_to_dict(parsing))
        return temp

    def level_1(self, code_list=None):
        level = 1
        if not code_list or code_list is None:
            raise ValueError(VALUE_ERROR_INFO)
        self.level_1_data = self._jobs(code_list, level)
        self.level_index[level] = [i["code_name"] for i in self.level_1_data]
        return self.level_1_data

    def level_2(self, code_list=None):
        level = 2
        if not code_list or code_list is None:
            raise ValueError(VALUE_ERROR_INFO)
        self.level_2_data = self._jobs(code_list, level)
        self.level_index[level] = [i["code_name"] for i in self.level_2_data]
        return self.level_2_data

    def level_3(self, code_list=None):
        level = 3
        if not code_list or code_list is None:
            raise ValueError(VALUE_ERROR_INFO)
        self.level_3_data = self._jobs(code_list, level)
        self.level_index[level] = [i["code_name"] for i in self.level_3_data]
        return self.level_3_data

    def level_4(self, code_list=None):
        level = 4
        if not code_list or code_list is None:
            raise ValueError(VALUE_ERROR_INFO)
        self.level_4_data = self._jobs(code_list, level)
        self.level_index[level] = [i["code_name"] for i in self.level_4_data]
        return self.level_4_data

    def level_5(self, code_list=None):
        if not code_list or code_list is None:
            raise ValueError(VALUE_ERROR_INFO)
        self.level_5_data = self._detail(code_list)
        return self.level_5_data
