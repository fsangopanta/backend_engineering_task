from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.exceptions import IdempotencyConflictError, InvalidAmountException, AccountNotFoundError
from app.models import TransferRequest
from app.repository import TransferRepository, AccountRepository
from app.services import TransferService

app = FastAPI()

app.state.repository = TransferRepository()
app.state.account_repository = AccountRepository()

service = TransferService(app.state.repository, app.state.account_repository)


@app.exception_handler(IdempotencyConflictError)
async def idempotency_handler(request: Request, exc: IdempotencyConflictError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )


@app.exception_handler(InvalidAmountException)
async def invalid_amount(request: Request, exc: InvalidAmountException):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(AccountNotFoundError)
async def account_not_found(request: Request, exc: AccountNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )


@app.post("/transfers")
def create_transfer(request: TransferRequest):
    return service.create_transfer(request)


@app.post("/transfer")
def get_transfer(request: TransferRequest):
    return service.transfer(request)


@app.get("/transfers")
def list_transfers():
    return service.list_transfers()


@app.get("/accounts")
def list_accounts():
    return service.list_accounts()
