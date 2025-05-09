#!/usr/bin/env python3
"""
Generate a `.env` file from Pydantic `BaseSettings` classes in a given Python module.

This script inspects a specified module within a service, detects all classes that inherit 
from `pydantic_settings.BaseSettings`, extracts their fields and default values, and writes 
them into a `.env` file. This is useful for bootstrapping environment configuration files 
based on your Pydantic settings definitions.

Main Steps:
    - Parses CLI arguments to identify the target service, module, and output file path.
    - Dynamically imports the specified module.
    - Finds all subclasses of `BaseSettings` within that module.
    - Extracts environment variable names and their default values.
    - Generates a `.env` file containing those variables in KEY=VALUE format.

Command-line Arguments:
    - service_name (str): Name of the service containing the module.
    - --module / -m (str): Python module within the service that defines the settings.
    - --output / -o (str, optional): Output path for the generated `.env` file. Defaults to `.env`.

Raises:
    - ImportError: If the module or settings classes cannot be found.

Example usage:
    python generate_env.py my_service --module config.settings --output .env.development
"""

import os
import sys
import inspect
import argparse
import importlib
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Type

import pydantic_settings


# Get the parent directory and append it to sys.path
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_path not in sys.path:
    sys.path.append(parent_path)


def find_settings_module(service_name: str, module_name: str) -> ModuleType:
    """
    Dynamically imports and returns a Python module given a service and module name.

    This function attempts to import a module using the fully qualified name
    constructed by combining `service_name` and `module_name`. If the import fails,
    it raises an ImportError with a message indicating the service name.

    Args:
        - service_name (str): The base package or service containing the desired module.
        - module_name (str): The specific module name to import within the service.

    Returns:
        - ModuleType: The imported module object.

    Raises:
        - ImportError: If the module cannot be imported (e.g., it does not exist).
    """
    try:
        return importlib.import_module(f'{service_name}.{module_name}')
    except ImportError:
        raise ImportError(f"Could not find module {service_name}")


def get_all_settings_classes(module: ModuleType) -> List[Type[pydantic_settings.BaseSettings]]:
    """
    Retrieves all classes in the given module that are subclasses of pydantic BaseSettings.

    This function inspects all members of the provided module and collects those
    that are classes inheriting from `pydantic_settings.BaseSettings`, excluding the base class itself.

    Args:
        - module (ModuleType): The module to inspect for settings classes.

    Returns:
        - List[Type[pydantic_settings.BaseSettings]]: A list of classes that inherit from BaseSettings.
    """
    settings_classes = []
    
    for name, obj in inspect.getmembers(module):
        # Check if it's a class and subclass of BaseSettings
        if inspect.isclass(obj) and issubclass(obj, pydantic_settings.BaseSettings) and obj != pydantic_settings.BaseSettings:
            settings_classes.append(obj)
    
    return settings_classes


def get_env_vars_from_settings(settings_class: Type[pydantic_settings.BaseSettings]) -> Dict[str, Any]:
    """
    Extracts environment variable names and their default values from a Pydantic settings class.

    This function iterates through the fields of a Pydantic BaseSettings subclass and collects
    their default values (if provided). Fields without a default are assigned None.

    Args:
        - settings_class (Type[pydantic_settings.BaseSettings]): A subclass of Pydantic BaseSettings 
          from which to extract environment variable defaults.

    Returns:
        - Dict[str, Any]: A dictionary mapping field names to their default values or None.
    """
    env_vars = {}
    
    # Get field info
    for field_name, field in settings_class.model_fields.items():
        default_value = field.default if field.default is not inspect.Signature.empty else None
        
        # Add to our env vars dict
        env_vars[field_name] = default_value
    
    return env_vars


def create_env_file(env_vars: Dict[str, Any], output_path: Path) -> None:
    """
    Creates a .env file at the specified path using the provided environment variables.

    This function writes each key-value pair in the `env_vars` dictionary to a new line
    in the .env file, converting values to strings and handling types like booleans,
    lists, and dictionaries. String values containing spaces are wrapped in quotes.

    Args:
        - env_vars (Dict[str, Any]): A dictionary of environment variable names and their values.
        - output_path (Path): The file path where the .env file should be created.
    """
    with open(output_path, 'w') as f:
        for name, value in env_vars.items():
            # Convert value to string and handle different types
            if isinstance(value, bool):
                value_str = str(value).lower()
            elif isinstance(value, (list, dict)):
                value_str = repr(value)
            else:
                value_str = str(value)
                
            # Add quotes for strings with spaces
            if ' ' in value_str and not (value_str.startswith('"') or value_str.startswith("'")):
                value_str = f'"{value_str}"'
                
            f.write(f"{name}={value_str}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate .env file from pydantic_settings settings")
    parser.add_argument("service_name", help="Name of the service to generate .env for")
    parser.add_argument("--module", "-m", required=True, help="Python module containing settings class")
    parser.add_argument("--output", "-o", default=".env", help="Output file path (default: .env)")
    args = parser.parse_args()
    
    # Try to find and import the settings module
    module = find_settings_module(args.service_name, args.module)
    
    # Get all settings classes
    settings_classes = get_all_settings_classes(module)
    if not settings_classes:
        raise ImportError(f"No settings classes found in module {args.module}")

    # Extract environment variables
    env_vars = {}
    for settings_class in settings_classes:
        setting_env_vars = get_env_vars_from_settings(settings_class)
        if setting_env_vars:
            env_vars.update(setting_env_vars)
    
    # Create .env file
    output_path = Path(args.output)
    create_env_file(env_vars, output_path)

    print(f".env file created at {output_path}")


if __name__ == "__main__":
    main()
