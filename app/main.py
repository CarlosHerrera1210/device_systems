from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse

from app.database.connection import create_tables
from app.dependencies.user_dependencies import get_api_config
from app.models import user_model
from app.routes.user_routes import router as user_router
from app.schemas.user_schema import APIMessage


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="device_systems API",
    version="3.0.0",
    lifespan=lifespan,
    redoc_url=None,
    description="API REST para la gestión de usuarios del sistema device_systems.",
    contact={
        "name": "Equipo device_systems",
        "email": "soporte@devicesystems.com",
    },
    openapi_tags=[
        {"name": "Health", "description": "Endpoints de verificación del servicio."},
        {"name": "Users", "description": "Gestión del recurso usuarios."},
    ],
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

