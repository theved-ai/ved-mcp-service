from app.db.postgres.psql_conn_pool import get_pg_pool
import asyncpg

async def fetch_one(query: str, *args) -> asyncpg.Record:
    pool = get_pg_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def fetch_all(query: str, *args) -> list[asyncpg.Record]:
    pool = get_pg_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def execute(query: str, *args) -> str:
    pool = get_pg_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)
