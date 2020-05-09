
from fastapi.testclient import TestClient
import pytest
from main import app, logger
import logging

client = TestClient(app)

def test_create_item():
    for i in range(1,100):
        response = client.post(
            "/checkout",
            json={"email": str(i)+"@email.domain", "username": str(i), "cost_spend": i, "item_count": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['email']
        assert data['username']
        assert data['billing_amount']
        assert data['id']
    logger.info("SUCCESS!")