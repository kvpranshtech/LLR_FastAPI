# check_tables.py
from sqlalchemy import create_engine, inspect

# Use the same database URL as your app
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


def check_database():
    inspector = inspect(engine)

    print("=== Database Structure ===")

    # Check all schemas
    schemas = inspector.get_schema_names()
    print(f"Available schemas: {schemas}")

    # Check tables in each schema
    for schema in schemas:
        print(f"\n--- Schema: {schema} ---")
        tables = inspector.get_table_names(schema=schema)
        print(f"Tables: {tables}")

    # Check for any table containing keywords
    print(f"\n--- Searching for related tables ---")
    all_tables = []
    for schema in schemas:
        tables = inspector.get_table_names(schema=schema)
        all_tables.extend([f"{schema}.{table}" for table in tables])

    email_tables = [t for t in all_tables if 'email' in t.lower()]
    user_tables = [t for t in all_tables if 'user' in t.lower()]
    auth_tables = [t for t in all_tables if 'auth' in t.lower()]

    print(f"Tables with 'email': {email_tables}")
    print(f"Tables with 'user': {user_tables}")
    print(f"Tables with 'auth': {auth_tables}")


if __name__ == "__main__":
    check_database()