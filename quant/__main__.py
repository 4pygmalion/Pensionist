import os
import yaml
import argparse

SDAM_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SDAM_DIR)
LOG_DIR = os.path.join(ROOT_DIR, "log")
RESULT_DIR = os.path.join(ROOT_DIR, "results")

from utils import get_logger
from quant.collector import DART
from annotator import Annotator
from indicator import Indicator


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-k",
        "--key",
        type=str,
        required=True,
        help="DART API key from https://opendart.fss.or.kr/",
    )

    return parser.parse_args()


def load_config() -> dict:
    with open(os.path.join(SDAM_DIR, "config.yaml")) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


if __name__ == "__main__":
    ARGS = get_args()
    CONFIG = load_config()
    CONFIG["DART"]["KEY"] = ARGS.key
    CONFIG["ENV"]["SAVE_DIR"] = RESULT_DIR
    INDEX_COL = "KRX_CODE"
    LOGGER = get_logger("MAIN", file_path=os.path.join(LOG_DIR, "main.log"))
    os.makedirs(RESULT_DIR, exist_ok=True)

    DART_API = DART(CONFIG, logger=LOGGER)
    table = DART_API.create_table(
        ["유동자산", "유동부채", "비유동자산", "비유동부채"], 2022, 1
    )
    table.to_csv(os.path.join(RESULT_DIR, "finance_table.csv"))

    annotator = Annotator(LOGGER)
    table = annotator.annotate(table)
    table.to_csv(os.path.join(RESULT_DIR, "annotated_table.csv"), encoding="utf-8")

    indicator = Indicator(LOGGER)
    indicator.indicate(table)
    table.to_csv(os.path.join(RESULT_DIR, "indicated_table.csv"), encoding="utf-8")
