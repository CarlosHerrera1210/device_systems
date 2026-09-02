from fastapi import FastAPI, Response

from app.dependencies.user_dependencies import get_api_config
from app.routes.user_routes import router as user_router
from app.schemas.user_schema import APIMessage


app = FastAPI(
    title="device_systems API",
    version="2.0.0",
    description="API REST para la gestión de usuarios del sistema device_systems.",
    contact={
        "name": "Equipo device_systems",
        "email": "soporte@device_systems.test",
    },
    openapi_tags=[
        {"name": "Health", "description": "Endpoints de verificación del servicio."},
        {"name": "Users", "description": "Gestión del recurso usuarios."},
    ],
)


def add_custom_headers(response: Response) -> None:
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "2.0.0"


@app.get(
    "/",
    response_model=APIMessage,
    tags=["Health"],
    summary="Health check",
    description="Verifica que la API está funcionando correctamente.",
    response_description="Información del estado del servicio.",
)
def health_check(response: Response, config: dict = get_api_config()) -> APIMessage:
    add_custom_headers(response)
    return APIMessage(message=f"{config['app_name']} API funcionando correctamente")


app.include_router(user_router)

