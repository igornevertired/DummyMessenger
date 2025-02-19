import os
import asyncio
import asyncpg
from typing import Annotated
from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import desc, select
from uvicorn import Server, Config
from db.models import Base, Message
from dotenv import load_dotenv
from db.schemas import UserMessageCreate, UserMessageFull, MessageStatistics
from logger import logger

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}'
logger.info(f"Connecting to database: {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL,
                             echo=True,
                             pool_size=10,
                             pool_pre_ping=True,
                             max_overflow=0,
                             future=True
                             )
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def create_database():
    """
    Создает базу данных, если она не существует

    """

    conn = await asyncpg.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=5432, database='postgres')
    db_exists = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    if not db_exists:
        await conn.execute(f'CREATE DATABASE "{DB_NAME}" OWNER {DB_USER}')
        logger.info(f"База данных {DB_NAME} создана.")
    else:
        logger.info(f"База данных {DB_NAME} уже существует.")

    await conn.close()

    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class MessageRepository:
    """
    Репозиторий для работы с сообщениями

    """

    @classmethod
    async def add_message_get_last_ten(cls, user_post: UserMessageCreate):
        async with AsyncSessionLocal() as session:
            query = select(Message).filter(Message.name == user_post.name)
            user_message_count = len((await session.execute(query)).scalars().all()) + 1

            new_message = Message(name=user_post.name, text=user_post.text, count=user_message_count)
            session.add(new_message)
            await session.commit()
            await session.refresh(new_message)

            query = (
                select(Message)
                .filter(Message.name == new_message.name)
                .order_by(desc(Message.id))
                .limit(10)
            )
            result = await session.execute(query)
            last_ten_messages = result.scalars().all()

            return {
                'messages': [UserMessageFull.model_validate(msg) for msg in last_ten_messages],
                'count_messages': MessageStatistics.model_validate(last_ten_messages[0])
            }


message_route = APIRouter()


@message_route.post('/add_message')
async def add_message(user_post: Annotated[UserMessageCreate, Depends()]):
    return await MessageRepository.add_message_get_last_ten(user_post)


def create_app():
    """
    Создание FastAPI приложения

    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            await create_database()

            async with engine.begin() as conn:
                try:
                    await conn.run_sync(Base.metadata.create_all)
                    logger.info("Схема базы данных обновлена.")
                except SQLAlchemyError as e:
                    logger.error(f"Ошибка при создании таблиц: {e}")

        except Exception as e:
            logger.error(f"❌ Ошибка при создании БД: {e}")
        yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(message_route)
    return app


app = create_app()


class MyServer(Server):
    async def run(self, sockets=None):
        self.config.setup_event_loop()
        return await self.serve(sockets=sockets)


async def run():
    """
    Запуск нескольких серверов

    """

    app_ports = [5001, 5002]
    tasks = []
    for port in app_ports:
        config = Config("Server:app", host="127.0.0.1", port=port, reload=True)
        server = MyServer(config=config)
        tasks.append(server.run())
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(run())
