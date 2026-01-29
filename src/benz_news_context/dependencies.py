"""FastAPI dependency injection functions."""
from benz_common.db import DatabaseAdapter, get_database_adapter


def get_db_adapter() -> DatabaseAdapter:
    """FastAPI dependency for database adapter."""
    return get_database_adapter()
