import pytest

from whocc.symbol import ACT_DDD_ROOT_URL


@pytest.fixture(scope="function")
def source_root_url() -> str:
    return ACT_DDD_ROOT_URL
