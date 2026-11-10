from decimal import Decimal


class TransferRepository:

    def __init__(self):
        self.transfers = {}

    def save(self, key, transfer):
        self.transfers[key] = transfer

    def find_by_key(self, key):
        return self.transfers.get(key)

    def find_all(self):
        return self.transfers



class AccountRepository:

    def __init__(self):
        self.accounts = {
            "100001": Decimal("100.00"),
            "200002": Decimal("500.00")
        }

    def get_balance(self, account_id):
        return self.accounts.get(account_id)

    def update_balance(self, account_id, amount):
        self.accounts[account_id] = amount

    def list_accounts(self):
        return self.accounts