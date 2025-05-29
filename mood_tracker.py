import numpy as np
import time
from datetime import datetime
import json
import os

# Assuming ere_core.soft_memory_map is available for current emotional state
# from ere_core.soft_memory_map import SoftMemoryMap # Not directly imported here to avoid circular dependency,
                                                    # but MoodTracker would likely receive ERE state as input.

class MoodTracker:
    """
    Tracks and manages the AI's overall mood based on aggregated emotional states
    and historical interactions. This goes beyond immediate emotional weights
    to a more generalized, long-term mood state.
    """

    def __init__(self, decay_rate: float = 0.005, mood_thresholds: dict = None):
        """
        Initializes the MoodTracker.

        Args:
            decay_rate (float): The rate at which accumulated emotional impact on mood decays.
                                A lower rate means mood changes more slowly.
            mood_thresholds (dict): Optional dictionary defining thresholds for different mood states.
                                    Example: {"positive": 0.7, "neutral": 0.4, "negative": 0.1}
        """
        if not (0 <= decay_rate <= 1):
            print("Warning: decay_rate should be between 0 and 1. Setting to default 0.005.")
            decay_rate = 0.005

        self.decay_rate = decay_rate
        # Mood is represented as a single float, typically between 0 and 1
        # 0.5 could be neutral, >0.5 positive, <0.5 negative
        self.current_mood_score = 0.5
        self.last_update_time = time.time() # Timestamp of the last mood update

        # Default mood thresholds if not provided
        self.mood_thresholds = mood_thresholds if mood_thresholds is not None else {
            "very_positive": 0.8,
            "positive": 0.6,
            "neutral": 0.4,
            "negative": 0.2,
            "very_negative": 0.0
        }
        # Sort thresholds for easier lookup (descending order of score)
        self.sorted_mood_thresholds = sorted(self.mood_thresholds.items(), key=lambda item: item[1], reverse=True)

        print(f"MoodTracker initialized with decay rate {self.decay_rate}. Initial mood score: {self.current_mood_score}")

    def update_mood(self, ere_weights: dict, interaction_intensity: float = 1.0):
        """
        Updates the overall mood based on the current ERE weights and interaction intensity.

        Args:
            ere_weights (dict): The current emotional resonance engine weights (e.g., from SoftMemoryMap).
                                Expected format: {"emotion_1": 0.7, "emotion_2": 0.3, ...}
            interaction_intensity (float): A multiplier indicating how strongly the current interaction
                                           influences the mood.
        """
        if not isinstance(ere_weights, dict):
            print("Error: ere_weights must be a dictionary.")
            return

        # Calculate time elapsed since last update for decay
        current_time = time.time()
        time_delta = current_time - self.last_update_time
        self.last_update_time = current_time

        # Apply decay to the current mood score
        # Mood decays towards neutral (0.5)
        self.current_mood_score += (0.5 - self.current_mood_score) * (1 - np.exp(-self.decay_rate * time_delta))

        # Aggregate emotional weights to influence mood
        # This is a simplified aggregation. A more complex model might use specific
        # emotional valences (e.g., joy is positive, sadness is negative).
        positive_emotions_sum = sum(v for k, v in ere_weights.items() if "positive" in k or "joy" in k or "surprise" in k)
        negative_emotions_sum = sum(v for k, v in ere_weights.items() if "negative" in k or "sadness" in k or "anger" in k or "fear" in k)

        # Simple net emotional impact
        net_emotional_impact = (positive_emotions_sum - negative_emotions_sum) * interaction_intensity

        # Adjust mood score based on net emotional impact
        # Normalize impact to a smaller range, e.g., -0.1 to 0.1, to prevent wild swings
        mood_adjustment = np.clip(net_emotional_impact * 0.05, -0.1, 0.1)
        self.current_mood_score = np.clip(self.current_mood_score + mood_adjustment, 0, 1)

        print(f"Mood updated. Current mood score: {self.current_mood_score:.3f}")

    def get_current_mood(self) -> str:
        """
        Returns the current mood state as a descriptive string based on thresholds.

        Returns:
            str: A string describing the current mood (e.g., "positive", "neutral", "negative").
        """
        for mood_label, threshold in self.sorted_mood_thresholds:
            if self.current_mood_score >= threshold:
                return mood_label
        return "undefined" # Should not happen if thresholds cover full range

    def get_mood_score(self) -> float:
        """
        Returns the raw numerical mood score.

        Returns:
            float: The current mood score (typically between 0 and 1).
        """
        return self.current_mood_score

# Example Usage (for testing purposes)
if __name__ == "__main__":
    mood_tracker = MoodTracker()
    print(f"Initial mood: {mood_tracker.get_current_mood()} ({mood_tracker.get_mood_score():.3f})")

    # Simulate some ERE weights (e.g., from SoftMemoryMap)
    # Example 1: Positive emotional input
    print("\n--- Simulating positive emotional input ---")
    positive_ere_weights = {"emotion_1": 0.9, "emotion_2": 0.1, "joy": 0.7, "sadness": 0.1}
    mood_tracker.update_mood(positive_ere_weights, interaction_intensity=0.8)
    print(f"Current mood: {mood_tracker.get_current_mood()} ({mood_tracker.get_mood_score():.3f})")

    # Example 2: Negative emotional input
    print("\n--- Simulating negative emotional input ---")
    negative_ere_weights = {"emotion_1": 0.1, "emotion_2": 0.9, "joy": 0.1, "sadness": 0.7}
    mood_tracker.update_mood(negative_ere_weights, interaction_intensity=0.7)
    print(f"Current mood: {mood_tracker.get_current_mood()} ({mood_tracker.get_mood_score():.3f})")

    # Example 3: Neutral period (decay should bring it closer to 0.5)
    print("\n--- Simulating a neutral period (decay) ---")
    time.sleep(2) # Simulate time passing
    neutral_ere_weights = {"emotion_1": 0.5, "emotion_2": 0.5, "joy": 0.5, "sadness": 0.5}
    mood_tracker.update_mood(neutral_ere_weights, interaction_intensity=0.0) # No new input
    print(f"Current mood: {mood_tracker.get_current_mood()} ({mood_tracker.get_mood_score():.3f})")

    # Example 4: Another positive input
    print("\n--- Simulating another positive input ---")
    another_positive_ere_weights = {"emotion_1": 0.8, "emotion_2": 0.2, "joy": 0.6, "anger": 0.1}
    mood_tracker.update_mood(another_positive_ere_weights, interaction_intensity=0.9)
    print(f"Current mood: {mood_tracker.get_current_mood()} ({mood_tracker.get_mood_score():.3f})")
