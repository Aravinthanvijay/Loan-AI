"""
Standardized API response format.
Ensures consistent JSON structure for all API responses.
"""

from typing import Any, Optional, Dict, List
from datetime import datetime
from bson import ObjectId
import json


def serialize_doc(doc: Any) -> Any:
    """Convert MongoDB documents to JSON-serializable format."""
    if doc is None:
        return None
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    else:
        return doc


class APIResponse:
    """Builder for standardized API responses."""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "message": message,
            "data": serialize_doc(data),
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def error(
        message: str,
        errors: Any = None,
        status_code: int = 400,
    ) -> Dict[str, Any]:
        return {
            "success": False,
            "message": message,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def paginated(
        data: list,
        total: int,
        page: int,
        per_page: int,
        message: str = "Success",
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "message": message,
            "data": serialize_doc(data),
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }