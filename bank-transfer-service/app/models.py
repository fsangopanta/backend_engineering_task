from pydantic import BaseModel, Field
from decimal import Decimal

class TransferRequest(BaseModel):
    source_account: str
    target_account: str
    amount: Decimal = Field(gt=0)
    idempotency_key: str