import os
import sys
from logging import Logger
import pandas as pd

STRATEGY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(STRATEGY_DIR)
LOG_DIR = os.path.join(ROOT_DIR, "log")
SAVE_DIR = os.path.join(ROOT_DIR, "results")
sys.path.append(ROOT_DIR)


class Indicator:
    def __init__(self, logger: Logger = Logger(__name__)):
        self.logger = logger

    def get_current_net_asset(
        self,
        current_asset: int,
        current_liab: int,
        non_current_liab: int,
    ) -> int:
        return current_asset - (current_liab + non_current_liab)

    def get_net_current_asset_per_share(
        self, current_net_asset: int, issued_stock: int, stock_price: int
    ) -> int:

        if stock_price == 0 or issued_stock == 0:
            self.logger.debug("passed market value is 0")
            return 0

        return current_net_asset / (stock_price * issued_stock)

    def indicate(self, table: pd.DataFrame) -> pd.DataFrame:

        self.logger.info("In processing: indicating NCAV of each coopreation.")

        table["NCAV"] = table.apply(
            lambda x: self.get_current_net_asset(
                x["CURRENT_ASSET"], x["CURRENT_LIAB"], x["NON_CURRENT_LIAB"]
            ),
            axis=1,
        )
        table["NCAV_SHARE"] = table.apply(
            lambda x: self.get_net_current_asset_per_share(
                x["NCAV"], x["ISSUED_STOCK"], x["STOCK_PRICE"]
            ),
            axis=1,
        )

        self.logger.info("End of processing: indicating NCAV of each coopreation.")

        return table
