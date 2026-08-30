"""Django admin registrations for every domain model."""

from django.contrib import admin

from .appointment import Appointment
from .appointment_item import AppointmentItem
from .barber import Barber
from .client import Client
from .service import Service
from .working_hours import WorkingHours


class AppointmentItemInline(admin.TabularInline):
    model = AppointmentItem
    extra = 0


class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "document_number", "phone", "email", "is_active"]
    search_fields = ["name", "document_number", "email"]
    list_filter = ["is_active"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "duration_minutes", "price", "is_active"]
    list_filter = ["is_active"]


@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "phone", "email", "is_active"]
    list_filter = ["is_active"]
    filter_horizontal = ["specialties"]
    inlines = [WorkingHoursInline]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["id", "client", "barber", "start_at", "end_at", "status"]
    list_filter = ["status", "barber"]
    inlines = [AppointmentItemInline]
