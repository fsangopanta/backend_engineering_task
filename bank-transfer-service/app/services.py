from decimal import Decimal
from uuid import uuid4

from app.exceptions import IdempotencyConflictError
from app.models import TransferRequest
from app.repository import TransferRepository


class TransferService:

    def __init__(self, repository: TransferRepository):
        self.repository = repository

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
