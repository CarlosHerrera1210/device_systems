import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import get_current_active_user
from app.main import app
from app.models.user_model import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ev10_device_systems.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_current_user():
    return User(id=1, name="Test Admin", email="test-admin@example.com", role="admin", is_active=True)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_current_user
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_user_and_device_and_loan_flow():
    user_payload = {
        "name": "Ana Perez",
        "email": "ana@sena.edu.co",
        "role": "admin",
        "is_active": True,
    }
    user_response = client.post("/users", json=user_payload)
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    device_payload = {
        "name": "Laptop Lenovo ThinkPad",
        "serial_number": "LEN-2024-001",
        "device_type": "laptop",
        "brand": "Lenovo",
        "is_available": True,
    }
    device_response = client.post("/devices", json=device_payload)
    assert device_response.status_code == 201
    device_id = device_response.json()["id"]

    loan_payload = {
        "user_id": user_id,
        "device_id": device_id,
        "status": "active",
    }
    loan_response = client.post("/loans", json=loan_payload)
    assert loan_response.status_code == 201
    assert loan_response.json()["status"] == "active"

    device_after_loan = client.get(f"/devices/{device_id}")
    assert device_after_loan.status_code == 200
    assert device_after_loan.json()["is_available"] is False


def test_filter_loans_by_status_and_user_email():
    user_response = client.post(
        "/users",
        json={
            "name": "Carlos Herrera",
            "email": "carlos@correo.com",
            "role": "support",
            "is_active": True,
        },
    )
    device_response = client.post(
        "/devices",
        json={
            "name": "Tablet Samsung",
            "serial_number": "TAB-2024-001",
            "device_type": "tablet",
            "brand": "Samsung",
            "is_available": True,
        },
    )
    user_id = user_response.json()["id"]
    device_id = device_response.json()["id"]

    client.post("/loans", json={"user_id": user_id, "device_id": device_id, "status": "active"})

    response = client.get("/loans?status=active&user_email=carlos@correo.com")
    assert response.status_code == 200
    assert response.json()["total"] >= 1

    device_response = client.get(f"/devices?device_type=tablet")
    assert device_response.status_code == 200
    assert device_response.json()["total"] >= 1


def test_return_loan_marks_device_available_again():
    user_response = client.post(
        "/users",
        json={
            "name": "Luis Gomez",
            "email": "luis@example.com",
            "role": "user",
            "is_active": True,
        },
    )
    device_response = client.post(
        "/devices",
        json={
            "name": "Proyector Epson",
            "serial_number": "PRO-2024-001",
            "device_type": "proyector",
            "brand": "Epson",
            "is_available": True,
        },
    )

    loan_response = client.post(
        "/loans",
        json={
            "user_id": user_response.json()["id"],
            "device_id": device_response.json()["id"],
            "status": "active",
        },
    )
    loan_id = loan_response.json()["id"]

    return_response = client.patch(f"/loans/{loan_id}/return")
    assert return_response.status_code == 200
    assert return_response.json()["status"] == "returned"

    device_after_return = client.get(f"/devices/{device_response.json()['id']}")
    assert device_after_return.status_code == 200
    assert device_after_return.json()["is_available"] is True


def test_device_not_available_business_rule():
    user_response = client.post(
        "/users",
        json={
            "name": "Maria Lopez",
            "email": "maria@example.com",
            "role": "user",
            "is_active": True,
        },
    )
    device_response = client.post(
        "/devices",
        json={
            "name": "Router Cisco",
            "serial_number": "ROU-2024-001",
            "device_type": "router",
            "brand": "Cisco",
            "is_available": True,
        },
    )

    first_loan = client.post(
        "/loans",
        json={
            "user_id": user_response.json()["id"],
            "device_id": device_response.json()["id"],
            "status": "active",
        },
    )
    assert first_loan.status_code == 201

    second_loan = client.post(
        "/loans",
        json={
            "user_id": user_response.json()["id"],
            "device_id": device_response.json()["id"],
            "status": "active",
        },
    )
    assert second_loan.status_code == 409
