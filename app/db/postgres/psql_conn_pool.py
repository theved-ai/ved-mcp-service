import asyncpg
from typing import Optional

_pg_pool: Optional[asyncpg.pool.Pool] = None

async def init_pg_pool(dburl: str):
    global _pg_pool
    if _pg_pool is None:
        _pg_pool = await asyncpg.create_pool(dsn=dburl, min_size=2, max_size=10)

def get_pg_pool() -> asyncpg.pool.Pool:
    if _pg_pool is None:
        raise RuntimeError("PostgreSQL pool not initialized.")
    return _pg_pool

async def close_pg_pool():
    global _pg_pool
    if _pg_pool is not None:
        await _pg_pool.close()
