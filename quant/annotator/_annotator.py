import os
import sys
from logging import Logger

import pandas as pd

ANNOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ANNOT_DIR)

from financial_data_crawler import FinancialDataCrawler


class Annotator:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.finantial_crawler = FinancialDataCrawler(logger)

    def annotate(self, table: pd.DataFrame) -> pd.DataFrame:

        self.logger.info("In processing: Annotation of stock price.")

        if table.index.name is None:
            ValueError("Expected table with index, passed not set-index table")

        prices = list()
        for idx, row in table.iterrows():
            stock_code = row.name
            prices.append(self.finantial_crawler.get_stock_price(stock_code))

        table["STOCK_PRICE"] = prices

        self.logger.info("End of processing: Annotation of stock price.")
        return table
