import asyncio
import re
import time
from itertools import chain

import httpx2 as httpx
from bs4 import BeautifulSoup

from .symbol import ACT_DDD_ROOT_URL


class WHOCCAtcDddIndex:
    def __init__(self, loop=None):
        self.act_ddd_root = ACT_DDD_ROOT_URL
        self.atc_re = r"([\w\d]+)\s+\<b\>\<a\s?href\=\"\.(\/\?.+?)\">([\w\s\.\\\/\,\-\(\)]+)\<\/a\>"
        self.parse = BeautifulSoup
        self.client = httpx.AsyncClient(timeout=None, follow_redirects=True)
        self.l1 = []
        self.l2 = []
        self.l3 = []
        self.l4 = []
        self.l5 = []

    async def close(self):
        await self.client.aclose()

    async def get_l1(self, clean_cache=False):
        if not self.l1 or clean_cache:
            print("Running L1 ... ", end="")
            start_time = time.perf_counter()
            response = await self.client.get(self.act_ddd_root)
            parsed = self.parse(response.text, "lxml")
            content = str(parsed.select_one("#content > div:nth-child(5) > div:nth-child(2) > p"))
            atc_dataset = re.findall(self.atc_re, content)
            self.l1 = [(code, self.act_ddd_root + href.replace("&amp;", "&"), name) for code, href, name in atc_dataset]
            end_time = time.perf_counter()
            total_time = end_time - start_time
            print(f"Done ~ {total_time:.4f} seconds")
        return self.l1

    async def get_l2(self, clean_cache=False):
        if not self.l1 or clean_cache:
            await self.get_l1()
        print("Running L2 ... ", end="")
        start_time = time.perf_counter()

        _tasks = [self.async_response_parsed(href, check_p=True) for _, href, _ in self.l1]
        gather_data = await asyncio.gather(*_tasks)
        self.l2 = list(chain.from_iterable(gather_data))
        self.l2.sort(key=lambda d: d[0])

        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Done ~ {total_time:.4f} seconds")

    async def get_data(self, use, to_this, key):
        _tasks = [self.async_response_parsed(href, check_p=True) for _, href, _ in use]
        gather_data = await asyncio.gather(*_tasks)
        _to_this = to_this
        _to_this = list(chain.from_iterable(gather_data))
        _to_this.sort(key=key)

    async def get_l3(self, clean_cache=False):
        if not self.l2 or clean_cache:
            _ = await self.get_l2()
        print("Running L3 ... ", end="")
        start_time = time.perf_counter()

        _tasks = [self.async_response_parsed(href, check_p=True) for _, href, _ in self.l2]
        gather_data = await asyncio.gather(*_tasks)
        self.l3 = list(chain.from_iterable(gather_data))
        self.l3.sort(key=lambda d: d[0])

        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Done ~ {total_time:.4f} seconds")

    async def get_l4(self, clean_cache=False):
        if not self.l3 or clean_cache:
            _ = await self.get_l3()
        print("Running L4 ... ", end="")
        start_time = time.perf_counter()

        _tasks = [self.async_response_parsed(href, check_p=True) for _, href, _ in self.l3]
        gather_data = await asyncio.gather(*_tasks)
        self.l4 = list(chain.from_iterable(gather_data))
        self.l4.sort(key=lambda d: d[0])

        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Done ~ {total_time:.4f} seconds")

    async def get_l5(self, clean_cache=False):
        if not self.l4 or clean_cache:
            _ = await self.get_l4()
        print("Running L5 ... ", end="")
        start_time = time.perf_counter()

        _tasks = [self.async_response_parsed(href, check_table=True) for _, href, _ in self.l4]
        gather_data = await asyncio.gather(*_tasks)
        self.l5 = list(chain.from_iterable(gather_data))
        self.l5.sort(key=lambda d: d["ATC code"])

        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Done ~ {total_time:.4f} seconds")

    async def async_response_parsed(self, url, check_p=False, check_table=False):
        response = await self.client.request("GET", url, timeout=None)
        parsed = self.parse(response.text, "html5lib")
        if check_p:
            runtime_element = parsed.select_one("#last_updated").previousSibling
            if runtime_element.name == "p":
                content = str(runtime_element)
                atc_dataset = re.findall(self.atc_re, content)
                return [
                    (code, self.act_ddd_root + href.replace("&amp;", "&"), name) for code, href, name in atc_dataset
                ]
        if check_table:
            tr_list = parsed.select("#content > ul > table > * > tr")
            datalist = []
            for tr in tr_list[1:]:
                item = {}
                for column, td in zip(
                    ["ATC code", "Name", "DDD", "U", "Adm.R", "Note", "href"],
                    tr.findAll("td") + [url],
                    strict=False,
                ):
                    item[column] = td if isinstance(td, str) else td.get_text().strip()
                if not item.get("ATC code"):
                    item["ATC code"] = datalist[-1].get("ATC code")
                datalist.append(item)

            return datalist
        return parsed
