import logging
import time
from uuid import uuid4

from fastapi import Request

logger = logging.getLogger("device_systems.requests")
logger.setLevel(logging.INFO)


async def request_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0.0"
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request method=%s path=%s status_code=%s request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        request_id,
    )
    return response
