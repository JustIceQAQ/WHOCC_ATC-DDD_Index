import pytest
from whocc.schemas import AtcL1234Format, AtcL5Format
from whocc.v2 import WHOCCAtcDddIndexV2


@pytest.mark.asyncio
async def test_get_l1():
    v2 = WHOCCAtcDddIndexV2()
    l1_result = await v2.get_l1()
    assert isinstance(l1_result, list)
    for item in l1_result:
        assert isinstance(item, AtcL1234Format)


@pytest.mark.asyncio
async def test_format_l234():
    url = "https://atcddd.fhi.no/atc_ddd_index/?code=A&showdescription=no"
    v2 = WHOCCAtcDddIndexV2()
    response = await v2.format_l234(url)
    assert isinstance(response, list)
    for item in response:
        assert isinstance(item, AtcL1234Format)


@pytest.mark.asyncio
async def test_format_l5():
    url = "https://atcddd.fhi.no/atc_ddd_index/?code=A01AA01&showdescription=yes"
    v2 = WHOCCAtcDddIndexV2()
    response = await v2.format_l5(url)
    assert isinstance(response, list)
    for item in response:
        assert isinstance(item, AtcL5Format)


@pytest.mark.asyncio
async def test_get_l2():
    v2 = WHOCCAtcDddIndexV2()
    l2_result = await v2.get_l2()
    assert isinstance(l2_result, list)
    for item in l2_result:
        assert isinstance(item, AtcL1234Format)


@pytest.mark.asyncio
async def test_get_l3():
    v2 = WHOCCAtcDddIndexV2()
    l3_result = await v2.get_l3()
    assert isinstance(l3_result, list)
    for item in l3_result:
        assert isinstance(item, AtcL1234Format)


@pytest.mark.asyncio
async def test_get_l4():
    v2 = WHOCCAtcDddIndexV2()
    l4_result = await v2.get_l4()
    assert isinstance(l4_result, list)
    for item in l4_result:
        assert isinstance(item, AtcL1234Format)


@pytest.mark.asyncio
async def test_get_l5():
    v2 = WHOCCAtcDddIndexV2()
    l5_result = await v2.get_l5()
    assert isinstance(l5_result, list)
    for item in l5_result:
        assert isinstance(item, AtcL5Format)

@pytest.mark.asyncio
async def test_export_csv():
    v2 = WHOCCAtcDddIndexV2()
    await v2.get_l5()
    v2.export_csv()
