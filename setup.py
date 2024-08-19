import argparse
import os
import stat
import sys
import pip
from shutil import copy2, rmtree
from distutils.dir_util import copy_tree

__author__ = "Ghost"
__email__ = "official.ghost@tuta.io"
__license__ = "GPL"
__version__ = "2.0"

# Installation directory paths
FILE_PATH_LINUX = "/usr/share/sqliv"
EXEC_PATH_LINUX = "/usr/bin/sqliv"
FILE_PATH_MAC = "/usr/local/bin/sqliv"
EXEC_PATH_MAC = "/usr/local/bin/sqliv"

def metadata():
    print(f"SQLiv (2.0) by {__author__}")
    print("Massive SQL injection vulnerability scanner")

def install_dependencies(option):
    """Install script dependencies with pip."""
    try:
        with open("requirements.txt", "r") as requirements:
            dependencies = requirements.read().splitlines()
    except IOError:
        print("requirements.txt not found, please redownload or do a pull request again")
        sys.exit(1)

    for lib in dependencies:
        pip.main([option, lib])

def install(file_path, exec_path):
    """Full installation of SQLiv to the system."""
    os.makedirs(file_path, exist_ok=True)
    copy2("sqliv.py", file_path)
    copy2("requirements.txt", file_path)
    copy2("LICENSE", file_path)
    copy2("README.md", file_path)

    os.makedirs(os.path.join(file_path, "src"), exist_ok=True)
    copy_tree("src", os.path.join(file_path, "src"))

    os.makedirs(os.path.join(file_path, "lib"), exist_ok=True)
    copy_tree("lib", os.path.join(file_path, "lib"))

    # Install Python dependencies with pip
    install_dependencies("install")

    # Add executable
    with open(exec_path, 'w') as installer:
        installer.write(f'#!/bin/bash\npython3 {file_path}/sqliv.py "$@"\n')

    os.chmod(exec_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

def uninstall(file_path, exec_path):
    """Uninstall SQLiv from the system."""
    if os.path.exists(file_path):
        rmtree(file_path)
        print(f"Removed {file_path}")

    if os.path.isfile(exec_path):
        os.remove(exec_path)
        print(f"Removed {exec_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--install", help="Install SQLiv in the system", action='store_true')
    parser.add_argument("-r", "--reinstall", help="Remove old files and reinstall to the system", action="store_true")
    parser.add_argument("-u", "--uninstall", help="Uninstall SQLiv from the system", action="store_true")
    args = parser.parse_args()

    if sys.platform.startswith("linux"):
        if os.getuid() != 0:
            print("Linux system requires root access for the installation")
            sys.exit(1)
        FILE_PATH = FILE_PATH_LINUX
        EXEC_PATH = EXEC_PATH_LINUX
    elif sys.platform == "darwin":
        FILE_PATH = FILE_PATH_MAC
        EXEC_PATH = EXEC_PATH_MAC
    else:
        print("Windows platform is not supported for installation")
        sys.exit(1)

    if args.install and not (args.reinstall or args.uninstall):
        if os.path.exists(FILE_PATH):
            print(f"SQLiv is already installed under {FILE_PATH}")
            sys.exit(1)
        if os.path.isfile(EXEC_PATH):
            print(f"Executable file exists under {EXEC_PATH}")
            sys.exit(1)

        install(FILE_PATH, EXEC_PATH)
        print("Installation finished")
        print(f"Files are installed under {FILE_PATH}")
        print("Run: sqliv --help")

    elif args.uninstall and not (args.install or args.reinstall):
        uninstall(FILE_PATH, EXEC_PATH)
        option = input("Do you want to uninstall Python dependencies? [Y/N]: ").strip().upper()
        while option not in ["Y", "N"]:
            option = input("Do you want to uninstall Python dependencies? [Y/N]: ").strip().upper()

        if option == "Y":
            install_dependencies("uninstall")
            print("Python dependencies removed")

        print("Uninstallation finished")

    elif args.reinstall and not (args.install or args.uninstall):
        uninstall(FILE_PATH, EXEC_PATH)
        print("Removed previous installed files")
        install(FILE_PATH, EXEC_PATH)
        print("Reinstallation finished")
        print(f"Files are installed under {FILE_PATH}")
        print("Run: sqliv --help")
    else:
        metadata()
        print()
        parser.print_help()
