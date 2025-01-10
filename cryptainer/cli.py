import argparse
import sys
from pathlib import Path
from cryptainer.log import *
from cryptainer.config import load_config
from cryptainer.controller import VolumeController
from cryptainer.keepass import KeepassManager

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
    parser.add_argument("--no-cleanup", action="store_true", default=False, help="Do not clean empty folders in mount directory")
    
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Command: list
    parser_list = subparsers.add_parser("list", help="List available encrypted volumes")
    parser_list.add_argument("--all", action="store_true", help="Show volumes with unknown types")

    # Command: create
    parser_create = subparsers.add_parser("create", help="Create a new volume")
    parser_create.add_argument("-t", "--type", required=True, choices=supported_volume_types, help="Volume type")
    parser_create.add_argument("-s", "--size", required=False, help="Volume size (veracrypt-only)")
    parser_create.add_argument("-a", "--auto-mount", required=False, action="store_true", help="Mount the volume after creation")
    parser_create.add_argument("-k", "--use-keepass", action="store_true", help="Use keepass database to store or fetch secrets")
    parser_create.add_argument("name", help="Encrypted volume name")

    # Command: mount
    parser_mount = subparsers.add_parser("mount", help="Mount an encrypted volume")
    parser_mount.add_argument("-k", "--use-keepass", action="store_true", help="Use keepass database to store or fetch secrets")
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

    if not args.no_cleanup:
        controller.cleanup()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'create':

        if args.type == 'veracrypt' and not args.size:
            print_error("--size option is required when using veracrypt containers")
            return
        
        # Instanciate the keepass manager
        if args.use_keepass:
            keyfile = config.get("keepass", "keyfile") or None

            try:
                kpm = KeepassManager(
                    config.get("keepass", "database"),
                    keyfile
                )
            except Exception as e:
                print_error(f"Failed to initialize KeepassManager: {e}")
                kpm = None
        
        controller.create_volume(args.type, 
                                 args.name, 
                                 args.size, 
                                 args.auto_mount, 
                                 keepass_manager=kpm)
    
    elif args.command == 'mount':

        # Instanciate the keepass manager
        if args.use_keepass:
            keyfile = config.get("keepass", "keyfile") or None

            try:
                kpm = KeepassManager(
                    config.get("keepass", "database"),
                    keyfile
                )
            except Exception as e:
                print_error(f"Failed to initialize KeepassManager: {e}")
                kpm = None

        for name in args.name:
            controller.mount_volume(name, keepass_manager=kpm)
    elif args.command == 'unmount':
        for name in args.name:
            controller.unmount_volume(name)
    elif args.command == 'list':
        controller.list_volumes(args.all)
    else:
        pass

if __name__ == '__main__':
    main()
