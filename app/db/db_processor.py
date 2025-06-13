import os
import asyncpg
from dotenv import load_dotenv

from app.dto.chunk_db_record import ChunkDbRecord

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
            SELECT access_token, refresh_token, expires_at, metadata FROM external_tokens
            WHERE user_uuid = $1 AND external_client = $2
        """
        rows = await conn.fetch(query, user_uuid, external_client)
        if not rows:
            return None

        final_result = [{
            "access_token": row["access_token"],
            "refresh_token": row["refresh_token"],
            "expires_at": row["expires_at"],
            "metadata": row["metadata"]
        } for row in rows]

        return final_result


async def update_token_by_user_id_and_external_client(user_uuid: str, token_data: dict, external_client: str):
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(dsn=DB_URL, min_size=1, max_size=10)
    async with pool.acquire() as conn:
        query = """
            UPDATE external_tokens
            SET access_token = $1,
                refresh_token = $2,
                expires_at = $3,
                updated_at = NOW()
            WHERE user_uuid = $4 AND external_client = $5
        """
        await conn.execute(query, token_data["access_token"], token_data["refresh_token"], token_data["expires_at"], user_uuid, external_client)

async def fetch_chunks(chunk_ids: list[str]) -> list[ChunkDbRecord]:
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(dsn=DB_URL, min_size=1, max_size=10)
    async with pool.acquire() as conn:
        query = """
            select chunk_content from chunked_data
            where uuid = ANY($1)
        """
        rows = await conn.fetch(query, chunk_ids)
        return [ChunkDbRecord(chunk_content=row['chunk_content']) for row in rows]