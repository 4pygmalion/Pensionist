class AccountNotFound(KeyError):
    def __init__(self, msg):
        self.msg = msg
