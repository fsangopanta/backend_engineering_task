
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_repository():
    """Reset repository state before every test."""
    app.state.repository.transfers.clear()


def create_payload(**overrides):
    payload = {
        "source_account": "100001",
        "target_account": "200002",
        "amount": "100.50",
        "idempotency_key": "test-key-001",
    }
    payload.update(overrides)
    return payload


class TestTransferAPI:

    def test_create_transfer_returns_200(self):
        response = client.post(
            "/transfers",
            json=create_payload()
        )

        assert response.status_code == 200
        assert "id" in response.json()
        assert response.json()["status"] == "COMPLETED"

    def test_repeated_request_returns_same_transfer(self):
        payload = create_payload()

        first = client.post("/transfers", json=payload)
        second = client.post("/transfers", json=payload)

        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["id"] == second.json()["id"]

    def test_same_key_with_different_amount_returns_409(self):
        first = client.post("/transfers", json=create_payload())
        second = client.post(
            "/transfers",
            json=create_payload(amount="200.00")
        )

        assert first.status_code == 200
        assert second.status_code == 409

    def test_same_key_with_different_target_returns_409(self):
        first = client.post("/transfers", json=create_payload())
        second = client.post(
            "/transfers",
            json=create_payload(target_account="300003")
        )

        assert first.status_code == 200
        assert second.status_code == 409

    def test_different_keys_create_different_transfers(self):
        first = client.post(
            "/transfers",
            json=create_payload(idempotency_key="key-001")
        )
        second = client.post(
            "/transfers",
            json=create_payload(idempotency_key="key-002")
        )

        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["id"] != second.json()["id"]

    @pytest.mark.parametrize("amount", ["0", "-10.00"])
    def test_invalid_amount_returns_422(self, amount):
        response = client.post(
            "/transfers",
            json=create_payload(amount=amount)
        )

        assert response.status_code == 422
