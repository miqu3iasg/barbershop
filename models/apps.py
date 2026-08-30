from django.apps import AppConfig


class ModelsConfig(AppConfig):
    """
    The single Django app of this project. It intentionally owns every
    domain entity (Client, Barber, Service, Appointment...), each in its
    own file under this package, instead of splitting the domain into one
    Django app per entity — that indirection added no value for a project
    this size and made the codebase harder to navigate.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "models"
    verbose_name = "Domain Models"
