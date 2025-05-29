import json
import os
import time
from datetime import datetime # Import datetime

# Assuming other core components might be integrated or referenced here
# from ere_core.soft_memory_map import SoftMemoryMap
# from virem_vault.driver import VIREMVaultDriver
# from mood_tracker import MoodTracker
# from body_controller import BodyController

BRAINS_DIR = "brains"
CONFIG_FILE = "config/config.json"

class BrainArchitect:
    """
    Defines, manages, and potentially dynamically builds the AI's "brain" or cognitive architecture.
    This class handles the loading, saving, and configuration of different AI modules
    to form a cohesive "brain profile."
    """

    def __init__(self):
        """
        Initializes the BrainArchitect, ensuring the brains directory exists.
        """
        os.makedirs(BRAINS_DIR, exist_ok=True)
        self.loaded_brain_profile = None
        print(f"BrainArchitect initialized. Brains directory: {BRAINS_DIR}")

    def _load_config(self) -> dict:
        """Loads configuration from config.json."""
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {CONFIG_FILE} not found. Please ensure it exists.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {CONFIG_FILE}. Please check its format.")
            return {}

    def create_brain_profile(self, profile_name: str, modules_config: dict, description: str = "") -> bool:
        """
        Creates a new brain profile configuration file.

        Args:
            profile_name (str): A unique name for the brain profile.
            modules_config (dict): A dictionary defining the configuration for various AI modules.
                                   Example: {"ere_core": {"num_emotions": 7}, "virem_vault": {"encryption_enabled": True}}
            description (str): A brief description of this brain profile.

        Returns:
            bool: True if the profile was created successfully, False otherwise.
        """
        if not profile_name.strip():
            print("Error: Brain profile name cannot be empty.")
            return False

        profile_filepath = os.path.join(BRAINS_DIR, f"{profile_name}.json")
        if os.path.exists(profile_filepath):
            print(f"Warning: Brain profile '{profile_name}' already exists. Overwriting.")

        brain_data = {
            "profile_name": profile_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "modules": modules_config
        }

        try:
            with open(profile_filepath, 'w') as f:
                json.dump(brain_data, f, indent=4)
            print(f"Brain profile '{profile_name}' created successfully at {profile_filepath}")
            return True
        except IOError as e:
            print(f"Error creating brain profile '{profile_name}': {e}")
            return False

    def load_brain_profile(self, profile_name: str) -> dict | None:
        """
        Loads an existing brain profile configuration.

        Args:
            profile_name (str): The name of the brain profile to load.

        Returns:
            dict | None: The loaded brain profile configuration as a dictionary, or None if not found.
        """
        profile_filepath = os.path.join(BRAINS_DIR, f"{profile_name}.json")
        if not os.path.exists(profile_filepath):
            print(f"Error: Brain profile '{profile_name}' not found at {profile_filepath}.")
            return None

        try:
            with open(profile_filepath, 'r') as f:
                self.loaded_brain_profile = json.load(f)
                print(f"Brain profile '{profile_name}' loaded successfully.")
                return self.loaded_brain_profile
        except json.JSONDecodeError as e:
            print(f"Error decoding brain profile '{profile_name}': {e}")
            return None
        except IOError as e:
            print(f"Error reading brain profile '{profile_name}': {e}")
            return None

    def get_loaded_profile_config(self) -> dict | None:
        """
        Returns the configuration of the currently loaded brain profile.
        """
        return self.loaded_brain_profile

    def list_available_profiles(self) -> list:
        """
        Lists all available brain profiles in the 'brains' directory.

        Returns:
            list: A list of available brain profile names (without .json extension).
        """
        profiles = []
        for filename in os.listdir(BRAINS_DIR):
            if filename.endswith(".json"):
                profiles.append(os.path.splitext(filename)[0])
        print(f"Available brain profiles: {profiles}")
        return profiles

    def delete_brain_profile(self, profile_name: str) -> bool:
        """
        Deletes a specified brain profile file.

        Args:
            profile_name (str): The name of the brain profile to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        profile_filepath = os.path.join(BRAINS_DIR, f"{profile_name}.json")
        if not os.path.exists(profile_filepath):
            print(f"Error: Brain profile '{profile_name}' not found for deletion.")
            return False
        try:
            os.remove(profile_filepath)
            print(f"Brain profile '{profile_name}' deleted successfully.")
            return True
        except OSError as e:
            print(f"Error deleting brain profile '{profile_name}': {e}")
            return False

# Example Usage (for testing purposes)
if __name__ == "__main__":
    architect = BrainArchitect()

    # 1. List initial profiles
    print("\n--- Listing initial profiles ---")
    architect.list_available_profiles()

    # 2. Create a new brain profile
    print("\n--- Creating 'Standard_AI' profile ---")
    standard_config = {
        "ere_core": {"num_emotions": 5, "initial_decay_rate": 0.01},
        "virem_vault": {"encryption_enabled": True},
        "mood_tracker": {"decay_rate": 0.005},
        "body_controller": {"simulation_mode": True}
    }
    architect.create_brain_profile("Standard_AI", standard_config, "A general-purpose AI profile.")

    # 3. Create another brain profile
    print("\n--- Creating 'Optimistic_AI' profile ---")
    optimistic_config = {
        "ere_core": {"num_emotions": 5, "initial_decay_rate": 0.005}, # Slower decay for positive emotions
        "virem_vault": {"encryption_enabled": True},
        "mood_tracker": {"decay_rate": 0.002, "mood_thresholds": {"positive": 0.5, "neutral": 0.3, "negative": 0.1}}, # Easier to be positive
        "body_controller": {"simulation_mode": True}
    }
    architect.create_brain_profile("Optimistic_AI", optimistic_config, "An AI profile with a positive bias.")

    # 4. List profiles again
    print("\n--- Listing profiles after creation ---")
    architect.list_available_profiles()

    # 5. Load a brain profile
    print("\n--- Loading 'Standard_AI' profile ---")
    loaded_profile = architect.load_brain_profile("Standard_AI")
    if loaded_profile:
        print("Loaded profile details:", loaded_profile)
        print("Modules config:", architect.get_loaded_profile_config().get("modules"))

    # 6. Attempt to load a non-existent profile
    print("\n--- Attempting to load 'NonExistent_AI' profile ---")
    architect.load_brain_profile("NonExistent_AI")

    # 7. Delete a brain profile
    print("\n--- Deleting 'Optimistic_AI' profile ---")
    architect.delete_brain_profile("Optimistic_AI")

    # 8. List profiles one last time
    print("\n--- Listing profiles after deletion ---")
    architect.list_available_profiles()
