import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse

from app.auth.auth_routes import router as auth_router
from app.dependencies.user_dependencies import get_api_config
from app.middlewares.request_middleware import request_middleware
from app.security.rate_limit import limiter
from app.models import Device, Loan, User
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.routes.user_routes import router as user_router
from app.schemas.user_schema import APIMessage

load_dotenv()

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    ).split(",")
    if origin.strip()
]


app = FastAPI(
    title="device_systems API",
    version="3.0.0",
    redoc_url=None,
    description="API REST segura para gestionar usuarios, dispositivos y préstamos.",
    contact={
        "name": "Equipo device_systems",
        "email": "soporte@device_systems.test",
        "email": "soporte@devicesystems.com",
    },
    openapi_tags=[
        {"name": "Health", "description": "Endpoints de verificación del servicio."},
        {"name": "Users", "description": "Gestión del recurso usuarios."},
        {"name": "Devices", "description": "Gestión del inventario de dispositivos."},
        {"name": "Loans", "description": "Gestión de préstamos y consultas relacionadas."},
        {"name": "Auth", "description": "Registro, login y sesión OAuth2/JWT."},
        {"name": "Security", "description": "Controles de seguridad y protección de la API."},
    ],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.middleware("http")(request_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/redoc", include_in_schema=False)
def redoc() -> HTMLResponse:
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.5.0/bundles/redoc.standalone.js",
    )


def add_custom_headers(response: Response) -> None:
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0.0"


@app.get(
    "/",
    response_model=APIMessage,
    tags=["Health"],
    summary="Health check",
    description="Verifica que la API está funcionando correctamente.",
    response_description="Información del estado del servicio.",
)
def health_check(response: Response, config: dict = Depends(get_api_config)) -> APIMessage:
    add_custom_headers(response)
    return APIMessage(message=f"{config['app_name']} API funcionando correctamente")


app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)
app.include_router(auth_router)

