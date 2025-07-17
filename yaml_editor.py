"""
YAML Editor Script

This script provides command line interface to manipulate YAML files. It supports adding, updating,
removing, and retrieving entries from a YAML file. This tool utilizes the PyYAML package for parsing
and emitting YAML content, and argparse for handling command-line arguments.

Usage Examples:
- Add an entry: python yaml_editor.py file.yaml add parent child value
- Update an entry: python yaml_editor.py file.yaml update parent child new_value
- Remove an entry: python yaml_editor.py file.yaml remove parent child
- Get an entry: python yaml_editor.py file.yaml get parent child
"""

import yaml
import argparse
from typing import Any, Union, List


class YamlEditor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self.load_yaml()

    def load_yaml(self) -> Union[dict, list]:
        """Load YAML file into memory."""
        with open(self.file_path, 'r') as file:
            return yaml.safe_load(file)

    def save_yaml(self):
        """Save the current data back to the YAML file."""
        with open(self.file_path, 'w') as file:
            yaml.safe_dump(self.data, file)

    def get_entry(self, path: List[str]) -> Any:
        """Retrieve an entry from the YAML data based on a list of keys."""
        current_data = self.data
        for key in path:
            current_data = current_data.get(key, None)
            if current_data is None:
                break
        return current_data

    def add_entry(self, path: List[str], value: Any):
        """Add a new entry to the YAML data."""
        current_data = self.data
        for key in path[:-1]:
            current_data = current_data.setdefault(key, {})
        current_data[path[-1]] = value
        self.save_yaml()

    def update_entry(self, path: List[str], value: Any):
        """Update the value of an existing entry."""
        self.add_entry(path, value)

    def remove_entry(self, path: List[str]):
        """Remove an entry from the YAML data."""
        current_data = self.data
        for key in path[:-1]:
            current_data = current_data.get(key, None)
            if current_data is None:
                return  # Early exit if path does not exist
        current_data.pop(path[-1], None)
        self.save_yaml()


class YamlEditor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = self.load_yaml()

    def load_yaml(self) -> Union[dict, list]:
        """Load YAML file into memory."""
        with open(self.file_path, 'r') as file:
            return yaml.safe_load(file)

    def save_yaml(self):
        """Save the current data back to the YAML file."""
        with open(self.file_path, 'w') as file:
            yaml.safe_dump(self.data, file)

    def get_entry(self, path: List[str]) -> Any:
        """Retrieve an entry from the YAML data based on a list of keys."""
        current_data = self.data
        for key in path:
            current_data = current_data.get(key, None)
            if current_data is None:
                break
        return current_data

    def add_entry(self, path: List[str], value: Any):
        """Add a new entry to the YAML data."""
        current_data = self.data
        for key in path[:-1]:
            current_data = current_data.setdefault(key, {})
        current_data[path[-1]] = value
        self.save_yaml()

    def update_entry(self, path: List[str], value: Any):
        """Update the value of an existing entry."""
        self.add_entry(path, value)

    def remove_entry(self, path: List[str]):
        """Remove an entry from the YAML data."""
        current_data = self.data
        for key in path[:-1]:
            current_data = current_data.get(key, None)
            if current_data is None:
                return  # Early exit if path does not exist
        current_data.pop(path[-1], None)
        self.save_yaml()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Manipulate YAML files.")
    parser.add_argument('file_path', help="Path to the YAML file to manipulate.")

    subparsers = parser.add_subparsers(dest='command')

    # Sub-parser for adding an entry
    parser_add = subparsers.add_parser('add', help="Add a new entry to the YAML file.")
    parser_add.add_argument('path', nargs='+', help="Path to set the value at (nested paths separated by space).")
    parser_add.add_argument('value', help="Value to add at the specified path.")

    # Sub-parser for updating an entry
    parser_update = subparsers.add_parser('update', help="Update an existing entry in the YAML file.")
    parser_update.add_argument('path', nargs='+', help="Path to the value to update (nested paths separated by space).")
    parser_update.add_argument('value', help="New value for the specified path.")

    # Sub-parser for removing an entry
    parser_remove = subparsers.add_parser('remove', help="Remove an entry from the YAML file.")
    parser_remove.add_argument('path', nargs='+', help="Path to the entry to remove (nested paths separated by space).")

    # Sub-parser for retrieving an entry
    parser_get = subparsers.add_parser('get', help="Get the value of an entry from the YAML file.")
    parser_get.add_argument('path', nargs='+', help="Path to the entry to retrieve (nested paths separated by space).")

    return parser.parse_args()


def main():
    args = parse_arguments()
    editor = YamlEditor(args.file_path)

    if args.command == 'add':
        editor.add_entry(args.path, yaml.safe_load(args.value))
        print(f"Added entry at {' '.join(args.path)}")
    elif args.command == 'update':
        editor.update_entry(args.path, yaml.safe_load(args.value))
        print(f"Updated entry at {' '.join(args.path)}")
    elif args.command == 'remove':
        editor.remove_entry(args.path)
        print(f"Removed entry at {' '.join(args.path)}")
    elif args.command == 'get':
        value = editor.get_entry(args.path)
        print(f"Value at {' '.join(args.path)}: {value}")

if __name__ == '__main__':
    main()
