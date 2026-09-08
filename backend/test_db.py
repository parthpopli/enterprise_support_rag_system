from sqlalchemy import text
from app.database.connection import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        print("Database connected successfully!")
        print(result.scalar())

except Exception as e:
    print("Database connection failed:")
    print(type(e).__name__)
    print(e)