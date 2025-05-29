import os
import json
from cryptography.fernet import Fernet
import base64
import hashlib
import configparser

# Define paths
CONFIG_FILE = "config/config.json"
VAULT_DATA_DIR = "vault_data"

class VIREMVaultDriver:
    """
    Handles persistent memory encryption, file creation, and retrieval for the VIREM Vault.
    This class manages the secure storage of AI memories.
    """

    def __init__(self):
        """
        Initializes the VIREMVaultDriver.
        Loads configuration and sets up encryption key.
        """
        self.config = self._load_config()
        self.vault_location = self.config.get("vault", {}).get("location", VAULT_DATA_DIR)
        self.encryption_enabled = self.config.get("vault", {}).get("encryption_enabled", True)

        # Ensure the vault data directory exists
        os.makedirs(self.vault_location, exist_ok=True)
        print(f"VIREM Vault initialized. Location: {self.vault_location}, Encryption Enabled: {self.encryption_enabled}")

        self._encryption_key = None
        if self.encryption_enabled:
            # In a real application, the key should be loaded securely,
            # not generated on each run or stored directly in config.json.
            # For this demo, we'll generate a key if one doesn't exist.
            self._encryption_key = self._load_or_generate_key()
            if self._encryption_key:
                self.fernet = Fernet(self._encryption_key)
                print("Encryption key loaded/generated.")
            else:
                print("Warning: Could not load or generate encryption key. Encryption will be disabled.")
                self.encryption_enabled = False
        else:
            print("Encryption is disabled as per configuration.")

    def _load_config(self) -> dict:
        """Loads configuration from config.json."""
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {CONFIG_FILE} not found. Using default settings.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {CONFIG_FILE}. Using default settings.")
            return {}

    def _load_or_generate_key(self) -> bytes:
        """
        Loads the encryption key from a file or generates a new one.
        In a production system, this key management needs to be much more robust.
        """
        key_file_path = os.path.join(self.vault_location, ".vault_key")
        if os.path.exists(key_file_path):
            try:
                with open(key_file_path, 'rb') as f:
                    key = f.read()
                    print(f"Encryption key loaded from {key_file_path}")
                    return key
            except IOError as e:
                print(f"Error reading key file: {e}")
                return None
        else:
            key = Fernet.generate_key()
            try:
                with open(key_file_path, 'wb') as f:
                    f.write(key)
                print(f"New encryption key generated and saved to {key_file_path}")
                return key
            except IOError as e:
                print(f"Error writing key file: {e}")
                return None

    def _get_memory_filepath(self, memory_id: str) -> str:
        """Generates a file path for a given memory ID."""
        # Use a hash of the memory_id to create a filename, ensuring valid filenames
        safe_memory_id = hashlib.sha256(memory_id.encode('utf-8')).hexdigest()
        return os.path.join(self.vault_location, f"{safe_memory_id}.mem")

    def store_memory(self, memory_id: str, data: dict) -> bool:
        """
        Stores a piece of memory persistently.

        Args:
            memory_id (str): A unique identifier for the memory.
            data (dict): The data to be stored (e.g., interaction details, emotional context).

        Returns:
            bool: True if memory was stored successfully, False otherwise.
        """
        filepath = self._get_memory_filepath(memory_id)
        try:
            json_data = json.dumps(data)
            if self.encryption_enabled and self._encryption_key:
                encrypted_data = self.fernet.encrypt(json_data.encode('utf-8'))
                with open(filepath, 'wb') as f:
                    f.write(encrypted_data)
                print(f"Memory '{memory_id}' encrypted and stored.")
            else:
                with open(filepath, 'w') as f:
                    f.write(json_data)
                print(f"Memory '{memory_id}' stored (unencrypted).")
            return True
        except Exception as e:
            print(f"Error storing memory '{memory_id}': {e}")
            return False

    def retrieve_memory(self, memory_id: str) -> dict | None:
        """
        Retrieves a piece of memory.

        Args:
            memory_id (str): The unique identifier of the memory to retrieve.

        Returns:
            dict | None: The retrieved memory data as a dictionary, or None if not found or error.
        """
        filepath = self._get_memory_filepath(memory_id)
        if not os.path.exists(filepath):
            print(f"Memory '{memory_id}' not found at {filepath}.")
            return None

        try:
            if self.encryption_enabled and self._encryption_key:
                with open(filepath, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data).decode('utf-8')
                print(f"Memory '{memory_id}' decrypted and retrieved.")
                return json.loads(decrypted_data)
            else:
                with open(filepath, 'r') as f:
                    json_data = f.read()
                print(f"Memory '{memory_id}' retrieved (unencrypted).")
                return json.loads(json_data)
        except Exception as e:
            print(f"Error retrieving memory '{memory_id}': {e}")
            # Attempt to delete corrupted file if decryption fails, to prevent future issues
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"Removed potentially corrupted memory file: {filepath}")
                except OSError as oe:
                    print(f"Error removing corrupted file {filepath}: {oe}")
            return None

    def delete_memory(self, memory_id: str) -> bool:
        """
        Deletes a piece of memory.

        Args:
            memory_id (str): The unique identifier of the memory to delete.

        Returns:
            bool: True if memory was deleted successfully, False otherwise.
        """
        filepath = self._get_memory_filepath(memory_id)
        if not os.path.exists(filepath):
            print(f"Memory '{memory_id}' not found for deletion.")
            return False
        try:
            os.remove(filepath)
            print(f"Memory '{memory_id}' deleted successfully.")
            return True
        except OSError as e:
            print(f"Error deleting memory '{memory_id}': {e}")
            return False

# Example Usage (for testing purposes, not part of the class itself)
if __name__ == "__main__":
    # Ensure a config.json exists for testing
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                "vault": {"location": "./vault_data", "encryption_enabled": True},
                "modes": {"persistent_memory": True, "debug_mode": False},
                "keys": {"example_api_key": "YOUR_API_KEY_HERE"}
            }, f, indent=2)
        print(f"Created a dummy {CONFIG_FILE} for testing.")

    vault = VIREMVaultDriver()

    test_memory_id = "user_interaction_123"
    test_data = {
        "interaction_text": "The user expressed joy about the new feature.",
        "timestamp": "2023-10-27T10:00:00Z",
        "emotional_impact": {"joy": 0.8, "sadness": 0.1}
    }

    print("\n--- Storing Memory ---")
    if vault.store_memory(test_memory_id, test_data):
        print("Memory stored successfully.")
    else:
        print("Failed to store memory.")

    print("\n--- Retrieving Memory ---")
    retrieved_data = vault.retrieve_memory(test_memory_id)
    if retrieved_data:
        print("Retrieved Data:", retrieved_data)
        assert retrieved_data == test_data # Verify data integrity
    else:
        print("Failed to retrieve memory.")

    print("\n--- Attempting to retrieve non-existent Memory ---")
    non_existent_data = vault.retrieve_memory("non_existent_memory")
    if non_existent_data is None:
        print("Correctly identified non-existent memory.")

    print("\n--- Deleting Memory ---")
    if vault.delete_memory(test_memory_id):
        print("Memory deleted successfully.")
    else:
        print("Failed to delete memory.")

    print("\n--- Verifying Deletion ---")
    verified_deleted_data = vault.retrieve_memory(test_memory_id)
    if verified_deleted_data is None:
        print("Memory confirmed deleted.")
    else:
        print("Memory still exists after deletion attempt.")
