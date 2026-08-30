"""
Configuration for the terminal client (cli.py / views package).

This module intentionally has zero Django dependencies, the terminal client
is a plain HTTP consumer of the backend, just like any external client
would be, and never touches the database or the ORM directly.
"""

import os

API_BASE_URL = os.getenv("BARBERSHOP_API_URL", "http://localhost:8000/api/v1")
REQUEST_TIMEOUT = int(os.getenv("BARBERSHOP_TIMEOUT", "10"))
DEV_MODE_DEFAULT = os.getenv("BARBERSHOP_DEV_MODE", "false").lower() == "true"
