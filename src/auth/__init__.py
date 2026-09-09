"""
Autogram Authentication & Licensing Package.
"""
from src.auth.licensing import (
    verify_license,
    generate_license,
    is_owner_key,
    get_active_license_status
)

__all__ = [
    "verify_license",
    "generate_license",
    "is_owner_key",
    "get_active_license_status"
]
