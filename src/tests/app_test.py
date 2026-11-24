"""Tests for the warehouse web application."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app import create_app


@pytest.fixture
def client():
    """Return a fresh test client for each test."""
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="test")
    return app.test_client()


def create_warehouse(client, name="Drinks", capacity="10", stock="0"):
    return client.post(
        "/warehouses",
        data={"name": name, "capacity": capacity, "initial_stock": stock},
        follow_redirects=True,
    )


def test_home_page_shows_empty_warehouse_list(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"No warehouses yet" in response.data


def test_can_create_and_list_multiple_warehouses(client):
    create_warehouse(client, "Drinks", "10", "2")
    response = create_warehouse(client, "Dry goods", "25")

    assert b"Drinks" in response.data
    assert b"Dry goods" in response.data
    assert b"Remaining space:" in response.data
    assert b"Inventory: 2 / 10" in response.data


def test_can_add_and_take_inventory(client):
    create_warehouse(client)
    client.post("/warehouses/1/add", data={"amount": "7"})
    response = client.post(
        "/warehouses/1/take", data={"amount": "3"}, follow_redirects=True
    )

    assert b"Inventory: 4 / 10" in response.data
    assert b"Remaining space:" in response.data


def test_adding_inventory_does_not_exceed_capacity(client):
    create_warehouse(client)
    response = client.post(
        "/warehouses/1/add", data={"amount": "15"}, follow_redirects=True
    )

    assert b"Inventory: 10 / 10" in response.data
    assert b"Added 10 to Drinks" in response.data


@pytest.mark.parametrize(
    "data", [
        {"name": "", "capacity": "10", "initial_stock": "0"},
        {"name": "Bad capacity", "capacity": "0", "initial_stock": "0"},
        {"name": "Bad number", "capacity": "invalid", "initial_stock": "0"},
        {"name": "Too full", "capacity": "3", "initial_stock": "4"},
    ]
)
def test_invalid_warehouse_is_not_created(client, data):
    response = client.post("/warehouses", data=data, follow_redirects=True)

    assert b"class=\"message error\"" in response.data
    assert b"No warehouses yet" in response.data


def test_duplicate_warehouse_names_are_rejected_case_insensitively(client):
    create_warehouse(client, "Drinks")
    response = create_warehouse(client, "drinks")

    assert b"already exists" in response.data
    assert response.data.count(b"<h3>Drinks</h3>") == 1


@pytest.mark.parametrize("amount", ["0", "-2", "invalid", "inf"])
def test_invalid_inventory_operations_do_not_change_stock(client, amount):
    create_warehouse(client)
    response = client.post(
        "/warehouses/1/add", data={"amount": amount}, follow_redirects=True
    )

    assert b"Inventory: 0 / 10" in response.data
    assert b"class=\"message error\"" in response.data


def test_taking_more_than_available_only_removes_existing_inventory(client):
    create_warehouse(client, stock="2")
    response = client.post(
        "/warehouses/1/take", data={"amount": "5"}, follow_redirects=True
    )

    assert b"Inventory: 0 / 10" in response.data
    assert b"Took 2 from Drinks" in response.data
