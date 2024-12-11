import configparser
import sys
from pathlib import Path
from cryptainer.logger import log

DEFAULT_CONFIG_DIR = Path.home() / ".cryptainer"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.ini"

class ConfigManager:
    def __init__(self):
        self.config_path = Path(DEFAULT_CONFIG_PATH)
        self.config = configparser.ConfigParser()

    def load(self):
        """
        Loads the configuration. If the config file doesn't exist,
        a default config file is created, and the user should fill in the desired parameters.
        """
        if not self.config_path.exists():
            self._create_default_config()
        self.config.read(self.config_path)

        # Expand and validate paths
        self._expand_and_validate_paths()

    def get(self, section, option, fallback=None):
        """
        Retrieves the value of a configuration parameter.
        If the option doesn't exist, the fallback value is returned.
        """
        return self.config.get(section, option, fallback=fallback)

    def _create_default_config(self):
        """
        Creates a default configuration file if it doesn't exist.
        """
        log.warning(f"A new config file has been created at {self.config_path}, please fill your desired parameters")
        default_content = {
            "volumes": {
                "volumes_dir": "",
                "mount_dir": ""
            },
            "template": {
                "template_path": ""
            },
            "keepass": {
                "database": "",
                "keyfile": ""
            },
            "passgen": {
                "length": "30"
            },
            "misc": {
                "prune_max_age": "365",
                "auto_cleanup": "True"
            }
        }
        self.config.read_dict(default_content)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            self.config.write(f)

        sys.exit(0)

    def _expand_and_validate_paths(self):
        """
        Expands and validates the paths defined in the configuration file.
        """
        paths_to_validate = [
            ("volumes", "volumes_dir"),
            ("volumes", "mount_dir"),
            ("template", "template_path"),
            ("keepass", "database"),
            ("keepass", "keyfile")
        ]

        for section, option in paths_to_validate:
            if section in self.config and option in self.config[section]:
                raw_path = self.config.get(section, option, fallback="").strip()

                # If path is empty and optional, skip validation
                if not raw_path:
                    if section in ["template", "keepass"] and option in ["template_path", "database", "keyfile"]:
                        continue
                    raise Exception(option, f"Path in [{section}] {option} cannot be empty")

                resolved_path = Path(raw_path).expanduser().resolve()
                if not resolved_path.exists():
                    raise Exception(resolved_path, f"Invalid path in [{section}] {option}")

                # Update the configuration with the resolved path
                self.config[section][option] = str(resolved_path)

# Exemple d'utilisation
if __name__ == "__main__":
    config_manager = ConfigManager()
    try:
        config_manager.load()
        print("Configuration loaded successfully.")
    except Exception as e:
        log.error(e)
        sys.exit(1)