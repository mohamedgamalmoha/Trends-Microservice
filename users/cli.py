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
        $ python cli.py createdb

testdb
    Tests the database connection using the configured credentials.
    This command attempts to establish a connection to the database and
    verifies that the credentials are valid. It provides feedback on success
    or failure.

    Example:
        $ python cli.py testdb

createadminuser
    Creates an administrator user with full system privileges.
    This command validates input credentials against security requirements
    before creating the user. All fields undergo Pydantic validation to
    ensure data integrity and security standards.

    Example:
        $ python cli.py createadminuser --username admin --email admin@example.com --password SecurePass123!

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

import asyncclick as click
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, ValidationError
from shared_utils.db.session import engine, init_db, get_db

from app.schemas.user import _AdminUserCreate
from app.repositories.user import get_user_repository


# Type variables for better type hinting
CCT = TypeVar('CCT')  # Click Callback Type
ClickCallback = Callable[[click.Context, click.Parameter, CCT], CCT]


def validate_pydantic_field[T: BaseModel](model: Type[T], field_name: str) -> ClickCallback:
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

    def callback[T](ctx: click.Context, param: click.Parameter, value: T) -> T:
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
async def createadminuser(email: str, username: str, password: str) -> None:
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

        with get_db() as db:
            user_repository = get_user_repository(db=db)
            user_db = await user_repository.create_admin(
                ** user_data.model_dump()
            )

        click.echo(click.style(f"✓ Administrator user created successfully: {user_db}", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Error creating administrator user: {e}", fg="red"), err=True)
        raise click.Abort()


@cli.command()
async def initdb() -> None:
    """
    Create all database tables.

    This command initializes the database by creating all tables defined
    in SQLAlchemy models. It should be run during initial application setup
    or after a database reset.

    The command uses the configured database engine and creates tables
    for all models that inherit from the Base class.
    """
    try:
        await init_db()
        click.echo(click.style("✓ Database tables created successfully", fg="green"))
    except SQLAlchemyError as e:
        click.echo(click.style(f"✗ Database creation failed: {e}", fg="red"), err=True)
        raise click.Abort()


@cli.command()
async def testdb():
    """
    Test database connection.

    This command attempts to establish a connection to the database
    using the provided credentials. It verifies that the database is
    accessible and that the credentials are valid.

    The command works as follows:
        - If the connection is successful, a confirmation message is displayed.
        - If the connection fails, an error message is displayed with details
    """
    try:
        async with engine.connect():
            await engine.execute("SELECT 1")
            click.echo(click.style("✓ Database connection successful!", fg="green", bold=True))
    except SQLAlchemyError as e:
        click.echo(click.style(f"✗ Database connection failed: {str(e)}", fg="red", bold=True), err=True)


if __name__ == '__main__':
    cli()
