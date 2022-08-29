import json
import re
import requests
from bs4 import BeautifulSoup

ROOT_PATH = "https://www.whocc.no/atc_ddd_index{}"


def recursion_get_atc_ddd(target_code=None):
    atc_re = r"([\w\d]+)\s+\<b\>\<a\s?href\=\"\.(\/\?.+?)\">([\w\s\.\\\/\,]+)\<\/a\>"
    if target_code is None:
        dataset = {}
        runtime_url = ROOT_PATH.format("/")
        response = requests.request("GET", runtime_url)
        parsed = BeautifulSoup(response.text, "lxml")
        content = str(parsed.select_one("#content > div:nth-child(5) > div:nth-child(2) > p").encode_contents())
        _data = re.findall(atc_re, content)
        for code, href, name in _data:
            clean_href = href.replace("&amp;", "&")
            dataset[code] = {"ATC code": code, "href": runtime_url, "name": name,
                             "node": recursion_get_atc_ddd(target_code=[(code, clean_href, name,)])}

    else:
        dataset = []
        for _, href, _ in target_code:
            runtime_url = ROOT_PATH.format(href)
            print(runtime_url)
            response = requests.request("GET", runtime_url)
            parsed = BeautifulSoup(response.text, "html5lib")
            runtime_element = parsed.select_one("#last_updated").previousSibling
            if getattr(runtime_element, "name") == "p":
                content = str(runtime_element)
                _data = re.findall(atc_re, content)
                for _code, _href, _name in _data:
                    clean_href = _href.replace("&amp;", "&")
                    dataset.append(
                        {"ATC code": _code, "href": runtime_url, "name": _name,
                         "node": recursion_get_atc_ddd(target_code=[(_code, clean_href, _name,)])}
                    )
            else:
                dataset = []
                tr_list = parsed.select("#content > ul > table > * > tr")
                for tr in tr_list[1:]:
                    dataset.append(
                        {
                            column: td.get_text().strip()
                            for column, td in
                            zip(["ATC code", "Name", "DDD", "U", "Adm.R", "Note"], tr.findAll("td"))
                        }
                    )

    return dataset


if __name__ == '__main__':
    qaq = recursion_get_atc_ddd()
    with open("atc_ddd_index.json", "w") as f:
        json.dump(qaq, f, indent=2)
