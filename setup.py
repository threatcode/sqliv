import argparse
import os
import stat
import subprocess
from sys import platform
from shutil import copy2, rmtree
from distutils.dir_util import copy_tree
from typing import List
import sys


__author__ = "Ghost"
__email__ = "official.ghost@tuta.io"
__license__ = "GPL"
__version__ = "2.1"


# Installation directory paths
FILE_PATH_LINUX = "/usr/share/sqliv"
EXEC_PATH_LINUX = "/usr/bin/sqliv"

FILE_PATH_MAC = "/usr/local/bin"
EXEC_PATH_MAC = "/usr/local/bin"


def metadata() -> None:
    """Print metadata about SQLiv"""
    print(f"SQLiv ({__version__}) by {__author__}")
    print("Massive SQL injection vulnerability scanner")


def dependencies(option: str) -> None:
    """Install or uninstall script dependencies with pip
    
    Args:
        option: Either 'install' or 'uninstall'
    """
    try:
        with open("requirements.txt", "r", encoding='utf-8') as requirements:
            dependencies = requirements.read().splitlines()
            dependencies = [dep for dep in dependencies if dep and not dep.startswith('#')]
    except IOError:
        print("requirements.txt not found, please redownload or do pull request again")
        sys.exit(1)

    for lib in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", option, lib], 
                         check=True, 
                         capture_output=True,
                         text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing {lib}: {e.stderr}")
            sys.exit(1)


def install(file_path: str, exec_path: str) -> None:
    """Full installation of SQLiv to the system
    
    Args:
        file_path: Directory path to install SQLiv files
        exec_path: Path to create executable script
    """
    # Create main directory and copy core files
    os.makedirs(file_path, exist_ok=True)
    for file in ["sqliv.py", "requirements.txt", "LICENSE", "README.md"]:
        copy2(file, file_path)

    # Copy source and library directories
    for dir_name in ["src", "lib"]:
        os.makedirs(os.path.join(file_path, dir_name), exist_ok=True)
        copy_tree(dir_name, os.path.join(file_path, dir_name))

    # Install Python dependencies
    dependencies("install")

    # Create executable script
    with open(exec_path, 'w') as installer:
        installer.write('#!/bin/bash\n\n')
        installer.write(f'python3 {os.path.join(file_path, "sqliv.py")} "$@"\n')

    # Set executable permissions (rwx for owner, rx for group and others)
    os.chmod(exec_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def uninstall(file_path: str, exec_path: str) -> None:
    """Uninstall SQLiv from the system
    
    Args:
        file_path: Directory path containing SQLiv files
        exec_path: Path to executable script
    """
    if os.path.exists(file_path):
        rmtree(file_path)
        print(f"Removed {file_path}")

    if os.path.isfile(exec_path):
        os.remove(exec_path)
        print(f"Removed {exec_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLiv installation script")
    parser.add_argument("-i", "--install", help="install sqliv in the system", action='store_true')
    parser.add_argument("-r", "--reinstall", help="remove old files and reinstall to the system", action="store_true")
    parser.add_argument("-u", "--uninstall", help="uninstall sqliv from the system", action="store_true')
    args = parser.parse_args()

    # Set installation paths based on platform
    if platform in ("linux", "linux2"):
        # Linux requires root access
        if os.getuid() != 0:
            print("Linux system requires root access for installation")
            exit(1)
        FILE_PATH = FILE_PATH_LINUX
        EXEC_PATH = EXEC_PATH_LINUX
    elif platform == "darwin":
        FILE_PATH = FILE_PATH_MAC
        EXEC_PATH = EXEC_PATH_MAC
    else:
        print("Windows platform is not supported for installation")
        exit(1)

    # Handle installation options
    if args.install and not (args.reinstall or args.uninstall):
        # Full installation
        if os.path.exists(FILE_PATH):
            print(f"SQLiv is already installed under {FILE_PATH}")
            exit(1)
        if os.path.isfile(EXEC_PATH):
            print(f"Executable file exists under {EXEC_PATH}")
            exit(1)

        install(FILE_PATH, EXEC_PATH)
        print("Installation finished")
        print(f"Files are installed under {FILE_PATH}")
        print("Run: sqliv --help")

    elif args.uninstall and not (args.install or args.reinstall):
        # Uninstall
        uninstall(FILE_PATH, EXEC_PATH)
        
        while True:
            option = input("Do you want to uninstall python dependencies? [Y/N]: ").upper()
            if option in ('Y', 'N'):
                break
                
        if option == 'Y':
            dependencies("uninstall")
            print("Python dependencies removed")
            
        print("Uninstallation finished")

    elif args.reinstall and not (args.install or args.uninstall):
        # Reinstall
        uninstall(FILE_PATH, EXEC_PATH)
        print("Removed previous installed files")

        install(FILE_PATH, EXEC_PATH)
        print("Reinstallation finished")
        print(f"Files are installed under {FILE_PATH}")
        print("Run: sqliv --help")

    else:
        metadata()
        print("")
        parser.print_help()
