import configparser
import sys
import shutil
from pathlib import Path
from cryptainer.log import *

DEFAULT_CONFIG_DIR = Path.home() / ".cryptainer"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.ini"
DEFAULT_CONFIG_SOURCE = Path(__file__).resolve().parent / "data" / "config.ini" # ./data/config.ini

def load_config():
    """
    Loads the configuration. If the config file doesn't exist,
    a default config file is created, and the user should fill in the desired parameters.
    """
    if not DEFAULT_CONFIG_PATH.exists():
        create_default_config()
        print_info(f"A new config file has been created at {DEFAULT_CONFIG_PATH}")
        sys.exit(0)


    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_PATH)

    # Expand and validate paths
    expand_and_validate_paths(config)

    return config


def create_default_config():
    """
    Copies the default configuration file from the source location
    to the destination location.
    """
    
    # Vérifiez si le fichier source existe
    if not DEFAULT_CONFIG_SOURCE.exists():
        print_error(f"Default config file not found at {DEFAULT_CONFIG_SOURCE}")
        sys.exit(1)
    
    # Créez le répertoire de destination s'il n'existe pas déjà
    DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Copiez le fichier de configuration
    shutil.copy(DEFAULT_CONFIG_SOURCE, DEFAULT_CONFIG_PATH)


def expand_and_validate_paths(config):
    """
    Expands and validates the paths defined in the configuration file.
    """
    paths_to_validate = [
        ("volumes", "volumes_dir"),
        ("volumes", "mount_dir"),
        # ("template", "template_path"),
        # ("keepass", "database"),
        # ("keepass", "keyfile")
    ]

    for section, option in paths_to_validate:
        if section in config and option in config[section]:
            raw_path = config.get(section, option, fallback="").strip()

            # If path is empty and optional, skip validation
            if not raw_path:
                if section in ["template", "keepass"] and option in ["template_path", "database", "keyfile"]:
                    continue
                raise Exception(option, f"Path in [{section}] {option} cannot be empty")

            resolved_path = Path(raw_path).expanduser().resolve()
            if not resolved_path.exists():
                raise Exception(resolved_path, f"Invalid path in [{section}] {option}")

            # Update the configuration with the resolved path
            config[section][option] = str(resolved_path)

# Exemple d'utilisation
if __name__ == "__main__":
    load_config()