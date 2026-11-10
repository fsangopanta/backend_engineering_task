from decimal import Decimal
from uuid import uuid4

from app.exceptions import IdempotencyConflictError, AccountNotFoundError, InvalidAmountException
from app.models import TransferRequest
from app.repository import TransferRepository, AccountRepository


class TransferService:

    def __init__(self, repository: TransferRepository, account_repository: AccountRepository):
        self.repository = repository
        self.account_repository = account_repository

    def create_transfer(self, request: TransferRequest):

        existing_transfer = self.repository.find_by_key(request.idempotency_key)

        if existing_transfer is not None:
            is_same_data = (
                    existing_transfer["source_account"] == request.source_account
                    and existing_transfer["target_account"] == request.target_account
                    and Decimal(str(existing_transfer["amount"])) == Decimal(str(request.amount))
            )

            if is_same_data:
                return existing_transfer

            raise IdempotencyConflictError("Transaction rejected")

        transfer = {
            "id": str(uuid4()),
            "source_account": request.source_account,
            "target_account": request.target_account,
            "amount": request.amount,
            "status": "COMPLETED"
        }

        self.repository.save(request.idempotency_key, transfer)
        return transfer

    def list_transfers(self):
        return self.repository.find_all()

    def transfer(self, request:TransferRequest):

        source_balance = self.account_repository.get_balance(
            request.source_account
        )

        target_balance = self.account_repository.get_balance(
            request.target_account
        )

        if source_balance is None:
            raise AccountNotFoundError("Source account not found")

        if target_balance is None:
            raise AccountNotFoundError("Target account not found")

        if source_balance < request.amount:
            raise InvalidAmountException("Insufficient funds")

        new_source_balance = source_balance - request.amount
        new_target_balance = target_balance + request.amount

        self.account_repository.update_balance(
            request.source_account,
            new_source_balance
        )

        self.account_repository.update_balance(
            request.target_account,
            new_target_balance
        )

        return {
            "source_balance": new_source_balance,
            "target_balance": new_target_balance,
            "status": "COMPLETED"
        }

    def list_accounts(self):
        return self.account_repository.list_accounts()