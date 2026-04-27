from redis.asyncio import Redis
from app.config import db_settings

_conn = Redis(host=db_settings.REDIS_HOST, port=db_settings.REDIS_PORT, db=0)

async def add_jti_to_blacklist(jti: str):
    await _conn.set(jti, 'blacklisted')

async def is_jti_blacklisted(jti: str) -> bool:
    return await _conn.exists(jti)