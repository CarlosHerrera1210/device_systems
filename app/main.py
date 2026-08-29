from fastapi import FastAPI, Response

from app.routes.user_routes import router as user_router
from app.schemas.user_schema import APIMessage


app = FastAPI(
    title="device_systems API",
    version="1.0",
    description="API REST para la gestion de usuarios del sistema device_systems.",
)


def add_custom_headers(response: Response) -> None:
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"


@app.get("/", response_model=APIMessage, tags=["Health"])
def health_check(response: Response) -> APIMessage:
    add_custom_headers(response)
    return APIMessage(message="device_systems API funcionando correctamente")


app.include_router(user_router)

