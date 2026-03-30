from datetime import datetime

from src.main.errors.types.domain_error import DomainError
from src.main.errors.types.server_error import ServerError
from src.main.errors.types.validation_error import ValidationError

from src.application.DTOs.http.HttpRequest import HttpRequest, HttpRequestSearch, HttpRequestValidationError
from src.application.DTOs.http.HttpResponse import HttpResponse, HttpResponseSearch, HttpResponseRetrieve, HttpResponseBase

from src.config.logger_config import setup_logger
logger = setup_logger(name="handle_errors")


def handle_errors(http_request: HttpRequest, error: Exception) -> HttpResponse:
    end_time = datetime.now(tz=http_request.created_in.tzinfo)
    took_ms = int((end_time - http_request.created_in).total_seconds() * 1000)

    if isinstance(http_request, HttpRequestValidationError) and isinstance(error, ValidationError):
        logger.error(f"handle_errors: {error.message.strip()}")
        return HttpResponseBase(id=http_request.id,
                                status_code=error.status_code,
                                created_in=http_request.created_in,
                                took_ms=took_ms,
                                body={
                                    "error": {
                                        "title": error.name,
                                        "detail": error.message,
                                        "validation_errors": error.body
                                    }
                                })

    if isinstance(error, DomainError) and isinstance(http_request, HttpRequestSearch):
        logger.error(f"handle_errors: {error.message.strip()}")
        return HttpResponseSearch(id=http_request.id,
                                  status_code=error.status_code,
                                  created_in=http_request.created_in,
                                  took_ms=took_ms,
                                  query=http_request.query,
                                  top_k=http_request.top_k,
                                  body={
                                      "error": {
                                          "title": error.name,
                                          "detail": error.message,
                                          "query_validation": error.body
                                      }
                                  })

    if isinstance(error, ServerError) and isinstance(http_request, HttpRequestSearch):
        logger.error(f"handle_errors: {error.message.strip()}")
        return HttpResponseSearch(id=http_request.id,
                                  status_code=500,
                                  created_in=http_request.created_in,
                                  took_ms=took_ms,
                                  query=http_request.query,
                                  top_k=http_request.top_k,
                                  body={
                                      "error": [{
                                          "title": "Server Error",
                                          "detail": "Interval Server Error"
                                      }]
                                  })

    if isinstance(error, ServerError) and isinstance(http_request, HttpResponseRetrieve):
        logger.error(f"handle_errors: {error.message.strip()}")
        return HttpResponseRetrieve(id=http_request.id,
                                    status_code=error.status_code,
                                    created_in=http_request.created_in,
                                    took_ms=took_ms,
                                    paragraph_numbers=http_request.paragraph_numbers,
                                    body={
                                        "error": [{
                                            "title": "Server Error",
                                            "detail": "Interval Server Error"
                                        }]
                                    })
    else:
        return HttpResponseBase(id=http_request.id,
                                status_code=500,
                                created_in=http_request.created_in,
                                took_ms=took_ms,
                                body={
                                    "error": [{
                                        "title": "Server Error",
                                        "detail": "Interval Server Error"
                                    }]
                                })
