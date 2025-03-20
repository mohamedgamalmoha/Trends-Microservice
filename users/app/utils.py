from typing import Any, Dict

from sqlalchemy.orm import DeclarativeBase


def db_model_to_dict(instance: DeclarativeBase) -> Dict[str, Any]:
    """
    Extract all fields and their values from a SQLAlchemy model instance.

    Args:
        - instance: A SQLAlchemy model instance

    Returns:
        - A dictionary mapping field names to their values
    """
    return {
        column.name: getattr(instance, column.name) for column in instance.__table__.columns
    }
