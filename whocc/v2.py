import asyncio
import csv
import re
from itertools import chain

import httpx
from bs4 import BeautifulSoup

from whocc import AtcL1234Format, AtcL5Format


class WHOCCAtcDddIndexV2:
    def __init__(self):
        self.act_ddd_root = "https://atcddd.fhi.no/atc_ddd_index/"
        self.atc_re = r"([\w\d]+)\s+\<b\>\<a\s?href\=\"\.(\/\?.+?)\">([\w\s\.\\\/\,\-\(\)]+)\<\/a\>"
        self.client = httpx.AsyncClient(timeout=None)
        self.l1: list[AtcL1234Format] | None = None
        self.l2: list[AtcL1234Format] | None = None
        self.l3 = None
        self.l4 = None
        self.l5 = None

    async def close(self):
        await self.client.aclose()

    async def _get_to_check_raise_for_status(self, url: str):
        response = await self.client.get(url)
        response.raise_for_status()
        return response

    def _parsed_to_soup(self, context: str) -> BeautifulSoup:
        return BeautifulSoup(context, 'lxml')

    async def format_l5(
            self,
            url: str,
    ) -> list[AtcL5Format]:
        response = await self._get_to_check_raise_for_status(url)
        parsed = self._parsed_to_soup(response.text)
        datalist = []
        try:
            div = parsed.find("div", {"id": "content"})
            ul = div.find("ul")
            tr_list = ul.select("table > tr")
            if not tr_list:
                return datalist

            for tr in tr_list[1:]:
                item = {}
                for column, td in zip(["ATC code", "Name", "DDD", "U", "Adm.R", "Note"], tr.findAll("td")):
                    if column == "Name":
                        item["url"] = self.act_ddd_root + td.find("a").get("href")[2:]
                    item[column] = td.get_text().strip()
                if item.get("ATC code", None) is None:
                    item["ATC code"] = datalist[-1].get("ATC code")
                datalist.append(AtcL5Format.model_validate(item))
        except AttributeError:
            pass
        return datalist

    async def format_l234(self, url: str, ) -> list[AtcL1234Format]:
        response = await self._get_to_check_raise_for_status(url)
        parsed = self._parsed_to_soup(response.text)
        runtime_element = parsed.select_one("#last_updated").previousSibling
        if getattr(runtime_element, "name") == "p":
            content = str(runtime_element)
            atc_dataset = re.findall(self.atc_re, content)
            return [
                AtcL1234Format(
                    code=code,
                    name=name,
                    url=self.act_ddd_root + href[1:].replace("&amp;", "&")
                )
                for code, href, name in
                atc_dataset
            ]

    async def get_l1(self, clean_cache: bool = False) -> list[AtcL1234Format]:
        if (self.l1 is None) or clean_cache:
            response = await self._get_to_check_raise_for_status(self.act_ddd_root)
            parsed = self._parsed_to_soup(response.text)
            content = str(parsed.select_one("#content > div:nth-child(5) > div:nth-child(2) > p"))
            atc_dataset = re.findall(self.atc_re, content)
            self.l1 = [
                AtcL1234Format(
                    code=code,
                    name=name,
                    url=self.act_ddd_root + href[1:].replace("&amp;", "&")
                )
                for code, href, name in atc_dataset
            ]
        return self.l1

    async def get_l2(self, clean_cache: bool = False) -> list[AtcL1234Format]:
        if (self.l2 is None) or clean_cache:
            l1 = await self.get_l1(clean_cache)
        else:
            l1 = self.l1
        task_results = await asyncio.gather(*[
            self.format_l234(item.url)
            for item in l1
        ])
        self.l2 = list(chain.from_iterable(task_results))
        self.l2.sort(key=lambda d: d.code)
        return self.l2

    async def get_l3(self, clean_cache: bool = False) -> list[AtcL1234Format]:
        if (self.l3 is None) or clean_cache:
            l2 = await self.get_l2(clean_cache)
        else:
            l2 = self.l2
        task_results = await asyncio.gather(*[
            self.format_l234(item.url)
            for item in l2
        ])
        self.l3 = list(chain.from_iterable(task_results))
        self.l3.sort(key=lambda d: d.code)
        return self.l3

    async def get_l4(self, clean_cache: bool = False) -> list[AtcL1234Format]:
        if (self.l4 is None) or clean_cache:
            l3 = await self.get_l3(clean_cache)
        else:
            l3 = self.l3
        task_results = await asyncio.gather(*[
            self.format_l234(item.url)
            for item in l3
        ])
        self.l4 = list(chain.from_iterable(task_results))
        self.l4.sort(key=lambda d: d.code)
        return self.l4

    async def get_l5(self, clean_cache: bool = False) -> list[AtcL5Format]:
        if (self.l5 is None) or clean_cache:
            l4 = await self.get_l4(clean_cache)
        else:
            l4 = self.l4
        task_results = await asyncio.gather(*[
            self.format_l5(item.url)
            for item in l4
        ])
        self.l5 = list(chain.from_iterable(task_results))
        self.l5.sort(key=lambda d: d.code)
        return self.l5

    def export_csv(self):
        from whocc.export import csv_store
        l1234_fieldnames = list(AtcL1234Format.model_json_schema()["properties"].keys())
        l5_fieldnames = list(AtcL5Format.model_json_schema()["properties"].keys())
        csv_store("l1", l1234_fieldnames, self.l1)
        csv_store("l2", l1234_fieldnames, self.l2)
        csv_store("l3", l1234_fieldnames, self.l3)
        csv_store("l4", l1234_fieldnames, self.l4)
        csv_store("l5", l5_fieldnames, self.l5)
