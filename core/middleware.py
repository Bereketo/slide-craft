from datetime import datetime, timezone
import time
import uuid
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from opentelemetry import trace
from core.logger_setup import app_logger
from core.constants import API_REQUEST_PROCESSED
from typing import Optional
from contextvars import ContextVar

tracer = trace.get_tracer(__name__)
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
trace_id_ctx: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)

def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization"],
    )

def add_logging_middleware(app):
    """Middleware to log incoming requests efficiently"""
    def format_timestamp(timestamp):
        return datetime.fromtimestamp(timestamp, timezone.utc).isoformat(timespec="milliseconds") + "Z"

    @app.middleware("http")
    async def log_requests(request: Request, call_next):        
        start_time = time.time()

        # Get or generate trace_id and request_id
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Set the context variables
        trace_id_ctx.set(trace_id)
        request_id_ctx.set(request_id)

        # Log the incoming request with context
        app_logger.info(
            "Incoming request received",
            client_ip=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown"),
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            request_headers=dict(request.headers),
        )

        response: Response = await call_next(request)
        # Adding CSP
        # response.headers["Content-Security-Policy"] = (
        #     "default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none';"
        # )
        # # Adding X-content-type-options
        # response.headers["X-Content-Type-Options"] = "nosniff"
        # # Adding STS 
        # response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        # Remove unwanted headers
        if "server" in response.headers:
            del response.headers["server"]
        end_time = time.time()
        duration = round((end_time - start_time) * 1000, 2)

        # Log the response
        log_kwargs = {
            "start_time": format_timestamp(start_time),
            "end_time": format_timestamp(end_time),
            "duration_ms": duration,
            "status_code": response.status_code,
            "response_headers": dict(response.headers)
        }

        if response.status_code >= 500:
            app_logger.error(API_REQUEST_PROCESSED, **log_kwargs)
        elif response.status_code >= 400:
            app_logger.warning(API_REQUEST_PROCESSED, **log_kwargs)
        else:
            app_logger.info(API_REQUEST_PROCESSED, **log_kwargs)

        # Add trace and request IDs to response headers
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Request-ID"] = request_id

        return response
