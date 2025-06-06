import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

# Global pool variable
pool: asyncpg.Pool = None

async def fetch_tokens(user_uuid: str, external_client: str):
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(dsn=DB_URL, min_size=1, max_size=10)
    async with pool.acquire() as conn:
        query = """
            SELECT access_token FROM external_tokens
            WHERE user_uuid = $1 AND external_client = $2
        """
        rows = await conn.fetch(query, user_uuid, external_client)
        return rows
