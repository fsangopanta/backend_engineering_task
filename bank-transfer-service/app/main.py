from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.exceptions import IdempotencyConflictError
from app.models import TransferRequest
from app.repository import TransferRepository
from app.services import TransferService

app = FastAPI()

repository = TransferRepository()
service = TransferService(repository)


@app.exception_handler(IdempotencyConflictError)
async def idempotency_handler(request: Request, exc: IdempotencyConflictError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )


@app.post("/transfers")
def create_transfer(request: TransferRequest):
    return service.create_transfer(request)


@app.get("/transfers")
def list_transfers():
    return service.list_transfers()
