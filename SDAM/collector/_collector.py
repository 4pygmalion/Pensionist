import os
import sys
import time
import xmltodict
import pandas as pd

import requests
from io import BytesIO
from logging import Logger
from zipfile import ZipFile
from bs4 import BeautifulSoup
from urllib.request import urlopen

COLLECTOR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(COLLECTOR_DIR)

sys.path.append(ROOT_DIR)
from error_handler import AccountNotFound


class DART(object):
    """
    The purpose of this class is to retrieve the financial information from DART
    (http://dart.fss.or.kr/)

    Parameters
    ----------
    cert_key: cert key (https://opendart.fss.or.kr/intro/main.do)
    corp_code : unique key in Open Dart (is not differ in stock code) **
    is_consolidation: 연결 또는 별도 재무재표 여부
        (default: True (연결))

    Example
    -------
        >>> corp_dart = DART(config)
        >>> corp_dart.get_finance_sheet(start_date=2020, report_code=11013)
    """

    def __init__(
        self,
        config: dict,
        logger=Logger(__name__),
        is_consolidation=True,
    ):

        self.config = config
        self.mapper = config["DART"]["MAPPER"]
        self.logger = logger
        self.cert_key = config["DART"]["KEY"]
        self.cope_code_map = dict()
        self.stock_codes = dict()
        self.is_consolidation = is_consolidation

    def _get_corpcode(self) -> list:
        """Get XML file from DART API and parse it

        Return
        ------

        list: including
            OrderedDict(['corp_code', '0043728'],
                        ['corp_name', '다코])
        """

        request_url = (
            "https://opendart.fss.or.kr/api/corpCode.xml?"
            + "crtfc_key="
            + self.cert_key
        )
        xml_zip = urlopen(request_url).read()
        zip_file = ZipFile(BytesIO(xml_zip))
        file = zip_file.namelist()[0]

        with zip_file.open(file) as corpcode_xml:
            corp_xml = xmltodict.parse(corpcode_xml.read())

        return corp_xml["result"]["list"]

    def set_stock_codes(self, market: list = ["KOSPI", "KOSDAQ"]) -> dict:
        """상장된 기업의 기업명, 종목코드를 인스턴스 변수에 저장합니다.

        Example:
            >>> self.set_stock_codes()
            >>> self.stock_codes
            {
                '코리아써키트': {'dart_code': '00152686', 'stock_code': '007810'},
                '텔레필드': {'dart_code': '00560122', 'stock_code': '091440'}
            }

        """

        self.logger.info("In process: load codes of listing companies")

        stokc_list_path = os.path.join(COLLECTOR_DIR, self.config["DATA"]["MARKET"])
        data = pd.read_csv(stokc_list_path, encoding="cp949")

        data = data.loc[data["시장구분"].isin(market)]
        data["단축코드"] = data["단축코드"].apply(
            lambda x: "{:06}".format((int(x)))
            if sum([char.isalpha() for char in x]) == 0
            else str(x)
        )

        for corp_info in self._get_corpcode():
            if not corp_info["stock_code"]:
                continue

            if corp_info["stock_code"] in list(data["단축코드"]):
                self.stock_codes[corp_info["corp_name"]] = {
                    "dart_code": corp_info["corp_code"],
                    "stock_code": corp_info["stock_code"],
                }

        return

    def get_finance_sheet(
        self, dart_code: str, year: int, quarter: int, doctype: str = "CFS"
    ) -> list:
        """단일회사의 전체 재무제표를 조회하여 반환함.

        Args:
            dart_code (str): 회계 대상의 DART_CODE
            year (int): 회계년도.
            quarter (int): 회계년도의 분기
            doctype (str): 문서타입
                - 'CFS':  연결재무재표 (Consolidated Finantial Statement)
                - 'IS' 손익계산서 (Income statetment)

        Example:
        >>> self.get_finance_sheet("00261285", 2022, 1)
        [
            {
                'rcept_no': '20220516002597',
                'reprt_code': '11013',
                'bsns_year': '2022',
                'corp_code': '00261285',
                'sj_div': 'BS',
                'sj_nm': '재무상태표',
                'account_id': 'ifrs-full_CurrentAssets',
                'account_nm': '유동자산',
                'account_detail': '-',
                'thstrm_nm': '제 40 기 1분기말',
                'thstrm_amount': '16255251734327',
                'frmtrm_nm': '제 39 기말',
                'frmtrm_amount': '13147738252924',
                'ord': '1',
                'currency': 'KRW'
            },
            {
                ...
            }
        ]

        See Also:
            https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020
        """

        self.logger.info(f"In process: getting finantial sheet of {dart_code}")

        # URL Type
        if doctype == "CFS":
            url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?"
        elif doctype == "IS":
            url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json?"
        else:
            raise ValueError(f"doctype not expected, given {doctype}")

        # Requested parameters
        try:
            stock_info = requests.get(
                url,
                params={
                    "crtfc_key": self.cert_key,
                    "corp_code": dart_code,
                    "bsns_year": year,
                    "reprt_code": self.mapper[quarter],
                    "fs_div": doctype,
                },
            ).json()

        except:
            self.logger.warning("request fail")
            time.sleep(3)
            return list()

        if stock_info["message"] != "정상":
            self.logger.warning(stock_info["message"])
            return list()

        return stock_info["list"]

    def get_assets(self, fs: list, asset_names: set) -> dict:
        """
        계정명칭(예, 유동자산, 유동부채 등)에 해당하는 당기 금액을 반환합니다.

        Args:
            fs (list): finantial sheet. nested list
            asset_names (set): 계정명칭들

        Return:
            int: 계정명칭의 보고서내 당기금액.
                (못 찾은 경우는 -을 반환)
        """

        assets = dict()
        for account_item in fs:
            if account_item["account_nm"] in asset_names:
                assets[account_item["account_nm"]] = int(account_item["thstrm_amount"])

        return assets

    def create_table(self, account_names: set, year: int, quarter: int) -> pd.DataFrame:
        rows = list()

        for corp_name, corp_codes in self.stock_codes.items():
            fs = self.get_finance_sheet(corp_codes["dart_code"], year, quarter)
            asset_info = self.get_assets(fs, {"유동자산", "유동부채", "비유동자산", "비유동부채"})

            row = [asset_info.get(asset_name, 0) for asset_name in account_names]
            rows.append(row)

        return pd.DataFrame(rows, columns=list(account_names))

    def get_issued_stocks(self, corp_code: str, year: int, quarter: int) -> int:
        """분기보고서에 작성된 발행된 주식의 수를 반환합니다.

        Note:

            응답결과
            result
                status	에러 및 정보 코드	(※메시지 설명 참조)
                message	에러 및 정보 메시지	(※메시지 설명 참조)
            list
                rcept_no	접수번호	접수번호(14자리)
                corp_cls	법인구분	법인구분 : Y(유가), K(코스닥), N(코넥스), E(기타)
                corp_code	고유번호	공시대상회사의 고유번호(8자리)
                corp_name	회사명	공시대상회사명
                se	구분	구분(증권의종류, 합계, 비고)
                isu_stock_totqy	발행할 주식의 총수	Ⅰ. 발행할 주식의 총수, 9,999,999,999
                now_to_isu_stock_totqy	현재까지 발행한 주식의 총수	Ⅱ. 현재까지 발행한 주식의 총수, 9,999,999,999
                now_to_dcrs_stock_totqy	현재까지 감소한 주식의 총수	Ⅲ. 현재까지 감소한 주식의 총수, 9,999,999,999
                redc	감자	Ⅲ. 현재까지 감소한 주식의 총수(1. 감자), 9,999,999,999
                profit_incnr	이익소각	Ⅲ. 현재까지 감소한 주식의 총수(2. 이익소각), 9,999,999,999
                rdmstk_repy	상환주식의 상환	Ⅲ. 현재까지 감소한 주식의 총수(3. 상환주식의 상환), 9,999,999,999
                etc	기타	Ⅲ. 현재까지 감소한 주식의 총수(4. 기타), 9,999,999,999
                istc_totqy	발행주식의 총수	Ⅳ. 발행주식의 총수 (Ⅱ-Ⅲ), 9,999,999,999
                tesstk_co	자기주식수	Ⅴ. 자기주식수, 9,999,999,999
                distb_stock_co	유통주식수	Ⅵ. 유통주식수 (Ⅳ-Ⅴ), 9,999,999,999

        Args:
            corp_code (str): 공시대상회사의 고유번호 8자리 (공시정보->고유번호)

        """

        stock_info = requests.get(
            "https://opendart.fss.or.kr/api/stockTotqySttus.json",
            params={
                "crtfc_key": self.cert_key,
                "corp_code": corp_code,
                "bsns_year": year,
                "reprt_code": self.mapper[quarter],
            },
        ).json()

        if stock_info["message"] != "정상":
            self.logger.warning(stock_info["message"])
            return 0

        return int(stock_info["list"][0]["istc_totqy"].replace(",", ""))


class MarketValueCollector(object):
    """Market Value Data collecter from NAVER finance

    Parameters
    ----------
    corp_code: '014680'
    """

    def __init__(self, corp_code: str):
        self.corp_code = corp_code
        self.bs_obj = self._get_html()

        if self._check_redirection():
            raise ValueError("Ticker not existed")

    def _check_redirection(self):
        """To check rediction due to not existing ticker

        return
        ------
        bool
        """
        return self.bs_obj.find("title").get_text() == "네이버 :: 세상의 모든 지식, 네이버"

    def _get_html(self):
        """Get html from naver stock using BS4"""

        URL = "https://finance.naver.com/item/main.nhn?code={}".format(self.corp_code)
        res = urlopen(URL).read().decode("cp949")
        bs_obj = BeautifulSoup(res, "html.parser")

        return bs_obj

    def get_market_value(self, attr: str) -> int:
        """
        Parameters
        ----------
            attr: str.
                'price': 현재가격
                'n_stock': 발행주식수
                'market_value': 시가총액
        """
        if attr == "price":
            market_sum = self.bs_obj.find("p", attrs={"class": "no_today"})
            spans = market_sum.find_all("span")[1:]
            csv = [tag.get_text() for tag in spans]
            current_price = "".join(csv)
            current_price = int(current_price.replace(",", ""))
            return current_price

        elif attr == "n_stocks":
            div = self.bs_obj.find("table", attrs={"summary": "시가총액 정보"})
            values = div.text.split("\n")
            n_stock = values[values.index("상장주식수") + 1]
            return int(n_stock.replace(",", ""))

        elif attr == "market_value":
            n_sum = self.get_market_value("price") * self.get_market_value("n_stocks")
            return n_sum
