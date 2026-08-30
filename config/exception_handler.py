"""
Custom DRF exception handler.

Translates two kinds of failures into a consistent JSON error shape:

- DomainError: business-rule violations raised by the model/service layers
  (e.g. scheduling conflicts).
- Django's own ValidationError: raised by Model.full_clean() when a field
  fails validation (e.g. an invalid CPF) or a uniqueness constraint fails.

Everything else falls back to DRF's default handler, just wrapped in the
same {"detail": ...} envelope so API consumers only need one error format.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from exceptions.domain_exceptions import DomainError


def custom_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return Response({"detail": str(exc)}, status=400)

    if isinstance(exc, DjangoValidationError):
        detail = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
        return Response({"detail": detail}, status=400)

    response = drf_exception_handler(exc, context)
    if response is not None:
        response.data = {"detail": response.data}

    return response
