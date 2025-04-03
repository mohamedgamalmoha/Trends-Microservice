import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_database_connection(session_local):
    async with session_local() as session:
        
        assert isinstance(session, AsyncSession)
        
        result = await session.execute(
            select(1)
        )
        value = result.scalar_one()
        
        assert value == 1
