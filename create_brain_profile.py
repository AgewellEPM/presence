import json
import os
from datetime import datetime
from brain_architect import BrainArchitect # Import the BrainArchitect class

# This script is a utility to simplify the creation of brain profiles.
# It leverages the functionality provided by BrainArchitect.

def main():
    """
    Main function to run the brain profile creation utility.
    """
    architect = BrainArchitect()
    print("\n--- Create New Brain Profile ---")

    profile_name = input("Enter a unique name for the new brain profile: ").strip()
    if not profile_name:
        print("Profile name cannot be empty. Exiting.")
        return

    description = input("Enter a brief description for this profile (optional): ").strip()

    print("\nNow, define the configuration for each module.")
    print("You will be prompted for common parameters. For advanced settings, you might need to edit the JSON directly.")

    modules_config = {}

    # --- ERE Core Configuration ---
    print("\n--- ERE Core Settings ---")
    try:
        num_emotions = int(input("Number of emotional dimensions (e.g., 5 for joy, sadness, anger, fear, surprise) [default: 5]: ") or "5")
        initial_decay_rate = float(input("Initial decay rate for emotional weights (0.0 - 1.0, e.g., 0.01) [default: 0.01]: ") or "0.01")
        modules_config["ere_core"] = {
            "num_emotions": num_emotions,
            "initial_decay_rate": initial_decay_rate
        }
    except ValueError:
        print("Invalid input for ERE Core settings. Using defaults.")
        modules_config["ere_core"] = {"num_emotions": 5, "initial_decay_rate": 0.01}


    # --- VIREM Vault Configuration ---
    print("\n--- VIREM Vault Settings ---")
    try:
        encryption_enabled_str = input("Enable memory encryption? (yes/no) [default: yes]: ").lower()
        encryption_enabled = encryption_enabled_str == 'yes' or encryption_enabled_str == ''
        modules_config["virem_vault"] = {
            "encryption_enabled": encryption_enabled
        }
    except ValueError:
        print("Invalid input for VIREM Vault settings. Using defaults.")
        modules_config["virem_vault"] = {"encryption_enabled": True}

    # --- Mood Tracker Configuration ---
    print("\n--- Mood Tracker Settings ---")
    try:
        mood_decay_rate = float(input("Mood decay rate (0.0 - 1.0, e.g., 0.005) [default: 0.005]: ") or "0.005")
        modules_config["mood_tracker"] = {
            "decay_rate": mood_decay_rate
        }
        # Optional: Add more complex mood thresholds here if desired, or leave for manual JSON edit
    except ValueError:
        print("Invalid input for Mood Tracker settings. Using defaults.")
        modules_config["mood_tracker"] = {"decay_rate": 0.005}

    # --- Body Controller Configuration ---
    print("\n--- Body Controller Settings ---")
    try:
        simulation_mode_str = input("Run Body Controller in simulation mode? (yes/no) [default: yes]: ").lower()
        simulation_mode = simulation_mode_str == 'yes' or simulation_mode_str == ''
        modules_config["body_controller"] = {
            "simulation_mode": simulation_mode
        }
    except ValueError:
        print("Invalid input for Body Controller settings. Using defaults.")
        modules_config["body_controller"] = {"simulation_mode": True}

    # --- Finalize and Create ---
    print("\n--- Creating Brain Profile ---")
    if architect.create_brain_profile(profile_name, modules_config, description):
        print(f"\nBrain profile '{profile_name}' created successfully!")
        print(f"You can find it in the '{BrainArchitect.BRAINS_DIR}' directory.")
    else:
        print("\nFailed to create brain profile.")

if __name__ == "__main__":
    main()
