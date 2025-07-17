"""
This script adds packages to the requirements.txt file and installs them using pip if they are not already installed.
It takes a string of package names separated by spaces as input, checks if each package is listed in requirements.txt,
and adds it if it's missing. Then, it attempts to install the package using pip. The script provides feedback on
whether each package was already installed or has been successfully installed as a result of the script's execution.

Example usage:
    python add_packages.py requests python-dotenv
"""

import subprocess
import sys

def add_package_to_requirements(packages_str):
    packages = packages_str.split()
    requirements_path = '/app/requirements.txt'

    # Read the current contents of the requirements file
    with open(requirements_path, 'r') as file:
        existing_packages = file.read().splitlines()

    # Check each package if it needs to be added to the requirements file
    for package in packages:
        if package not in existing_packages:
            with open(requirements_path, 'a') as file:
                file.write(f"{package}\n")
            print(f"Added {package} to requirements.txt")
        else:
            print(f"{package} is already in requirements.txt")

        # Check if the package is already installed
        if not is_package_installed(package):
            # Install the package
            install_package(package)
        else:
            print(f"{package} is already installed.")

def is_package_installed(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}. Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        packages_str = ' '.join(sys.argv[1:])
        add_package_to_requirements(packages_str)
    else:
        print("Usage: python add_packages.py <package1> <package2> ...")
