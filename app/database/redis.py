from uuid import UUID

from redis.asyncio import Redis
from app.config import db_settings

_blacklisted_tokens = Redis(
    host=db_settings.REDIS_HOST, port=db_settings.REDIS_PORT, db=0
)

_verification_codes = Redis(
    host=db_settings.REDIS_HOST,
    port=db_settings.REDIS_PORT,
    db=1,
    decode_responses=True,
)


async def add_jti_to_blacklist(jti: str):
    await _blacklisted_tokens.set(jti, "blacklisted")


async def is_jti_blacklisted(jti: str) -> bool:
    return await _blacklisted_tokens.exists(jti)


async def add_verification_code(id: UUID, code: str):
    await _verification_codes.set(str(id), code)


async def get_verification_code(id: UUID) -> str:
    return await _verification_codes.get(str(id))
