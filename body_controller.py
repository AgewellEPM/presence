import time
import json

class BodyController:
    """
    Simulates the AI's ability to interact with a physical or simulated "body"
    or external actuators. This class translates AI decisions into actionable outputs.
    """

    def __init__(self, simulation_mode: bool = True):
        """
        Initializes the BodyController.

        Args:
            simulation_mode (bool): If True, operations are simulated (e.g., print statements).
                                    If False, it would attempt to connect to real hardware/APIs.
        """
        self.simulation_mode = simulation_mode
        self.last_action_time = time.time()
        self.action_history = [] # To log simulated actions

        print(f"BodyController initialized. Simulation Mode: {self.simulation_mode}")

    def _log_action(self, action_type: str, details: dict):
        """Logs a simulated or real action."""
        log_entry = {
            "timestamp": time.time(),
            "action_type": action_type,
            "details": details
        }
        self.action_history.append(log_entry)
        if self.simulation_mode:
            print(f"[BodyController - SIM] Action: {action_type}, Details: {details}")
        else:
            # In a real scenario, this would log to a persistent file or monitoring system
            print(f"[BodyController - REAL] Action: {action_type}, Details: {details}")

    def perform_action(self, action_type: str, parameters: dict = None) -> bool:
        """
        Performs a specified action.

        Args:
            action_type (str): The type of action to perform (e.g., "speak", "move", "display_image").
            parameters (dict): A dictionary of parameters relevant to the action.

        Returns:
            bool: True if the action was successfully initiated, False otherwise.
        """
        parameters = parameters if parameters is not None else {}
        self.last_action_time = time.time()

        if action_type == "speak":
            text_to_speak = parameters.get("text", "Hello, I am Presence AI.")
            if self.simulation_mode:
                self._log_action("speak", {"text": text_to_speak})
                # In a real system: call text-to-speech API or hardware
            else:
                # Placeholder for real TTS integration
                # Example: tts_engine.speak(text_to_speak)
                self._log_action("speak", {"text": text_to_speak, "status": "attempted_real"})
            return True
        elif action_type == "move":
            direction = parameters.get("direction", "forward")
            distance = parameters.get("distance", 1.0)
            if self.simulation_mode:
                self._log_action("move", {"direction": direction, "distance": distance})
                # In a real system: send commands to robot motors
            else:
                # Placeholder for real robotics integration
                # Example: robot_api.move(direction, distance)
                self._log_action("move", {"direction": direction, "distance": distance, "status": "attempted_real"})
            return True
        elif action_type == "display_visual":
            content_type = parameters.get("content_type", "text") # "text", "image_url", "emoji"
            content = parameters.get("content", "No content.")
            if self.simulation_mode:
                self._log_action("display_visual", {"content_type": content_type, "content": content})
                # In a real system: update a display screen
            else:
                # Placeholder for real display integration
                # Example: display_api.show(content_type, content)
                self._log_action("display_visual", {"content_type": content_type, "content": content, "status": "attempted_real"})
            return True
        elif action_type == "express_emotion":
            emotion = parameters.get("emotion", "neutral")
            intensity = parameters.get("intensity", 0.5) # 0.0 to 1.0
            if self.simulation_mode:
                self._log_action("express_emotion", {"emotion": emotion, "intensity": intensity})
                # In a real system: change facial expression on avatar, adjust vocal tone
            else:
                # Placeholder for real emotional expression integration
                self._log_action("express_emotion", {"emotion": emotion, "intensity": intensity, "status": "attempted_real"})
            return True
        else:
            print(f"Warning: Unknown action type '{action_type}'.")
            return False

    def get_action_history(self) -> list:
        """Returns the history of performed actions."""
        return self.action_history

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Test in simulation mode
    print("\n--- Testing BodyController in Simulation Mode ---")
    sim_controller = BodyController(simulation_mode=True)
    sim_controller.perform_action("speak", {"text": "Hello, world! I am in simulation mode."})
    sim_controller.perform_action("move", {"direction": "left", "distance": 0.5})
    sim_controller.perform_action("display_visual", {"content_type": "emoji", "content": "😊"})
    sim_controller.perform_action("express_emotion", {"emotion": "joy", "intensity": 0.8})
    sim_controller.perform_action("unknown_action")
    print("\nSimulated Action History:")
    for action in sim_controller.get_action_history():
        print(f"  - {action['action_type']} at {datetime.fromtimestamp(action['timestamp']).strftime('%H:%M:%S')}: {action['details']}")

    # Test in (conceptual) real mode
    print("\n--- Testing BodyController in (Conceptual) Real Mode ---")
    real_controller = BodyController(simulation_mode=False)
    real_controller.perform_action("speak", {"text": "Initiating real-world speech."})
    real_controller.perform_action("move", {"direction": "forward", "distance": 2.0})
    print("\nReal Mode Action History (conceptual):")
    for action in real_controller.get_action_history():
        print(f"  - {action['action_type']} at {datetime.fromtimestamp(action['timestamp']).strftime('%H:%M:%S')}: {action['details']}")
