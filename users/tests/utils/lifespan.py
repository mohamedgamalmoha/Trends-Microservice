
async def lifespan(app):
    from shared_utils.db.session import init_db, close_db, drop_db

    await init_db()
    
    yield

    await drop_db()
    await close_db()
