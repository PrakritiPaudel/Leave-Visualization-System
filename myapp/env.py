import os
from dotenv import load_dotenv
from logging.config import fileConfig

from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import engine_from_config, pool
from alembic import context


# Load environment variables from .env file
load_dotenv()

# Get the database URL from the environment variable
database_url = os.getenv("DATABASE_URL")

# Ensure the database_url is a string
if not isinstance(database_url, str):
    raise ValueError("DATABASE_URL must be a valid string. Check your .env file.")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
script = ScriptDirectory.from_config(config)

# Update the sqlalchemy.url in Alembic config with the environment variable
config.set_main_option("sqlalchemy.url", str(database_url))  # Ensure the URL is a string

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

target_metadata = None  # Replace with your model's metadata if using autogenerate

# Set the metadata object

# start to run migrations in order
# def run_migrations_in_custom_order():
#     """Run migrations in a custom order."""
#     # Define the order of revision IDs manually
#     ordered_revisions = [
#         "27b875bfea0b",  # revision id to create dbo schema
#         "23fdc1d88362",  # revision id to create department table
#         "99766294c058",  # Replace with your actual revision ID
#         "eb012e3ab17e",
#         "b774344d4d78",
#         "f443bb587438",
#         "b774344d4d78",
#         "dc8a7d29cf5a"
#         # Add more revisions as needed
#     ]
    
#     # Fetch all available revisions
#     available_revisions = {rev.revision: rev for rev in script.walk_revisions()}
    
#     # Apply migrations in the specified order
#     for rev_id in ordered_revisions:
#         if rev_id in available_revisions:
#             version = available_revisions[rev_id]
#             if context.is_offline_mode():
#                 context.run_migrations_offline()
#             else:
#                 context.run_migrations_online()
#         else:
#             print(f"Revision {rev_id} not found in the available migrations.")
# # end to run migrations in order

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
