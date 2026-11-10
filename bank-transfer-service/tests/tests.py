import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from app.exceptions import IdempotencyConflictError
from app.models import TransferRequest
from app.repository import TransferRepository
from app.services import TransferService


class TestTransferServiceUnit:
    """Tests unitarios usando Mocks (sin base de datos)."""

    @pytest.fixture
    def mock_repository(self):
        return MagicMock(spec=TransferRepository)

    @pytest.fixture
    def service(self, mock_repository):
        return TransferService(repository=mock_repository)

    @pytest.fixture
    def transfer_request(self):
        return TransferRequest(
            source_account="source_account",
            target_account="target_account",
            idempotency_key="idempotency_key",
            amount=Decimal("1.00"),
        )

    def test_should_return_transfer_when_transfer_is_ok(self, service, mock_repository, transfer_request):
        mock_repository.find_by_key.return_value = None

        result = service.create_transfer(transfer_request)

        assert result["source_account"] == "source_account"
        assert result["amount"] == Decimal("1.00")
        assert result["status"] == "COMPLETED"
        assert "id" in result

        mock_repository.save.assert_called_once()
        args, _ = mock_repository.save.call_args
        assert args[0] == "idempotency_key"

    def test_should_return_same_transfer_when_idempotency_key_already_exists(
            self, service, mock_repository, transfer_request
    ):
        existing_transfer = {
            "id": "id-generado-antes-12345",
            "source_account": "source_account",
            "target_account": "target_account",
            "amount": Decimal("1.00"),
            "status": "COMPLETED",
        }
        mock_repository.find_by_key.return_value = existing_transfer

        result = service.create_transfer(transfer_request)

        assert result["id"] == "id-generado-antes-12345"
        mock_repository.save.assert_not_called()

    def test_should_reject_transfer_when_idempotency_key_already_exists_and_data_is_diferent(
            self, service, mock_repository, transfer_request
    ):
        existing_transfer = {
            "id": "id-generado-antes-12345",
            "source_account": "source_account1",
            "target_account": "target_account",
            "amount": Decimal("1.00"),
            "status": "COMPLETED",
            "idempotency_key": "idempotency_key",
        }

        mock_repository.find_by_key.return_value = existing_transfer

        with pytest.raises(IdempotencyConflictError, match="Transaction rejected"):
            service.create_transfer(transfer_request)

        mock_repository.save.assert_not_called()


class TestTransferServiceIntegration:
    """Tests de integración con el repositorio real en memoria."""

    @pytest.fixture
    def repository(self):
        return TransferRepository()

    @pytest.fixture
    def service(self, repository):
        return TransferService(repository=repository)

    def test_idempotency_with_real_repository(self, service, repository):
        request = TransferRequest(
            source_account="A",
            target_account="B",
            idempotency_key="key-123",
            amount=Decimal("50.00"),
        )

        result1 = service.create_transfer(request)
        assert repository.find_by_key("key-123") is not None

        result2 = service.create_transfer(request)

        assert result1["id"] == result2["id"]
        assert len(repository.transfers) == 1
