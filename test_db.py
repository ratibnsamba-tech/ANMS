from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import Config


def test_database_connection():
    uri = Config.SQLALCHEMY_DATABASE_URI
    print('Testing database connection for:', uri)
    engine = create_engine(uri)

    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            value = result.scalar()
            if value == 1:
                print('Success: Database connection is working.')
                return 0
            print('Warning: Connected, but query returned unexpected value:', value)
            return 1
    except SQLAlchemyError as exc:
        print('Database connection failed:')
        print(exc)
        return 2


if __name__ == '__main__':
    raise SystemExit(test_database_connection())
