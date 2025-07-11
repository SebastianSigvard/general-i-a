"""
Validation utilities for Generala game
"""
from typing import List


def validate_dice_list(dice: List[int], allow_empty: bool = False) -> None:
    """Validate a list of dice values"""
    if not allow_empty and not dice:
        raise ValueError("Dice list cannot be empty")
    
    for die in dice:
        if not isinstance(die, int) or die < 1 or die > 6:
            raise ValueError(f"All dice values must be integers between 1 and 6, got {die}")


def validate_dice_count(dice: List[int], expected_count: int) -> None:
    """Validate dice list has expected number of dice"""
    if len(dice) != expected_count:
        raise ValueError(f"Must have exactly {expected_count} dice, got {len(dice)}")


def validate_roll_number(roll_number: int, max_rolls: int) -> None:
    """Validate roll number is within valid range"""
    if roll_number <= 0 or roll_number > max_rolls:
        raise ValueError(f"Roll number must be between 1 and {max_rolls}, got {roll_number}")


def validate_held_dice_count(held: List[int], max_dice: int) -> None:
    """Validate held dice count doesn't exceed maximum"""
    if len(held) > max_dice:
        raise ValueError(f"Cannot hold more than {max_dice} dice, got {len(held)}")


def validate_player_names(player_names: List[str]) -> None:
    """Validate player names list"""
    if not player_names:
        raise ValueError("Player list cannot be empty")
    
    for i, name in enumerate(player_names):
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Player name at index {i} must be a non-empty string, got {repr(name)}")