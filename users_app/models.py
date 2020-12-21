from datetime import datetime
import os
import bcrypt
import jwt

from database import Database
from settings import MIGRATIONS_DIR
from settings import init_config


async def migrate() -> None:
    async with Database.pool.acquire() as connection:
        for migration in os.listdir(MIGRATIONS_DIR)[::-1]:
            migration_path = os.path.join(MIGRATIONS_DIR, migration)
            with open(migration_path) as f:
                await connection.execute(f.read())


class User:
    def __init__(self, id: int, email: str, password: str):
        self.id = id
        self.email = email
        self.password = password
        super().__init__()

    @classmethod
    async def create(cls, email: str,
                     password: str,
                     created_at: datetime = datetime.now()
                     ) -> None:
        hashed_password = await cls.hash_password(password)
        async with Database.pool.acquire() as connection:
            await connection.execute('''
            INSERT INTO public.users (email, password, created_at)
            VALUES($1, $2, $3)''', email, hashed_password, created_at)

    @classmethod
    async def check_password(cls, email: str, password: str) -> bool:
        async with Database.pool.acquire() as connection:
            db_password = await connection.fetchval('''
            SELECT password FROM public.users WHERE email = $1''', email)

        return await cls.hash_password(password) == db_password

    @classmethod
    async def hash_password(cls, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'),
                             init_config().get('SALT')
                             .encode('utf-8')).decode('utf-8')

    @classmethod
    async def get(cls, email: str, password: str):
        if await cls.check_password(email, password):
            async with Database.pool.acquire() as connection:
                user = await connection.fetchrow('''
                SELECT id, email, password
                FROM public.users WHERE email = $1''', email)
                return User(**user)
        else:
            raise PermissionError


class Token:
    def __init__(self, user: str, key: str):
        self.user = user
        self.key = key
        super().__init__()

    @classmethod
    async def create(cls, user: User) -> str:
        return jwt.encode({
            'id': user.id,
            'email': user.email,
            'time': datetime.now().timestamp()
        }, init_config().get('JWT_SECRET_KEY')).decode('utf-8')
