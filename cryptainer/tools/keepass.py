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
            raise Exception(f"Failed to open Keepass database: {e}")

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
            raise (f"Password for {entry_name} not found")

if __name__ == '__main__':
    db_path = Path("./tests/passwords.kdbx")
    
    keyfile_path = None  # Remplacez par un fichier clé si nécessaire
    password = "test_password"


    # Instancie le gestionnaire KeePass
    manager = KeepassManager(db_path=db_path, keyfile=keyfile_path, password=password)

    # Teste le stockage et la récupération de mots de passe
    try:
        # Stocke un mot de passe
        manager.store_password(entry_name="Test Entry", username="test_user", password="test_pass", url="https://example.com")
        print("Mot de passe stocké avec succès.")

        # Récupère le mot de passe
        retrieved_password = manager.retrieve_password("Test Entry")
        if retrieved_password:
            print(f"Mot de passe récupéré : {retrieved_password}")
        else:
            print("Impossible de récupérer le mot de passe.")

    except Exception as e:
        log.error(f"Erreur lors du test : {e}")