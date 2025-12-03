import tempfile
from fastapi import FastAPI
from fastapi.responses import JSONResponse,FileResponse
from pathlib import Path
import sys
import os

from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from core.logger_setup import app_logger as logger
from core.constants import VALIDATED_FAILED
from api.v1.ppt_generator import router as ppt_router
from core.middleware import add_cors_middleware, add_logging_middleware
import uvicorn
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger.info("Starting FastAPI Secure API")
app = FastAPI(
    title="FastAPI Secure API",
    description="PPT Api",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "JSON-PPT",
            "description": "Endpoints for PPT",
        }
    ]
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [
                {"OAuth2PasswordBearer": []}
            ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


FastAPIInstrumentor.instrument_app(app)

add_cors_middleware(app)
add_logging_middleware(app)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the PPT Generator API!"}

# Example endpoint: health check
@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})

app.include_router(ppt_router, prefix="/api/v1",tags=['PPT'])
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(exc)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    error_response = {
        "status": "error",
        "message": "An error occurred",
        "errors": [],
    }

    if isinstance(exc.detail, dict) and "errors" in exc.detail:
        logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
        error_response.update(
            {
                "message": exc.detail.get("message", VALIDATED_FAILED),
                "errors": exc.detail["errors"],
            }
        )
    elif isinstance(exc.detail, str):
        if exc.status_code == 400:
            logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
            error_response["message"] = VALIDATED_FAILED
            error_response["errors"] = [{"field": "general", "error": exc.detail}]
        elif exc.status_code == 401:
            logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
            error_response["message"] = "Unauthorized"
            error_response["errors"] = [
                {
                    "field": "Authorization",
                    "error": "JWT token is missing, invalid or expired.",
                }
            ]
        elif exc.status_code == 403:
            logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
            error = exc.detail if exc.detail else "You do not have permission to perform this action."
            error_response["message"] = "Forbidden"
            error_response["errors"] = [
                {
                    "field": "role",
                    "error": error,
                }
            ]
        elif exc.status_code == 409:
            logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
            error_response["message"] = "Conflict"
            error_response["errors"] = [{"field": "email", "error": exc.detail}]
        else:
            logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
            error_response["message"] = exc.detail

    logger.error(f"HTTPException: {exc.status_code} - {error_response}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = [
        {
            "field": ".".join(map(str, error["loc"][1:])),
            "error": f"{' '.join(map(str, error['loc'][1:]))} {error['msg']}",
        }
        for error in errors
    ]

    logger.error(f"RequestValidationError: {formatted_errors}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": VALIDATED_FAILED,
            "errors": formatted_errors,
        },
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5252)
