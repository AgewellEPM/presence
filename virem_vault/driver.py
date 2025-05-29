import os
import json
from cryptography.fernet import Fernet, InvalidToken
import base64
import hashlib
import configparser # Although configparser is imported, config.json is used via json module

# Define paths
CONFIG_FILE = "config/config.json"
VAULT_DATA_DIR = "vault_data"
KEY_DERIVATION_SALT = b'presence_ai_ghost_vault_salt' # A fixed salt for key derivation

class VIREMVaultDriver:
    """
    Handles persistent memory encryption, file creation, and retrieval for the VIREM Vault.
    This class now implements the "Ghost Vault" concept, where memory is encrypted
    and accessible only via a specific wake phrase.
    """

    def __init__(self):
        """
        Initializes the VIREMVaultDriver.
        Loads configuration. Encryption key is now derived dynamically per operation.
        """
        self.config = self._load_config()
        self.vault_location = self.config.get("vault", {}).get("location", VAULT_DATA_DIR)
        self.encryption_enabled = self.config.get("vault", {}).get("encryption_enabled", True)

        # Ensure the vault data directory exists
        os.makedirs(self.vault_location, exist_ok=True)
        print(f"VIREM Vault initialized. Location: {self.vault_location}, Encryption Enabled: {self.encryption_enabled}")
        print("Note: Encryption key is now derived from a wake phrase for Ghost Vault functionality.")

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

    def _derive_key_from_phrase(self, phrase: str) -> Fernet:
        """
        Derives a Fernet encryption key from a given wake phrase using SHA256.

        Args:
            phrase (str): The wake phrase to use for key derivation.

        Returns:
            Fernet: An initialized Fernet cipher object.
        """
        if not isinstance(phrase, str) or not phrase:
            raise ValueError("Wake phrase cannot be empty or non-string.")

        # Use PBKDF2HMAC for stronger key derivation in a real application,
        # but for simplicity and to match user's example, we'll use sha256 + base64.
        # Note: For production, consider using `kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), ...)`
        # and storing salt securely.
        hashed_phrase = hashlib.sha256(phrase.encode('utf-8') + KEY_DERIVATION_SALT).digest()
        key = base64.urlsafe_b64encode(hashed_phrase)
        return Fernet(key)

    def _get_memory_filepath(self, memory_id: str) -> str:
        """Generates a file path for a given memory ID with a .ghost extension."""
        # Use a hash of the memory_id to create a filename, ensuring valid filenames
        safe_memory_id = hashlib.sha256(memory_id.encode('utf-8')).hexdigest()
        return os.path.join(self.vault_location, f"{safe_memory_id}.ghost")

    def store_memory(self, memory_id: str, data: dict, wake_phrase: str) -> bool:
        """
        Stores a piece of memory persistently, encrypting it with a key derived
        from the provided wake phrase.

        Args:
            memory_id (str): A unique identifier for the memory.
            data (dict): The data to be stored (e.g., interaction details, emotional context).
            wake_phrase (str): The phrase used to encrypt this memory. This phrase will be
                                required to retrieve it.

        Returns:
            bool: True if memory was stored successfully, False otherwise.
        """
        filepath = self._get_memory_filepath(memory_id)
        try:
            fernet = self._derive_key_from_phrase(wake_phrase)
            json_data = json.dumps(data)
            if self.encryption_enabled:
                encrypted_data = fernet.encrypt(json_data.encode('utf-8'))
                with open(filepath, 'wb') as f:
                    f.write(encrypted_data)
                print(f"Memory '{memory_id}' encrypted and stored as .ghost file.")
            else:
                # If encryption is disabled, store in plain JSON (not recommended for Ghost Vault)
                with open(filepath, 'w') as f:
                    f.write(json_data)
                print(f"Memory '{memory_id}' stored (unencrypted, not true Ghost Vault).")
            return True
        except ValueError as ve:
            print(f"Error deriving key for storing memory '{memory_id}': {ve}")
            return False
        except Exception as e:
            print(f"Error storing memory '{memory_id}': {e}")
            return False

    def retrieve_memory(self, memory_id: str, wake_phrase: str) -> dict | None:
        """
        Retrieves a piece of memory, attempting to decrypt it with the provided wake phrase.
        If decryption fails (e.g., incorrect phrase), it returns None.

        Args:
            memory_id (str): The unique identifier of the memory to retrieve.
            wake_phrase (str): The phrase required to decrypt this memory.

        Returns:
            dict | None: The retrieved memory data as a dictionary, or None if not found,
                         decryption fails, or an error occurs.
        """
        filepath = self._get_memory_filepath(memory_id)
        if not os.path.exists(filepath):
            print(f"Memory '{memory_id}' (.ghost file) not found at {filepath}.")
            return None

        try:
            fernet = self._derive_key_from_phrase(wake_phrase)
            if self.encryption_enabled:
                with open(filepath, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = fernet.decrypt(encrypted_data).decode('utf-8')
                print(f"Memory '{memory_id}' decrypted and retrieved with correct phrase.")
                return json.loads(decrypted_data)
            else:
                # If encryption is disabled, retrieve plain JSON
                with open(filepath, 'r') as f:
                    json_data = f.read()
                print(f"Memory '{memory_id}' retrieved (unencrypted).")
                return json.loads(json_data)
        except InvalidToken:
            print(f"❌ Incorrect wake phrase or corrupted vault for memory '{memory_id}'. Memory remains hidden.")
            return None
        except ValueError as ve:
            print(f"Error deriving key for retrieving memory '{memory_id}': {ve}")
            return None
        except Exception as e:
            print(f"Error retrieving memory '{memory_id}': {e}")
            # Attempt to delete potentially corrupted file if other errors occur
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"Removed potentially corrupted memory file: {filepath}")
                except OSError as oe:
                    print(f"Error removing corrupted file {filepath}: {oe}")
            return None

    def delete_memory(self, memory_id: str) -> bool:
        """
        Deletes a piece of memory (the .ghost file).

        Args:
            memory_id (str): The unique identifier of the memory to delete.

        Returns:
            bool: True if memory was deleted successfully, False otherwise.
        """
        filepath = self._get_memory_filepath(memory_id)
        if not os.path.exists(filepath):
            print(f"Memory '{memory_id}' (.ghost file) not found for deletion.")
            return False
        try:
            os.remove(filepath)
            print(f"Memory '{memory_id}' (.ghost file) deleted successfully.")
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

    test_memory_id = "user_interaction_ghost_123"
    test_data = {
        "interaction_text": "The user expressed joy about the new feature, this is a secret memory.",
        "timestamp": "2023-10-27T10:00:00Z",
        "emotional_impact": {"joy": 0.9, "sadness": 0.05},
        "secret_flag": True
    }
    correct_wake_phrase = "remember the sunflower"
    incorrect_wake_phrase = "forget the moon"

    print("\n--- Storing Ghost Memory ---")
    if vault.store_memory(test_memory_id, test_data, correct_wake_phrase):
        print("Ghost Memory stored successfully.")
    else:
        print("Failed to store Ghost Memory.")

    print("\n--- Attempting to Retrieve Ghost Memory with INCORRECT Phrase ---")
    retrieved_data_incorrect = vault.retrieve_memory(test_memory_id, incorrect_wake_phrase)
    if retrieved_data_incorrect is None:
        print("Correctly failed to retrieve with incorrect phrase. Memory remains hidden.")
    else:
        print("ERROR: Retrieved memory with incorrect phrase!")

    print("\n--- Attempting to Retrieve Ghost Memory with CORRECT Phrase ---")
    retrieved_data_correct = vault.retrieve_memory(test_memory_id, correct_wake_phrase)
    if retrieved_data_correct:
        print("Retrieved Data with correct phrase:", retrieved_data_correct)
        assert retrieved_data_correct == test_data # Verify data integrity
        print("Data integrity verified.")
    else:
        print("Failed to retrieve memory with correct phrase.")

    print("\n--- Attempting to retrieve non-existent Ghost Memory ---")
    non_existent_data = vault.retrieve_memory("non_existent_ghost_memory", "any_phrase")
    if non_existent_data is None:
        print("Correctly identified non-existent ghost memory.")

    print("\n--- Deleting Ghost Memory ---")
    if vault.delete_memory(test_memory_id):
        print("Ghost Memory deleted successfully.")
    else:
        print("Failed to delete Ghost Memory.")

    print("\n--- Verifying Deletion ---")
    verified_deleted_data = vault.retrieve_memory(test_memory_id, correct_wake_phrase)
    if verified_deleted_data is None:
        print("Ghost Memory confirmed deleted.")
    else:
        print("ERROR: Ghost Memory still exists after deletion attempt.")
