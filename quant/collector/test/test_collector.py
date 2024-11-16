import os
import sys
import yaml
import pytest
from unittest.mock import Mock, patch

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
COLLECTOR_DIR = os.path.dirname(TEST_DIR)
ROOT_DIR = os.path.dirname(COLLECTOR_DIR)
sys.path.append(ROOT_DIR)
from collector import DART


@pytest.fixture(scope="module")
def config():
    with open(os.path.join(ROOT_DIR, "config.yaml")) as f:
        _config = yaml.safe_load(f)
    yield _config


@pytest.fixture(scope="module")
def dart_collector(config):
    dart = DART(config, Mock())
    return dart


def test_create_table(dart_collector):

    dart_collector.get_finance_sheet = Mock(
        side_effect=[
            [
                {
                    "rcept_no": "20220516001861",
                    "reprt_code": "11013",
                    "bsns_year": "2022",
                    "corp_code": "00152686",
                    "sj_div": "BS",
                    "sj_nm": "재무상태표",
                    "account_id": "ifrs-full_CurrentAssets",
                    "account_nm": "유동자산",
                    "account_detail": "-",
                    "thstrm_nm": "제 51 기 1분기말",
                    "thstrm_amount": "596695845194",
                    "frmtrm_nm": "제 50 기말",
                    "frmtrm_amount": "616191020534",
                    "ord": "1",
                    "currency": "KRW",
                },
                {
                    "rcept_no": "20220516001861",
                    "reprt_code": "11013",
                    "bsns_year": "2022",
                    "corp_code": "00152686",
                    "sj_div": "BS",
                    "sj_nm": "재무상태표",
                    "account_id": "ifrs-full_CashAndCashEquivalents",
                    "account_nm": "현금및현금성자산",
                    "account_detail": "-",
                    "thstrm_nm": "제 51 기 1분기말",
                    "thstrm_amount": "140328007776",
                    "frmtrm_nm": "제 50 기말",
                    "frmtrm_amount": "71522634066",
                    "ord": "2",
                    "currency": "KRW",
                },
            ],
            [
                {
                    "rcept_no": "20220516001861",
                    "reprt_code": "11013",
                    "bsns_year": "2022",
                    "corp_code": "00152686",
                    "sj_div": "BS",
                    "sj_nm": "재무상태표",
                    "account_id": "ifrs-full_CurrentAssets",
                    "account_nm": "유동자산",
                    "account_detail": "-",
                    "thstrm_nm": "제 51 기 1분기말",
                    "thstrm_amount": "596695845194",
                    "frmtrm_nm": "제 50 기말",
                    "frmtrm_amount": "616191020534",
                    "ord": "1",
                    "currency": "KRW",
                },
                {
                    "rcept_no": "20220516001861",
                    "reprt_code": "11013",
                    "bsns_year": "2022",
                    "corp_code": "00152686",
                    "sj_div": "BS",
                    "sj_nm": "재무상태표",
                    "account_id": "ifrs-full_CashAndCashEquivalents",
                    "account_nm": "현금및현금성자산",
                    "account_detail": "-",
                    "thstrm_nm": "제 51 기 1분기말",
                    "thstrm_amount": "140328007776",
                    "frmtrm_nm": "제 50 기말",
                    "frmtrm_amount": "71522634066",
                    "ord": "2",
                    "currency": "KRW",
                },
            ],
        ]
    )

    dart_collector.set_stock_codes = Mock()
    dart_collector.stock_codes = {
        "코리아써키트": {"dart_code": "00152686", "stock_code": "007810"},
        "텔레필드": {"dart_code": "00560122", "stock_code": "091440"},
    }

    account_names = ["유동자산", "유동부채", "비유동자산", "비유동부채"]
    result_table = dart_collector.create_table(account_names, 2022, 1)

    expected_columns = [
        "CORP_NAME",
        "DART_CODE",
        "CURRENT_ASSET",
        "CURRENT_LIAB",
        "NON_CURRENT_ASSET",
        "NON_CURRENT_LIAB",
    ]

    assert expected_columns == list(result_table.columns)
