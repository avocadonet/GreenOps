import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from shared.db.user import UserModel


async def create_superuser() -> None:
    database_url = os.environ["DATABASE_URL"]
    email = os.environ.get("SUPERUSER_EMAIL", "admin@greenops.io")
    password = os.environ["SUPERUSER_PASSWORD"]
    fullname = os.environ.get("SUPERUSER_FULLNAME", "Super Admin")

    engine = create_async_engine(database_url)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_maker() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.role == "SUPER_USER")
        )
        if result.scalar_one_or_none() is not None:
            print("Superuser already exists, skipping.")
            await engine.dispose()
            return

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        model = UserModel(
            email=email,
            fullname=fullname,
            is_active=True,
            hashed_password=hashed.decode("utf-8"),
            salt="",
            role="SUPER_USER",
        )
        session.add(model)
        await session.commit()
        print(f"Superuser created: {email}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_superuser())
