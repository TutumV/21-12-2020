import logging
import asyncpg

log = logging.getLogger(__name__)


class Database:

    pool = None

    @classmethod
    async def connect(cls, dsn: str) -> None:
        try:
            cls.pool = await asyncpg.create_pool(dsn, command_timeout=60)
        except Exception as error:
            log.info(error)
