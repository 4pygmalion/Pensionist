class EnterpriseValue:
    def __init__(self, config):
        self.config = config

    def calculate(
        self,
        operating_profit: int,
        current_asset: int,
        current_liabilities: int,
        non_current_asset:int,
        issued_shares: int,
    ) -> int:

        """
        주당 기업가치을 계산함

        Args:
            operating_profit (int): 영업이익
            current_asset (int): 유동자산. 1년미만의 처분가능한 자산
            current_liabilities (int): 유동부채. 1년미만으로 갚아야할 부채
            non_current_asset (int): 비유동자산. 1년 이상의 기간으로 처분해야할 자산(예, 투자자산)
            issued_shares (int): 발행주식수
        """

        business_value = operating_profit * 10
        asset_value = current_asset - current_liabilities *1.1
        share_holder_value = business_value - asset_value + non_current_asset* self.config["NON_CURRNET_ASSET_DISCOUNT"]
        return share_holder_value / issued_shares

    def buffer_safety_margin(self, value_per_share: int) -> float:
        return
