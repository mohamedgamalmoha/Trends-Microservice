import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_db(app):
    from shared_utils.db.session import get_db
    
    # Get a database session
    db_gen = get_db()
    session = await anext(db_gen)
    
    # Verify the session is an instance of AsyncSession
    assert isinstance(session, AsyncSession)
    
    # Verify the session can execute a simple query
    result = await session.execute(text("SELECT 1"))
    value = result.scalar_one()
    assert value == 1
