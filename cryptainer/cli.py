import argparse
from getpass import getpass
from cryptainer.manager import VolumeManager
from cryptainer.config import ConfigManager
from cryptainer.tools.passgen import PasswordGenerator
from cryptainer.logger import log

def prompt_password(confirm=False):
    """
    Prompt the user for a password securely.

    Args:
        confirm (bool): Whether to prompt for password confirmation.

    Returns:
        str: The entered password.
    """
    while True:
        password = getpass("Enter password: ")
        if confirm:
            password_confirm = getpass("Confirm password: ")
            if password != password_confirm:
                print("Passwords do not match. Please try again.")
                continue
        return password

def main():

    config = ConfigManager()
    config.load()

    # CLI parsers
    parser = argparse.ArgumentParser(prog="cryptainer.py", description="Manage encrypted volumes")
    parser.add_argument(
       "--debug",
        action="store_true",
        help="Enable debug mode for detailed logging",
    )

    subparsers = parser.add_subparsers(dest="command")

    # List Volumes
    subparsers.add_parser("list", help="List all encrypted volumes")

    # Create Volume
    create_parser = subparsers.add_parser("create", help="Create an encrypted volume")
    create_parser.add_argument("-t", "--type", required=True, choices=["gocryptfs", "veracrypt"], help="Volume type")
    create_parser.add_argument("-s", "--size", help="Size of the volume (e.g., 10G, 500M). Required for VeraCrypt")
    create_parser.add_argument("-a", "--auto-mount", action="store_true", help="Automatically mount the volume after creation")
    create_parser.add_argument("-T", "--template", action="store_true", help="Automatically mount the volume after creation")
    # create_parser.add_argument("-k", "--use-keepass", action="store_true", help="Store the password in the Keepass database")
    create_parser.add_argument("name", help="Name of the volume")

    # Mount Volume
    mount_parser = subparsers.add_parser("mount", help="Mount encrypted volumes")
    # mount_parser.add_argument("-k", "--use-keepass", action="store_true", help="Store the password in the Keepass database")
    mount_parser.add_argument("volumes", nargs="+", help="List of volumes to mount")

    # Unmount Volume
    umount_parser = subparsers.add_parser("umount", help="Unmount encrypted volumes")
    umount_parser.add_argument("volumes", nargs="+", help="List of volumes to unmount")

    # Prune
    # prune_parser = subparsers.add_parser("prune", help="Remove old or unused volumes")
    # prune_parser.add_argument("--max-age", type=int, default=None, help="Maximum age of volumes to keep (in days)")

    # Clean
    # subparsers.add_parser("clean", help="Clean up temporary files or mount points")

    # Parse arguments and route commands
    args = parser.parse_args()

    # Configure logger based on debug mode
    if args.debug:
        log.set_debug(True)
        log.debug("Debug mode enabled")
    else:
        log.set_debug(False)

    manager = VolumeManager(
        config.get("volumes", "volumes_dir"),
        config.get("volumes", "mount_dir"),
    )

    if args.command == "list":
        manager.list_volumes()

    elif args.command == "create":
        try:
            manager.create_volume(args.type, args.name, password, args.size, args.auto_mount)
        except Exception as e:
            log.error(f"Could not create volume: {e}")

    elif args.command == "mount":
        for volume in args.volumes:
            try:
                # Prompt for password for each volume
                password = prompt_password()
                manager.mount_volume(volume, password)
            except Exception as e:
                log.error(f"Could not mount volume '{volume}': {e}")

    elif args.command == "umount":
        for volume in args.volumes:
            try:
                manager.unmount_volume(volume)
            except Exception as e:
                log.error(f"Could not unmount volume '{volume}': {e}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()