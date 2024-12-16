import argparse, sys
from getpass import getpass
from cryptainer.manager import VolumeManager
from cryptainer.config import ConfigManager
from cryptainer.tools.passgen import PasswordGenerator
from cryptainer.tools.keepass import KeepassManager
from cryptainer.logger import log



def main():

    config = ConfigManager()
    config.load()

    # CLI parsers
    parser = argparse.ArgumentParser(prog="cryptainer.py", description="Manage encrypted volumes")
    # parser.add_argument(
    #    "--debug",
    #     action="store_true",
    #     help="Enable debug mode for detailed logging",
    # )

    # subparsers = parser.add_subparsers(dest="command")

    # List Volumes
    parser.add_argument("-l", "--list", action="store_true", help="List all encrypted volumes")

    # Create Volume
    creation = parser.add_argument_group("volume creation")
    creation.add_argument("-c", "--create", help="Create an encrypted volume")
    creation.add_argument("-t", "--type", choices=["gocryptfs", "veracrypt"], help="Volume type")
    creation.add_argument("-s", "--size", help="Size of the volume (e.g., 10G, 500M). Required for VeraCrypt")
    creation.add_argument("-a", "--auto-mount", action="store_true", help="Automatically mount the volume after creation")

    operations = parser.add_argument_group("volume mounting and unmounting")
    operations.add_argument("-m", "--mount", nargs="+", help="List of volumes to mount")
    operations.add_argument("-u", "--umount", nargs="+", help="List of volumes to unmount")
    # parser.add_argument("-T", "--template", action="store_true", help="Automatically mount the volume after creation")
    # Mount Volume
    # Use keepass for mounting or creating volumes
    # parser.add_argument("-k", "--use-keepass", action="store_true", help="Store the password in the Keepass database")
    # Unmount Volume

    # Prune
    # prune_parser = subparsers.add_parser("prune", help="Remove old or unused volumes")
    # prune_parser.add_argument("--max-age", type=int, default=None, help="Maximum age of volumes to keep (in days)")
    # Clean
    # subparsers.add_parser("clean", help="Clean up temporary files or mount points")

    # Parse arguments and route commands
    args = parser.parse_args()

    # Configure logger based on debug mode
    # if args.debug:
    #     log.set_debug(True)
    #     log.debug("Debug mode enabled")
    # else:
    #     log.set_debug(False)

    manager = VolumeManager(
        config.get("volumes", "volumes_dir"),
        config.get("volumes", "mount_dir"),
    )

    if args.list:
        manager.list_volumes()

    elif args.create:

        try:
            length = int(config.get("passgen", "length"))
            password = PasswordGenerator(length).generate_password()
            manager.create_volume(args.type, args.create, password, args.size, args.auto_mount)

        except Exception as e:
            log.error(f"Could not create volume: {e}")
            return 1
    
    elif args.mount:
        for volume in args.mount:
            try:
                password = log.prompt(f"Password for '{volume}': ")
                manager.mount_volume(volume, password)
            except Exception as e:
                log.error(f"Could not mount volume '{volume}': {e}")

    elif args.umount:
        for volume in args.umount:
            try:
                manager.unmount_volume(volume)
            except Exception as e:
                log.error(f"Could not unmount volume '{volume}': {e}")

    else:
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main())