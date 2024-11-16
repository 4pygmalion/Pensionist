import os
import sys
import pytest
from unittest.mock import Mock

from bs4 import BeautifulSoup

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
ANNOT_DIR = os.path.dirname(TEST_DIR)

sys.path.append(ANNOT_DIR)

from financial_data_crawler import FinancialDataCrawler


@pytest.fixture(scope="module")
def crawler():
    return FinancialDataCrawler(Mock())


def test_get_bs4_obj(crawler):
    assert isinstance(crawler.get_bs4_obj("005930"), BeautifulSoup)


def test_get_stock_price(crawler):
    assert isinstance(crawler.get_stock_price("005930"), int)
