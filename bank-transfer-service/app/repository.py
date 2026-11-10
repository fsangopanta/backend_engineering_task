class TransferRepository:

    def __init__(self):
        self.transfers = {}

    def save(self, key, transfer):
        self.transfers[key] = transfer

    def find_by_key(self, key):
        return self.transfers.get(key)

    def find_all(self):
        return self.transfers