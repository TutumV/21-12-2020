import os

BASE_DIR = os.getcwd()
MIGRATIONS_DIR = os.path.join(BASE_DIR, 'migrations')


def init_config() -> dict:
    config = dict(
        HOST=os.environ.get('HOST', '127.0.0.1'),
        PORT=os.environ.get('PORT', '5000'),
        DB_HOST=os.environ.get('DB_HOST', 'localhost'),
        DB_PORT=os.environ.get('DB_PORT', '5432'),
        DB_USER=os.environ.get('DB_USER', 'postgres'),
        DB_PASSWORD=os.environ.get('DB_PASSWORD', 'password'),
        DATABASE=os.environ.get('DATABASE', 'postgres'),
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwtkey'),
        JWT_ALGORITHM=os.environ.get('JWT_ALGORITHM', 'HS256'),
        SALT=os.environ.get('SALT', '$2b$08$N5Ki85CXepNsxzmR1/9WWe')
    )
    return config
