import os
import sys
import pytest
import pandas as pd
from unittest.mock import Mock

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
ANNOT_DIR = os.path.dirname(TEST_DIR)

sys.path.append(ANNOT_DIR)

from annotator import Annotator


@pytest.fixture()
def annotator():
    return Annotator(Mock())


def test_annotate_error(annotator):
    table = pd.DataFrame(
        data=[
            [
                "00956028",
                "엑세스바이오",
                "950130",
                "34423861",
                "121180026",
                "370201176",
                "761374506",
            ],
            [
                "00783246",
                "글로벌에스엠",
                "900070",
                "71183918",
                "258756994",
                "160606524",
                "550811241",
            ],
        ],
        columns=[
            "dart_code",
            "corp_name",
            "stock_code",
            "비유동부채",
            "비유동자산",
            "유동부채",
            "유동자산",
        ],
    )
    table.set_index("stock_code", inplace=True)
    result_table = annotator.annotate(table)
    assert "stock_price" in result_table.columns
