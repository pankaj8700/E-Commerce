from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


async def internal_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


def parse_integrity_error(e: IntegrityError) -> str:
    """Convert SQLAlchemy IntegrityError into a human-readable message."""
    msg = str(e.orig).lower()

    if "unique" in msg or "duplicate" in msg:
        # Try to extract the field name from the error message
        # SQLite format: "UNIQUE constraint failed: table.column"
        if "unique constraint failed:" in msg:
            field = msg.split("unique constraint failed:")[-1].strip()
            # e.g. "product.name" -> "name"
            field = field.split(".")[-1].strip()
            return f"A record with this {field} already exists."
        return "A record with these details already exists."

    if "not null" in msg:
        if "not null constraint failed:" in msg:
            field = msg.split("not null constraint failed:")[-1].strip().split(".")[-1].strip()
            return f"'{field}' field is required and cannot be empty."
        return "A required field is missing."

    if "foreign key" in msg:
        return "Related record does not exist. Please check the provided ID."

    return "A database constraint was violated. Please check your input."
