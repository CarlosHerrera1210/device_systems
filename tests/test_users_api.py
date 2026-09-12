import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.dependencies.database_dependency import get_db
from app.main import app
from app.models.user_model import User


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_device_systems.db"

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


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add_all(
        [
            User(
                name="Carlos Herrera",
                email="carlos@example.com",
                role="admin",
                is_active=True,
            ),
            User(
                name="Laura Gomez",
                email="laura@example.com",
                role="support",
                is_active=True,
            ),
            User(
                name="Andres Perez",
                email="andres@example.com",
                role="user",
                is_active=False,
            ),
        ]
    )
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_endpoint_returns_custom_headers():
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-App-Name"] == "device_systems"
    assert response.headers["X-API-Version"] == "3.0.0"


def test_openapi_schema_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "device_systems API"
    assert "/users" in response.json()["paths"]


def test_redoc_page_uses_available_stable_bundle():
    response = client.get("/redoc")

    assert response.status_code == 200
    assert "redoc@2.5.0/bundles/redoc.standalone.js" in response.text


def test_list_users_returns_headers_and_users():
    response = client.get("/users")

    assert response.status_code == 200
    assert response.headers["X-App-Name"] == "device_systems"
    assert response.headers["X-API-Version"] == "3.0.0"
    assert response.json()["total"] == 3


def test_get_user_by_id():
    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json()["email"] == "carlos@example.com"
    assert "created_at" in response.json()


def test_filter_users_by_role():
    response = client.get("/users?role=admin")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["users"][0]["role"] == "admin"


def test_filter_users_by_active_status():
    response = client.get("/users?is_active=false")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["users"][0]["is_active"] is False


def test_order_users_by_name():
    response = client.get("/users?order_by=name")

    assert response.status_code == 200
    names = [user["name"] for user in response.json()["users"]]
    assert names == sorted(names)


def test_create_user():
    payload = {
        "name": "Maria Lopez",
        "email": "maria.lopez@example.com",
        "role": "user",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == "maria.lopez@example.com"
    assert response.json()["role"] == "user"


def test_duplicate_email_returns_bad_request():
    payload = {
        "name": "Carlos Herrera",
        "email": "carlos@example.com",
        "role": "admin",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 400


def test_invalid_name_returns_validation_error():
    payload = {
        "name": "Al",
        "email": "alberto@example.com",
        "role": "support",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 422


def test_invalid_email_returns_validation_error():
    payload = {
        "name": "Alberto Torres",
        "email": "correo-no-valido",
        "role": "user",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 422


def test_invalid_role_returns_validation_error():
    payload = {
        "name": "Pedro Ruiz",
        "email": "pedro@example.com",
        "role": "manager",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 422


def test_database_rejects_invalid_role_constraint():
    db = TestingSessionLocal()
    db.add(
        User(
            name="Rol Invalido",
            email="rol.invalido@example.com",
            role="manager",
            is_active=True,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()
    db.close()


def test_unknown_user_returns_not_found():
    response = client.get("/users/999")

    assert response.status_code == 404


def test_update_user_full():
    payload = {
        "name": "Carlos Actualizado",
        "email": "carlos.actualizado@example.com",
        "role": "support",
        "is_active": False,
    }

    response = client.put("/users/1", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Carlos Actualizado"
    assert response.json()["role"] == "support"


def test_update_user_partial():
    payload = {"role": "support"}

    response = client.patch("/users/1", json=payload)

    assert response.status_code == 200
    assert response.json()["role"] == "support"


def test_patch_empty_returns_bad_request():
    response = client.patch("/users/1", json={})

    assert response.status_code == 400


def test_delete_user():
    response = client.delete("/users/1")

    assert response.status_code == 204
    assert client.get("/users/1").status_code == 404


def test_delete_unknown_user_returns_not_found():
    response = client.delete("/users/999")

    assert response.status_code == 404

