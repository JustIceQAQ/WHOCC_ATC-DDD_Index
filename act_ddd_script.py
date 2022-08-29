import asyncio

from whocc import WHOCCAtcDddIndex
import pandas as pd


async def main(loop):
    atc_ddd = WHOCCAtcDddIndex(loop=loop)
    _ = await atc_ddd.get_l5()
    pd.DataFrame(atc_ddd.l1, columns=["ATC code", "href", "name"]).to_excel('demo_atc_l1.xlsx', index=False)
    pd.DataFrame(atc_ddd.l2, columns=["ATC code", "href", "name"]).to_excel('demo_atc_l2.xlsx', index=False)
    pd.DataFrame(atc_ddd.l3, columns=["ATC code", "href", "name"]).to_excel('demo_atc_l3.xlsx', index=False)
    pd.DataFrame(atc_ddd.l4, columns=["ATC code", "href", "name"]).to_excel('demo_atc_l4.xlsx', index=False)
    pd.DataFrame(atc_ddd.l5).to_excel('demo_atc_l5.xlsx', index=False)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
