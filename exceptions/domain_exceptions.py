"""
Business-rule exceptions raised by the domain layer (models/ and services/).

These are framework-agnostic: they know nothing about HTTP status codes.
config/exception_handler.py is responsible for translating them into HTTP
responses, and the terminal client has its own, separate exception
hierarchy (see exceptions/api_exceptions.py) for errors that come back
over the wire.
"""


class DomainError(Exception):
    """Base class for every business-rule violation in the barbershop domain."""


class EmptyServiceListError(DomainError):
    """Raised when trying to schedule an appointment without any service selected."""


class PastSchedulingError(DomainError):
    """Raised when trying to schedule an appointment in the past."""


class BarberNotAvailableError(DomainError):
    """Raised when a barber does not work at all on the requested day of the week."""


class OutsideWorkingHoursError(DomainError):
    """Raised when the requested time window falls outside the barber's shift."""


class SchedulingConflictError(DomainError):
    """Raised when the barber already has a conflicting appointment at that time."""


class InvalidStatusTransitionError(DomainError):
    """Raised when an appointment status change violates the allowed state machine."""


class ResourceNotFoundError(DomainError):
    """Raised when a referenced entity (client, barber, service...) does not exist."""
