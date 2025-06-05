import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.generala import (
    GeneralaGame,
    GeneralaRules,
    GeneralaCategory,
    GeneralaScoreBoard,
)


@pytest.mark.parametrize(
    "category,dice,roll,expected",
    [
        (GeneralaCategory.ONES, [1, 1, 2, 3, 4], 1, 2),
        (GeneralaCategory.TWOS, [2, 2, 2, 5, 6], 2, 6),
        (GeneralaCategory.THREES, [3, 3, 3, 1, 1], 1, 9),
        (GeneralaCategory.FOURS, [4, 4, 2, 2, 2], 1, 8),
        (GeneralaCategory.FIVES, [5, 5, 5, 5, 1], 3, 20),
        (GeneralaCategory.SIXES, [6, 6, 6, 1, 2], 1, 18),
        (GeneralaCategory.ESCALERA, [1, 2, 3, 4, 5], 1, 30),
        (GeneralaCategory.ESCALERA, [2, 3, 4, 5, 6], 3, 25),
        (GeneralaCategory.FULL, [2, 2, 3, 3, 3], 1, 40),
        (GeneralaCategory.FULL, [2, 2, 2, 3, 3], 2, 35),
        (GeneralaCategory.POKER, [4, 4, 4, 4, 1], 1, 50),
        (GeneralaCategory.POKER, [4, 4, 4, 4, 1], 2, 45),
        (GeneralaCategory.GENERALA, [5, 5, 5, 5, 5], 1, "WIN"),
        (GeneralaCategory.GENERALA, [5, 5, 5, 5, 5], 3, 50),
        (GeneralaCategory.GENERALA, [1, 2, 3, 4, 5], 1, 0),
        (GeneralaCategory.DOUBLE_GENERALA, [6, 6, 6, 6, 6], 2, 100),
        (GeneralaCategory.DOUBLE_GENERALA, [1, 2, 3, 4, 5], 1, 0),
    ],
)
def test_score_category(category, dice, roll, expected):
    assert GeneralaRules.score_category(category, dice, roll) == expected


def test_scoreboard_set_score_and_total():
    sb = GeneralaScoreBoard()
    sb.set_score(GeneralaCategory.ONES, 3)
    with pytest.raises(ValueError):
        sb.set_score(GeneralaCategory.ONES, 1)
    assert sb.total_score() == 3
    result_str = str(sb)
    assert "ones" in result_str


def test_game_playthrough(monkeypatch):
    def fake_roll(held=None):
        if held is None:
            held = []
        return held + [1] * (GeneralaRules.DICE_COUNT - len(held))

    monkeypatch.setattr(GeneralaRules, "roll_dice", fake_roll)
    game = GeneralaGame(["p1", "p2"])
    game.num_categories = 1
    game.start_turn()

    game.roll([game.dice[0]])
    assert game.roll_number == 2
    assert game.dice == [1, 1, 1, 1, 1]
    assert game.can_score()

    result = game.score(GeneralaCategory.GENERALA)
    assert result == 50
    assert game.scoreboards[0].scores[GeneralaCategory.GENERALA] == 50

    game.next_player()
    assert game.current_player == 1
    assert game.roll_number == 1

    game.roll()
    res2 = game.score(GeneralaCategory.ONES)
    assert res2 == 5

    game.next_player()
    assert game.finished

    winners, totals = game.get_winner()
    assert winners == ["p1"]
    assert totals == [50, 5]


def test_roll_raises_when_max_rolls_reached():
    game = GeneralaGame(["p1"])
    game.start_turn()
    # Roll until reaching the maximum allowed rolls
    while game.roll_number < GeneralaRules.MAX_ROLLS:
        game.roll()
    assert game.roll_number == GeneralaRules.MAX_ROLLS
    with pytest.raises(Exception):
        game.roll()
