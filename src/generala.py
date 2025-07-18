from enum import Enum, auto
from collections import defaultdict
import random
from typing import List, Optional, Dict, Union

from validation import (
    validate_dice_list,
    validate_dice_count,
    validate_roll_number,
    validate_held_dice_count,
    validate_player_names,
)


class GeneralaAction(Enum):
    ROLL = "roll"
    HOLD = "hold"
    SCORE = "score"
    END_TURN = "end_turn"


class GeneralaCategory(Enum):
    ONES = "ones"
    TWOS = "twos"
    THREES = "threes"
    FOURS = "fours"
    FIVES = "fives"
    SIXES = "sixes"
    ESCALERA = "escalera"
    FULL = "full"
    POKER = "poker"
    GENERALA = "generala"
    DOUBLE_GENERALA = "double_generala"


class GeneralaRules:
    DICE_COUNT = 5
    MAX_ROLLS = 3
    CATEGORIES = [cat for cat in GeneralaCategory]

    @staticmethod
    def roll_dice(held: Optional[List[int]] = None) -> List[int]:
        if held is None:
            held = []
        
        # Input validation
        validate_held_dice_count(held, GeneralaRules.DICE_COUNT)
        validate_dice_list(held, allow_empty=True)
        
        return held + [
            random.randint(1, 6) for _ in range(GeneralaRules.DICE_COUNT - len(held))
        ]

    @staticmethod
    def score_category(
        category: GeneralaCategory, dice: List[int], roll_number: int = 1
    ) -> Union[int, str]:
        # Input validation
        validate_dice_list(dice)
        validate_dice_count(dice, GeneralaRules.DICE_COUNT)
        validate_roll_number(roll_number, GeneralaRules.MAX_ROLLS)
        
        counts = {i: dice.count(i) for i in range(1, 7)}
        bonus = (
            5
            if roll_number == 1
            and category
            in [
                GeneralaCategory.ESCALERA,
                GeneralaCategory.FULL,
                GeneralaCategory.POKER,
            ]
            else 0
        )
        if category == GeneralaCategory.ONES:
            return counts[1] * 1
        elif category == GeneralaCategory.TWOS:
            return counts[2] * 2
        elif category == GeneralaCategory.THREES:
            return counts[3] * 3
        elif category == GeneralaCategory.FOURS:
            return counts[4] * 4
        elif category == GeneralaCategory.FIVES:
            return counts[5] * 5
        elif category == GeneralaCategory.SIXES:
            return counts[6] * 6
        elif category == GeneralaCategory.ESCALERA:
            return (
                20 + bonus if sorted(dice) in ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6]) else 0
            )
        elif category == GeneralaCategory.FULL:
            return 30 + bonus if sorted(counts.values())[-2:] == [2, 3] else 0
        elif category == GeneralaCategory.POKER:
            return 40 + bonus if 4 in counts.values() else 0
        elif category == GeneralaCategory.GENERALA:
            if 5 in counts.values():
                if roll_number == 1:
                    return "WIN"
                return 50
            return 0
        elif category == GeneralaCategory.DOUBLE_GENERALA:
            return 100 if 5 in counts.values() else 0
        return 0


class GeneralaScoreBoard:
    def __init__(self) -> None:
        self.scores: Dict[GeneralaCategory, Optional[int]] = {
            cat: None for cat in GeneralaRules.CATEGORIES
        }

    def set_score(self, category: GeneralaCategory, score: int) -> None:
        if self.scores[category] is None:
            self.scores[category] = score
        else:
            raise ValueError(f"Category '{category}' already scored.")

    def total_score(self) -> int:
        return sum(score for score in self.scores.values() if score is not None)

    def __str__(self) -> str:
        return "\n".join(
            f"{cat.value}: {score if score is not None else '-'}"
            for cat, score in self.scores.items()
        )


class GeneralaGame:
    def __init__(self, player_names: List[str]):
        validate_player_names(player_names)
        self.player_names = player_names
        self.scoreboards = [GeneralaScoreBoard() for _ in player_names]
        self.current_player = 0
        self.round = 0
        self.dice: List[int] = []
        self.held: List[int] = []
        self.roll_number = 1
        self.finished = False
        self.num_categories = len(GeneralaRules.CATEGORIES)

    def start_turn(self):
        self.dice = GeneralaRules.roll_dice()
        self.held = []
        self.roll_number = 1

    def roll(self, held: Optional[List[int]] = None):
        if self.roll_number >= GeneralaRules.MAX_ROLLS:
            raise Exception("No rolls left")
        self.held = held if held is not None else []
        self.dice = GeneralaRules.roll_dice(self.held)
        self.roll_number += 1
        return self.dice

    def can_score(self):
        return self.roll_number > 0

    def score(self, category: GeneralaCategory):
        if not self.can_score():
            raise ValueError("Cannot score before making at least one roll")
        
        score = GeneralaRules.score_category(category, self.dice, self.roll_number)
        if score == "WIN":
            self.scoreboards[self.current_player].set_score(category, 50)
            self.finished = True
            return "WIN"
        elif isinstance(score, int):
            self.scoreboards[self.current_player].set_score(category, score)
            return score
        else:
            raise Exception(f"Invalid score: {score}")

    def next_player(self):
        self.current_player = (self.current_player + 1) % len(self.player_names)
        if self.current_player == 0:
            self.round += 1
        if self.round >= self.num_categories:
            self.finished = True
        self.start_turn()

    def get_winner(self):
        totals = [sb.total_score() for sb in self.scoreboards]
        max_score = max(totals)
        winners = [self.player_names[i] for i, t in enumerate(totals) if t == max_score]
        return winners, totals
