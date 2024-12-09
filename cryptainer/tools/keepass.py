# volumx/tools/keepass.py
from pykeepass import PyKeePass
from pathlib import Path
from cryptainer.logger import log

class KeepassManager:
    def __init__(self, db_path: str, keyfile: str, password: str = None):
        self.db_path = Path(db_path)
        self.keyfile = Path(keyfile) if keyfile else None
        self.password = password
        self.kp = None

    def open_database(self):
        try:
            self.kp = PyKeePass(self.db_path, password=self.password, keyfile=self.keyfile)
        except Exception as e:
            log.error(f"Failed to open Keepass database: {e}")
            raise

    def store_password(self, entry_name: str, username: str, password: str = None, url: str = None):
        if not self.kp:
            self.open_database()
        group = self.kp.find_groups(name="Encrypted volumes", first=True)
        if not group:
            group = self.kp.add_group(self.kp.root_group, "Encrypted volumes")
        entry = self.kp.find_entries(title=entry_name, first=True)
        if entry:
            entry.password = password
        else:
            self.kp.add_entry(group, entry_name, username, password, url)
        self.kp.save()

    def retrieve_password(self, entry_name: str):
        if not self.kp:
            self.open_database()
        entry = self.kp.find_entries(title=entry_name, first=True)
        if entry:
            return entry.password
        else:
            log.error(f"Password for {entry_name} not found.")
            return None
