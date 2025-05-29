import numpy as np
import json
import os
from datetime import datetime

# Define the path for the ERE weight log
LOG_DIR = "logs"
ERE_WEIGHT_LOG_FILE = os.path.join(LOG_DIR, "ere_weight_log.jsonl")

class SoftMemoryMap:
    """
    Manages ERE (Emotional Resonance Engine) weights and emotion resonance mapping.
    This class simulates a 'soft memory' where emotional states are represented
    by numerical weights that can be updated based on interactions.
    """

    def __init__(self, num_emotions: int = 5, initial_decay_rate: float = 0.01):
        """
        Initializes the SoftMemoryMap.

        Args:
            num_emotions (int): The number of distinct emotional dimensions.
                                For example, 5 could represent joy, sadness, anger, fear, surprise.
            initial_decay_rate (float): The rate at which emotional weights naturally decay over time.
        """
        if num_emotions <= 0:
            print("Warning: num_emotions should be a positive integer. Setting to default 5.")
            num_emotions = 5
        if not (0 <= initial_decay_rate <= 1):
            print("Warning: initial_decay_rate should be between 0 and 1. Setting to default 0.01.")
            initial_decay_rate = 0.01

        self.num_emotions = num_emotions
        # Emotional weights, initialized to a neutral state (e.g., 0.5 for each emotion)
        self.ere_weights = np.full(num_emotions, 0.5)
        self.decay_rate = initial_decay_rate
        self.emotion_labels = [f"emotion_{i+1}" for i in range(num_emotions)] # Example labels

        # Ensure the log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        print(f"SoftMemoryMap initialized with {self.num_emotions} emotions and decay rate {self.decay_rate}.")

    def update_ere_weights(self, emotional_input: np.ndarray, interaction_strength: float = 1.0):
        """
        Updates the ERE weights based on new emotional input.

        Args:
            emotional_input (np.ndarray): A numpy array representing the emotional impact
                                          of the current interaction. Should have the same
                                          dimension as self.num_emotions.
                                          Values typically range from -1 (negative impact) to 1 (positive impact).
            interaction_strength (float): A multiplier indicating how strongly this interaction
                                          affects the emotional weights.
        """
        if not isinstance(emotional_input, np.ndarray) or emotional_input.shape != (self.num_emotions,):
            print(f"Error: emotional_input must be a numpy array of shape ({self.num_emotions},).")
            return

        # Apply decay to existing weights
        self.ere_weights = self.ere_weights * (1 - self.decay_rate)

        # Apply new emotional input, capped between 0 and 1
        # We use a simple additive model here, but more complex models could be used
        self.ere_weights = np.clip(self.ere_weights + (emotional_input * interaction_strength), 0, 1)
        print(f"ERE weights updated: {self.ere_weights}")
        self._log_ere_weights()

    def get_current_ere_state(self) -> dict:
        """
        Returns the current emotional state (ERE weights) as a dictionary.

        Returns:
            dict: A dictionary mapping emotion labels to their current weights.
        """
        return dict(zip(self.emotion_labels, self.ere_weights.tolist()))

    def _log_ere_weights(self):
        """
        Appends the current ERE weights to the log file.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ere_weights": self.ere_weights.tolist(),
            "emotion_labels": self.emotion_labels
        }
        try:
            with open(ERE_WEIGHT_LOG_FILE, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            print(f"Logged ERE weights to {ERE_WEIGHT_LOG_FILE}")
        except IOError as e:
            print(f"Error writing to ERE weight log file: {e}")

    def map_input_to_emotion(self, text_input: str) -> np.ndarray:
        """
        A placeholder function to simulate mapping a text input to an emotional vector.
        In a real AI, this would involve NLP, sentiment analysis, and complex emotional modeling.

        Args:
            text_input (str): The input text to be analyzed for emotional content.

        Returns:
            np.ndarray: A numpy array representing the emotional impact of the text.
                        Its shape should match self.num_emotions.
        """
        # This is a simplified example. In a real system, this would be much more complex.
        # For demonstration, let's assume certain keywords trigger specific emotions.
        emotional_vector = np.zeros(self.num_emotions)
        text_input_lower = text_input.lower()

        if "happy" in text_input_lower or "joy" in text_input_lower:
            emotional_vector[0] = 0.2 # Positive impact on 'joy' emotion
        if "sad" in text_input_lower or "unhappy" in text_input_lower:
            emotional_vector[1] = 0.2 # Positive impact on 'sadness' emotion
        if "angry" in text_input_lower or "frustrated" in text_input_lower:
            emotional_vector[2] = 0.2 # Positive impact on 'anger' emotion
        if "scared" in text_input_lower or "fear" in text_input_lower:
            emotional_vector[3] = 0.2 # Positive impact on 'fear' emotion
        if "surprise" in text_input_lower or "unexpected" in text_input_lower:
            emotional_vector[4] = 0.2 # Positive impact on 'surprise' emotion

        # Normalize the vector to ensure values are within a reasonable range for update
        # For simplicity, if sum is greater than 1, scale it down
        if np.sum(emotional_vector) > 1:
            emotional_vector = emotional_vector / np.sum(emotional_vector)

        return emotional_vector

# Example Usage (for testing purposes, not part of the class itself)
if __name__ == "__main__":
    memory_map = SoftMemoryMap(num_emotions=5)
    print("Initial ERE State:", memory_map.get_current_ere_state())

    # Simulate an interaction
    print("\nSimulating a 'happy' interaction:")
    input_vector = memory_map.map_input_to_emotion("I feel very happy today!")
    memory_map.update_ere_weights(input_vector, interaction_strength=0.5)
    print("Current ERE State after happy interaction:", memory_map.get_current_ere_state())

    print("\nSimulating a 'sad' interaction:")
    input_vector = memory_map.map_input_to_emotion("This is a sad situation.")
    memory_map.update_ere_weights(input_vector, interaction_strength=0.7)
    print("Current ERE State after sad interaction:", memory_map.get_current_ere_state())

    print("\nSimulating a neutral interaction (decay only):")
    memory_map.update_ere_weights(np.zeros(5), interaction_strength=0) # No new input, just decay
    print("Current ERE State after neutral interaction:", memory_map.get_current_ere_state())
