import sys
import argparse
import importlib
from pathlib import Path


COMMANDS_DIR = Path(__file__).parent

sys.path.append(str(COMMANDS_DIR))  # -> cli folder (searching for commands)
sys.path.append( str(COMMANDS_DIR.parent))  # -> users folder (importing from users app within commands)


def load_commands():
    commands = {}

    for command_file in COMMANDS_DIR.glob('*.py'):
        if command_file.stem.startswith('_'):
            continue
        print(command_file)
        module = importlib.import_module(command_file.stem)
        commands[command_file.stem] = module

    return commands


def main():
    parser = argparse.ArgumentParser(description='App Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Load and setup all commands
    commands = load_commands()
    command_parsers = {}

    for command_name, command_module in commands.items():
        command_parsers[command_name] = command_module.setup_parser(subparsers)

    # Parse arguments and handle command
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute the appropriate command
    commands[args.command].handle(args)


if __name__ == '__main__':
    main()
