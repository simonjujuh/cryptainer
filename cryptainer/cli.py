import argparse
import sys
from pathlib import Path
from cryptainer.log import *
from cryptainer.config import load_config
from cryptainer.controller import VolumeController
from cryptainer.password import generate_password
from cryptainer.volumes.gocryptfs import GocryptfsTool

# Supported volume types
supported_volume_types = ['gocryptfs', 'veracrypt']
# Enable debug mode

def main():

    # Load the configuration file
    config = load_config()

    # Create a volume controller for managing volumes
    controller = VolumeController(
        config.get("volumes", "volumes_dir"),
        config.get("volumes", "mount_dir")
    )

    try:
        import argcomplete
        completion = True
    except ImportError:
        completion = False

    # Create the main parser
    parser = argparse.ArgumentParser(prog="cryptainer", description="Manage encrypted volumes")
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Command: list
    parser_list = subparsers.add_parser("list", help="List available encrypted volumes")
    parser_list.add_argument("--show-unknown", action="store_true", help="Show volumes with unknown types")

    # Command: create
    parser_create = subparsers.add_parser("create", help="Create a new volume")
    parser_create.add_argument("-t", "--type", required=True, choices=supported_volume_types, help="Volume type")
    parser_create.add_argument("-s", "--size", required=False, help="Volume size (veracrypt-only)")
    parser_create.add_argument("-a", "--auto-mount", required=False, action="store_true", help="Mount the volume after creation")
    parser_create.add_argument("name", help="Encrypted volume name")

    # Command: mount
    parser_mount = subparsers.add_parser("mount", help="Mount an encrypted volume")
    if completion:
        parser_mount.add_argument("name", type=str, nargs='+', help="Encrypted volume name", choices=controller.get_unmounted_volumes())
    else:
        parser_mount.add_argument("name", type=str, nargs='+', help="Encrypted volume name")

    # Command: unmount
    parser_unmount = subparsers.add_parser("unmount", help="Unmount an encrypted volume")
    if completion:
        parser_unmount.add_argument("name", type=str, nargs='+', help="Target volume name", choices=controller.get_mounted_volumes())
    else:
        parser_unmount.add_argument("name", type=str, nargs='+', help="Target volume name")

    # Parse arguments
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'create':
        if args.type == 'veracrypt' and not args.size:
            print_error("--size option is required when using veracrypt containers")
            return
        controller.create_volume(args.type, args.name, args.size, args.auto_mount)
    elif args.command == 'mount':
        for name in args.name:
            controller.mount_volume(name)
    elif args.command == 'unmount':
        for name in args.name:
            controller.unmount_volume(name)
    elif args.command == 'list':
        controller.list_volumes(args.show_unknown)
    else:
        pass

if __name__ == '__main__':
    main()
