import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import logging
from typing import Optional
from contextvars import ContextVar
from loguru import logger
from opentelemetry import trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor
import os
# Context variables for request-scoped logging
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
trace_id_ctx: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)

LoggingInstrumentor().instrument()

class CustomLogger:
    def __init__(self):
        self._logger = logger

    def _get_context_data(self):
        """Get the current request context data"""
        extras = {}
        try:
            trace_id = trace_id_ctx.get()
            request_id = request_id_ctx.get()
            if trace_id:
                extras["trace_id"] = trace_id
            if request_id:
                extras["request_id"] = request_id
        except LookupError:
            pass
        return extras

    def _log(self, level: str, message: str, *args, **kwargs):
        """Internal method to handle logging with proper formatting"""
        extras = self._get_context_data()
        
        # If there are format args, format the message
        if args:
            message = message % args
        
        # Handle dictionary values in kwargs by converting them to strings
        for key, value in kwargs.items():
            if isinstance(value, (dict, list)):
                kwargs[key] = json.dumps(value)
        
        # Add any additional kwargs to extras
        extras.update(kwargs)
        
        # Use loguru's logging with extras
        self._logger.opt(depth=1).log(level, message, **extras)

    def info(self, message: str, *args, **kwargs):
        self._log("INFO", message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self._log("ERROR", message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self._log("WARNING", message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        self._log("DEBUG", message, *args, **kwargs)

class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect it to Loguru"""
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelname
        logger.opt(depth=6, exception=record.exc_info).log(
            level, record.getMessage()
        )

def logger_setup():
    """Configure Loguru for file logging with rotation & retention"""
    logger.remove()
    log_format = "{message}"
    is_aws_lambda = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    is_ecs_fargate = os.environ.get("AWS_EXECUTION_ENV") or os.environ.get("ECS_CONTAINER_METADATA_URI_V4")
    if is_aws_lambda or is_ecs_fargate:
        # Log to stdout for AWS Lambda (CloudWatch logs)
        logger.add(sys.stdout, format=log_format, serialize=True, level="INFO")
        service_type = "AWS Lambda" if is_aws_lambda else "ECS/Fargate"
        print(f"Logging to {service_type}")
    else:
        # Log to a file for local execution
        logger.add("logs/app.log", format=log_format, serialize=True, level="INFO", rotation="1 day", retention="7 days", compression="zip")

logger_setup()
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

# Create a global logger instance
app_logger = CustomLogger()

async def get_logger():
    """FastAPI dependency for getting the logger"""
    return app_logger

def log_message(message, **kwargs):
    """
    Logs messages with OpenTelemetry trace info attached.

    Example Usage:
        log_message("User logged in", user_id=123)
    """
    span = trace.get_current_span()

    if span.get_span_context().trace_id:
        kwargs["trace_id"] = format(span.get_span_context().trace_id, "x")

    logger.info(message, **kwargs)
