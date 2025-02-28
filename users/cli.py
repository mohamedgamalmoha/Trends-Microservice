#!/usr/bin/env python3
"""
Database Administration CLI Tool
===============================

A comprehensive command-line interface for performing database administration tasks in a
Python application. This tool provides utilities for database initialization, connection
testing, and user management.

Commands:
---------

createdb
    Creates all database tables defined in SQLAlchemy models.
    This command initializes the database schema based on model definitions
    inherited from the Base class. It should be run during initial setup or
    after database resets.

    Example:
        $ python db_admin.py createdb

testdb
    Tests database connection using provided credentials.
    This command attempts to establish a connection to verify accessibility
    and credential validity. It supports multiple database engines and
    provides detailed error information if connection fails.

    Example:
        $ python db_admin.py testdb --name mydb --user dbuser --password secret123
        $ python db_admin.py testdb --name analytics --user report_user --password dbpass --host db.example.com --port 5433 --engine postgresql

createadminuser
    Creates an administrator user with full system privileges.
    This command validates input credentials against security requirements
    before creating the user. All fields undergo Pydantic validation to
    ensure data integrity and security standards.

    Example:
        $ python db_admin.py createadminuser --username admin --email admin@example.com --password SecurePass123!

Usage Notes:
-----------
    - Commands can be chained to perform multiple operations
    - All operations provide colored output to indicate success/failure
    - Use the --help option with any command for detailed parameter information
    - Error messages include specific details to aid in troubleshooting

Environment Configuration:
-------------------------
The tool uses database connection parameters from the app's environment configuration
by default. These can be overridden using command-line arguments.
"""
from typing import Any, Callable, Type, TypeVar

import click
from pydantic import BaseModel, ValidationError
from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import SQLAlchemyError

from app.db.base import Base
from app.db.session import engine
from app.schemas.user import _AdminUserCreate
from app.repositories.user import _create_admin_user


# Type variables for better type hinting
T = TypeVar('T', bound=BaseModel)
ClickCallback = Callable[[click.Context, click.Parameter, Any], Any]


def validate_pydantic_field(model: Type[BaseModel], field_name: str) -> ClickCallback:
    """
    Create a Click callback to validate a field using Pydantic validation.

    This function returns a callback that validates input parameters against
    Pydantic model field definitions, providing consistent validation across
    the CLI interface.

    Args:
        - model: The Pydantic model class containing the field
        - field_name: The name of the field to validate

    Returns:
        - A Click callback function that validates the field

    Raises:
        - click.BadParameter: If validation fails
    """

    def callback(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
        try:
            # Create an empty model instance and validate the field assignment
            model.__pydantic_validator__.validate_assignment(
                model.model_construct(),
                field_name,
                value
            )
            return value
        except ValidationError as e:
            raise click.BadParameter(f"Invalid {field_name}: {e}")
    return callback


def test_db_connection(database_url: str) -> bool:
    """
    Test a database connection with the given URL.

    This function attempts to establish a connection to a database and
    reports the result.

    Args:
        - database_url: SQLAlchemy-compatible database connection string

    Returns:
        - bool: True if connection successful, False otherwise
    """
    # Create a new engine instance for this specific connection test
    test_engine: Engine = create_engine(database_url)

    try:
        with test_engine.connect():
            click.echo(click.style("✓ Database connection successful!", fg="green", bold=True))
            return True
    except SQLAlchemyError as e:
        click.echo(click.style(f"✗ Database connection failed: {str(e)}", fg="red", bold=True), err=True)
        return False


@click.group()
def cli() -> None:
    """
    Database administration tools.

    This CLI provides utilities for database management including:
        - Creating database tables
        - Testing database connections
        - Managing administrative users

    Use the --help option with any command for detailed usage information.
    """
    ...


@cli.command()
@click.option(
    '--email',
    required=True,
    help='Admin user email address',
    callback=validate_pydantic_field(_AdminUserCreate, 'email')
)
@click.option(
    '--username',
    required=True,
    help='Admin user username',
    callback=validate_pydantic_field(_AdminUserCreate, 'username')
)
@click.option(
    '--password',
    required=True,
    help='Admin user password',
    callback=validate_pydantic_field(_AdminUserCreate, 'password')
)
def createadminuser(email: str, username: str, password: str) -> None:
    """
    Create an administrator user account.

    This command creates a new administrator user with full system access.
    The provided credentials are validated against security requirements
    before the user is created.

    All fields are required and must meet validation requirements:
        - Email must be a valid email format
        - Username must meet length and character requirements
        - Password must meet security requirements
    """
    click.echo(f"Creating administrator user '{username}' with email '{email}'...")

    try:
        # Create user data model and pass to repository layer
        user_data = _AdminUserCreate(email=email, username=username, password=password)
        user_db = _create_admin_user(user_data)

        click.echo(click.style(f"✓ Administrator user created successfully: {user_db}", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Error creating administrator user: {e}", fg="red"), err=True)
        raise click.Abort()


@cli.command()
def createdb() -> None:
    """
    Create all database tables.

    This command initializes the database by creating all tables defined
    in SQLAlchemy models. It should be run during initial application setup
    or after a database reset.

    The command uses the configured database engine and creates tables
    for all models that inherit from the Base class.
    """
    try:
        Base.metadata.create_all(bind=engine)
        click.echo(click.style("✓ Database tables created successfully", fg="green"))
    except SQLAlchemyError as e:
        click.echo(click.style(f"✗ Database creation failed: {e}", fg="red"), err=True)
        raise click.Abort()


@cli.command()
@click.option('--name', required=True, help='Database name')
@click.option('--user', required=True, help='Database username')
@click.option('--password', required=True, help='Database password')
@click.option('--host', default='localhost', show_default=True, help='Database host')
@click.option('--port', default='5432', show_default=True, help='Database port')
@click.option(
    '--engine',
    default='postgresql',
    show_default=True,
    type=click.Choice(['postgresql', 'mysql', 'sqlite'], case_sensitive=False),
    help='Database engine type'
)
def testdb(name: str, user: str, password: str, host: str, port: str, engine: str) -> None:
    """
    Test database connection.

    This command attempts to establish a connection to the specified database
    using the provided credentials and connection parameters.

    Use cases:
    • Verify database credentials before deployment
    • Check network connectivity to database servers
    • Validate database configuration
    • Troubleshoot connection issues

    The command will display a success message or detailed error information.
    """
    click.echo(f"Testing connection to {engine} database '{name}' on {host}:{port}...")

    # Construct the database URL
    database_url = f"{engine}://{user}:{password}@{host}:{port}/{name}"

    # Test the connection and exit with appropriate status code
    if not test_db_connection(database_url):
        raise click.Abort()


if __name__ == '__main__':
    cli()
