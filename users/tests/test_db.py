import os

import pytest


@pytest.mark.asyncio
async def test_database_connection(get_db, app):
    db_url = os.getenv("DATABASE_URL")
    assert db_url.startswith("postgresql+asyncpg://")

    # Run a simple query to verify connection
    result = await get_db.execute("SELECT 1")
    assert result.scalar_one() == 1
