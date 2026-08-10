from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import pytest
from main import MOCK_SHIPMENTS, app

client = TestClient(app)
AUTH_HEADERS = {"X-API-Key": "techstar-fde-key-001"}


# --- Auth Tests ---
def test_missing_api_key_returns_401():
    response = client.get("/shipments")
    assert response.status_code == 401


def test_invalid_api_key_returns_403():
    response = client.get("/shipments", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 403


# --- Shipment CRUD Tests ---
def test_list_shipments_returns_all():
    response = client.get("/shipments", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) == len(MOCK_SHIPMENTS)


def test_list_shipments_filters_by_status_and_carrier():
    response = client.get(
        "/shipments?status=delayed&carrier=BLUEDART", headers=AUTH_HEADERS
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["status"] == "delayed"


def test_get_shipment_success():
    response = client.get("/shipments/SH001", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["shipment_id"] == "SH001"


def test_get_shipment_not_found_returns_404():
    response = client.get("/shipments/NONEXISTENT", headers=AUTH_HEADERS)
    assert response.status_code == 404


def test_create_shipment_success():
    payload = {
        "shipment_id": "SH999",
        "carrier": "dhl",
        "origin": "Mumbai",
        "destination": "Pune",
        "cost_usd": 99.0,
    }
    response = client.post("/shipments", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 201
    assert response.json()["carrier"] == "DHL"


def test_create_shipment_invalid_carrier_returns_422():
    payload = {
        "shipment_id": "SH998",
        "carrier": "UPS",
        "origin": "Mumbai",
        "destination": "Pune",
        "cost_usd": 99.0,
    }
    response = client.post("/shipments", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422


def test_create_shipment_duplicate_id_returns_409():
    payload = {
        "shipment_id": "SH001",
        "carrier": "DHL",
        "origin": "Mumbai",
        "destination": "Pune",
        "cost_usd": 50.0,
    }
    response = client.post("/shipments", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 409


def test_list_carriers_success():
    response = client.get("/carriers", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) == 3


# --- Aggregation Endpoint Mocked Tests ---
@patch("main.call_vendor_c", new_callable=AsyncMock)
@patch("main.call_vendor_b", new_callable=AsyncMock)
@patch("main.call_vendor_a", new_callable=AsyncMock)
def test_supply_chain_status_all_vendors_succeed(mock_a, mock_b, mock_c):
    mock_a.return_value = {"id": "SH001", "current_status": "in_transit"}
    mock_b.return_value = {"shipmentRef": "SH001", "trackingState": "DELAYED"}
    mock_c.return_value = {
        "shipment": {"identifier": "SH001", "state": {"code": "DELIVERED"}}
    }

    response = client.get("/supply-chain-status/SH001", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) == 3


@patch("main.call_vendor_c", new_callable=AsyncMock)
@patch("main.call_vendor_b", new_callable=AsyncMock)
@patch("main.call_vendor_a", new_callable=AsyncMock)
def test_supply_chain_status_one_vendor_fails(mock_a, mock_b, mock_c):
    mock_a.return_value = {"id": "SH001", "current_status": "in_transit"}
    mock_b.side_effect = ConnectionError("Vendor B timeout")
    mock_c.return_value = {
        "shipment": {"identifier": "SH001", "state": {"code": "DELIVERED"}}
    }

    response = client.get("/supply-chain-status/SH001", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert len(response.json()) == 2


@patch("main.call_vendor_c", new_callable=AsyncMock)
@patch("main.call_vendor_b", new_callable=AsyncMock)
@patch("main.call_vendor_a", new_callable=AsyncMock)
def test_supply_chain_status_all_vendors_fail_returns_503(mock_a, mock_b, mock_c):
    mock_a.side_effect = ConnectionError("down")
    mock_b.side_effect = ConnectionError("down")
    mock_c.side_effect = ConnectionError("down")

    response = client.get("/supply-chain-status/SH001", headers=AUTH_HEADERS)
    assert response.status_code == 503
