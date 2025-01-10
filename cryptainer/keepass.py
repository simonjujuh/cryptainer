from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError
from typing import Optional


class KeepassManager:
    """
    A manager class to interact with a Keepass database.
    """

    def __init__(self, db_path: str, keyfile: Optional[str] = None):
        """
        Initialize the KeepassManager.

        Args:
            db_path (str): Path to the Keepass database file.
            keyfile (str, optional): Path to the Keepass keyfile (if used).
        """
        self.db_path = db_path
        self.keyfile = keyfile
        self.kp = None  # Will store the loaded Keepass database instance

    def open_database(self, master_key: str):
        """
        Open the Keepass database using the provided master key.

        Args:
            master_key (str): The master password for the Keepass database.

        Raises:
            CredentialsError: If the master key or keyfile is incorrect.
            FileNotFoundError: If the database file is not found.
        """
        try:
            self.kp = PyKeePass(self.db_path, password=master_key, keyfile=self.keyfile)
        except CredentialsError:
            raise CredentialsError("Invalid master key or keyfile.")
        except Exception as e:
            raise Exception(f"Unexpected error while opening the database: {e}")

    def fetch_entry(self, title: str) -> Optional[str]:
        """
        Fetch a password for a given entry title from the Keepass database.

        Args:
            title (str): The title of the entry to fetch.

        Returns:
            str: The password for the entry, or None if the entry does not exist.
        """
        if not self.kp:
            raise Exception("Keepass database is not open. Please call open_database() first.")

        entry = self.kp.find_entries(title=title, first=True)
        if not entry:
            raise Exception(f"Cound not find entry: {title}")
        return entry.password

    def add_or_update_entry(self, title: str, username: str, password: str, group: Optional[str] = None):
        """
        Add a new entry or update an existing one in the Keepass database.

        Args:
            title (str): The title of the entry.
            username (str): The username for the entry.
            password (str): The password for the entry.
            group (str, optional): The group to place the entry in. Defaults to the root group.
        """
        if not self.kp:
            raise Exception("Keepass database is not open. Please call open_database() first.")

        # Find existing entry
        entry = self.kp.find_entries(title=title, first=True)

        if entry:
            # Update existing entry
            entry.username = username
            entry.password = password
        else:
            # Add new entry in the specified group
            if group:
                group = self.kp.find_groups(name=group, first=True)
            self.kp.add_entry(group or self.kp.root_group, title, username, password)

    def save_database(self):
        """
        Save changes to the Keepass database.
        """
        if not self.kp:
            raise Exception("Keepass database is not open. Please call open_database() first.")
        self.kp.save()

if __name__ == '__main__':
    pass