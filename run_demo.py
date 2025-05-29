import json
import os
import time
import numpy as np

# Import core components
from ere_core.soft_memory_map import SoftMemoryMap
from virem_vault.driver import VIREMVaultDriver

# Define paths
CONFIG_FILE = "config/config.json"
SCRATCH_MEMORY_CONCEPT = "Conceptual RAM-only memory, no physical files."

class PresenceAIDemo:
    """
    Entry point for running the AI demo.
    This class orchestrates the interaction between the ERE core and the VIREM vault,
    simulating an AI that processes emotional input and manages persistent memory.
    """

    def __init__(self):
        """
        Initializes the AI demo, loading configuration and setting up components.
        """
        self.config = self._load_config()
        self.persistent_memory_enabled = self.config.get("modes", {}).get("persistent_memory", True)
        self.debug_mode = self.config.get("modes", {}).get("debug_mode", False)

        self.soft_memory_map = SoftMemoryMap(num_emotions=5) # Initialize with 5 emotional dimensions
        self.virem_vault = VIREMVaultDriver()

        print("\n--- Presence AI Demo Initialized ---")
        print(f"Persistent Memory Enabled: {self.persistent_memory_enabled}")
        print(f"Debug Mode: {self.debug_mode}")
        print(f"Scratch Memory: {SCRATCH_MEMORY_CONCEPT}")

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

    def _simulate_user_interaction(self, prompt: str) -> dict:
        """
        Simulates a user interaction and generates a unique interaction ID.
        In a real system, this would involve receiving actual user input.
        """
        interaction_id = f"interaction_{int(time.time())}_{np.random.randint(1000, 9999)}"
        print(f"\nUser says: '{prompt}' (Interaction ID: {interaction_id})")
        return {"id": interaction_id, "text": prompt}

    def run_interaction_loop(self):
        """
        Runs the main interaction loop of the AI demo.
        """
        print("\n--- Starting AI Interaction Loop (Type 'exit' to quit) ---")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting Presence AI Demo. Goodbye!")
                break

            # 1. Simulate user interaction
            interaction_details = self._simulate_user_interaction(user_input)
            interaction_id = interaction_details["id"]
            interaction_text = interaction_details["text"]

            # 2. Process emotional input via ERE Core (soft_memory_map)
            emotional_vector = self.soft_memory_map.map_input_to_emotion(interaction_text)
            self.soft_memory_map.update_ere_weights(emotional_vector, interaction_strength=0.6) # Adjust strength as needed

            current_ere_state = self.soft_memory_map.get_current_ere_state()
            print(f"AI's current emotional state: {current_ere_state}")

            # 3. Store interaction details in VIREM Vault (persistent memory) if enabled
            if self.persistent_memory_enabled:
                memory_data = {
                    "interaction_id": interaction_id,
                    "user_input": interaction_text,
                    "ere_state_after_interaction": current_ere_state,
                    "timestamp": time.time()
                }
                if self.virem_vault.store_memory(interaction_id, memory_data):
                    print(f"Interaction '{interaction_id}' stored in VIREM Vault.")
                else:
                    print(f"Failed to store interaction '{interaction_id}' in VIREM Vault.")
            else:
                print("Persistent memory is disabled. Interaction not stored.")

            # 4. Simulate AI response (placeholder)
            # In a real AI, this would involve generating a response based on emotional state,
            # context, and potentially retrieving past memories.
            ai_response = f"I noted your input. My current emotional resonance is based on our conversation. (Debug: {self.debug_mode})"
            print(f"AI: {ai_response}")

            # Optional: Retrieve a memory to demonstrate vault functionality
            if self.debug_mode and self.persistent_memory_enabled:
                retrieved_memory = self.virem_vault.retrieve_memory(interaction_id)
                if retrieved_memory:
                    print(f"Debug: Retrieved memory for '{interaction_id}': {retrieved_memory.get('user_input')[:30]}...")
                else:
                    print(f"Debug: Could not retrieve memory for '{interaction_id}'.")

# Main execution block
if __name__ == "__main__":
    # Ensure config.json exists before running the demo
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found. Please run the previous step to create it.")
        # Create a dummy config.json for demonstration if it doesn't exist
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                "vault": {"location": "./vault_data", "encryption_enabled": True},
                "modes": {"persistent_memory": True, "debug_mode": False},
                "keys": {"example_api_key": "YOUR_API_KEY_HERE"}
            }, f, indent=2)
        print(f"A dummy {CONFIG_FILE} has been created. Please review it.")
        # Exit or allow user to re-run after creating config
        # For now, let's proceed with the dummy config for demonstration
        # exit() # Uncomment this line if you want to force user to create config first

    demo = PresenceAIDemo()
    demo.run_interaction_loop()
