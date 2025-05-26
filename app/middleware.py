from fastapi import Request, Response
from app.loggers import logger

async def log_requests(request: Request, call_next) -> Response:
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Completed response: {response.status_code}")
    return response