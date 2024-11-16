from logging import Logger
from urllib.request import urlopen
from bs4 import BeautifulSoup


class FinancialDataCrawler(object):
    """financial Data Crawler from Naver finance

    Parameters
    ----------
    logger (Logger): python built-in logger
    """

    def __init__(self, logger: Logger = Logger(__name__)) -> None:
        self.logger = logger

    def _check_redirection(self, bs_obj):
        """To check rediction due to not existing ticker

        return
        ------
        bool
        """
        return bs_obj.find("title").get_text() == "네이버 :: 세상의 모든 지식, 네이버"

    def get_bs4_obj(self, corp_code: str):
        """get attribute from naver financial.

        Args:
            corp_code (str): cooperation code nominated by KRX
            attribute (str): data label
        """

        URL = "https://finance.naver.com/item/main.nhn?code={}".format(corp_code)
        res = urlopen(URL).read().decode("cp949")
        bs_obj = BeautifulSoup(res, "html.parser")

        if self._check_redirection(bs_obj):
            raise ValueError("Ticker not existed")

        return bs_obj

    def get_stock_price(self, corp_code: str) -> int:
        self.logger.debug(f"In processing: {corp_code} stock_price crawling")

        try:
            bs4_obj = self.get_bs4_obj(corp_code)
        except:
            self.logger.warning(f"{corp_code} was not found")
            return 0

        market_sum = bs4_obj.find("p", attrs={"class": "no_today"})

        try:
            spans = market_sum.find_all("span")[1:]
            csv = [tag.get_text() for tag in spans]
            current_price = "".join(csv)
            current_price = int(current_price.replace(",", ""))
            return current_price

        except:
            self.logger.debug(f"{corp_code} was not parsed")
            return 0
