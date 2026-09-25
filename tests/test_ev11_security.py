import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.main import app
from app.security.rate_limit import limiter

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_ev11_security.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides.pop(get_current_active_user, None)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides.pop(get_current_active_user, None)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    if hasattr(limiter, "reset"):
        limiter.reset()
    yield
    Base.metadata.drop_all(bind=engine)


def register(email="security@example.com", role="user", password="SecurePass1"):
    return client.post(
        "/auth/register",
        json={
            "name": "Security User",
            "email": email,
            "password": password,
            "role": role,
        },
    )


def login(email="security@example.com", password="SecurePass1"):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_register_hashes_password_and_login_returns_jwt():
    response = register()
    assert response.status_code == 201
    assert "hashed_password" not in response.json()

    db = TestingSessionLocal()
    user = db.query(__import__("app.models.user_model", fromlist=["User"]).User).one()
    assert user.hashed_password.startswith("$2")
    db.close()

    token_response = login()
    assert token_response.status_code == 200
    assert token_response.json()["token_type"] == "bearer"
    assert token_response.json()["access_token"]


def test_password_validation_duplicate_and_wrong_login():
    weak = register(email="weak@example.com", password="weak")
    assert weak.status_code == 422

    assert register().status_code == 201
    duplicate = register()
    assert duplicate.status_code == 400
    wrong_password = login(password="WrongPass1")
    assert wrong_password.status_code == 401


def test_public_registration_cannot_assign_admin_role():
    response = register(email="public-admin@example.com", role="admin")

    assert response.status_code == 422


def test_auth_me_and_protected_route_errors():
    assert register().status_code == 201
    token = login().json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert "hashed_password" not in me.json()

    assert client.get("/users").status_code == 401
    assert client.get("/users", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_middleware_headers_and_cors(caplog):
    caplog.set_level("INFO", logger="device_systems.requests")
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["X-App-Name"] == "device_systems"
    assert "X-Process-Time" in response.headers
    assert response.headers["X-Request-ID"]
    assert "method=GET" in caplog.text
    assert "path=/" in caplog.text
    assert "status_code=200" in caplog.text
    assert response.headers["X-Request-ID"] in caplog.text

    cors = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert cors.status_code == 200
    assert cors.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_login_rate_limit_returns_429():
    assert register(email="rate@example.com").status_code == 201
    responses = [login(email="rate@example.com", password="WrongPass1") for _ in range(6)]
    assert [response.status_code for response in responses[:5]] == [401] * 5
    assert responses[5].status_code == 429


def test_role_authorization_rejects_forbidden_operation():
    assert register(email="support@example.com", role="support").status_code == 201
    token = login(email="support@example.com").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    device = client.post(
        "/devices",
        json={
            "name": "Equipo de soporte",
            "serial_number": "SUP-EV11-001",
            "device_type": "monitor",
            "brand": "Dell",
            "is_available": True,
        },
        headers=headers,
    )
    assert device.status_code == 201

    forbidden = client.delete(f"/devices/{device.json()['id']}", headers=headers)
    assert forbidden.status_code == 403
