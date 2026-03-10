import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost:5433/scopus_sirius"


async def main():
    engine = create_async_engine(DATABASE_URL)

    async with engine.connect() as conn:

        # 1. Проверка подключения
        result = await conn.execute(text("SELECT 1"))
        print("DB работает:", result.scalar())

        # 2. Получить список таблиц
        tables = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
        """))

        tables = tables.scalars().all()
        print("\nТаблицы:", tables)

        # 3. Проверить данные в таблицах
        for table in tables:
            count = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = count.scalar()

            print(f"\nТаблица: {table}")
            print(f"Количество строк: {count}")

            rows = await conn.execute(text(f"SELECT * FROM {table} LIMIT 3"))

            for row in rows:
                print(dict(row._mapping))

    await engine.dispose()


asyncio.run(main())