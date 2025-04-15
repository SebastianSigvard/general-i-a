from enum import Enum, auto
from collections import defaultdict
import random
from typing import List, Optional, Dict, Union


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
        return held + [
            random.randint(1, 6) for _ in range(GeneralaRules.DICE_COUNT - len(held))
        ]

    @staticmethod
    def score_category(
        category: GeneralaCategory, dice: List[int], roll_number: int = 1
    ) -> Union[int, str]:
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
                25 + bonus if sorted(dice) in ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6]) else 0
            )
        elif category == GeneralaCategory.FULL:
            return 35 + bonus if sorted(counts.values())[-2:] == [2, 3] else 0
        elif category == GeneralaCategory.POKER:
            return 45 + bonus if 4 in counts.values() else 0
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
