import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.generala import GeneralaGame, GeneralaRules


def test_roll_raises_when_max_rolls_reached():
    game = GeneralaGame(["p1"])
    game.start_turn()
    # Roll until reaching the maximum allowed rolls
    while game.roll_number < GeneralaRules.MAX_ROLLS:
        game.roll()
    assert game.roll_number == GeneralaRules.MAX_ROLLS
    with pytest.raises(Exception):
        game.roll()
