import os

from sqlalchemy import create_engine, text


DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://tester:tester@localhost:5432/testlab",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def get_device_from_db(device_id: str) -> dict | None:
    with engine.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT id, name, status, created_at, processing_count
                FROM devices
                WHERE id = :device_id
                """
            ),
            {"device_id": device_id},
        ).mappings().first()

        return dict(row) if row else None