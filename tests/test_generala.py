import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from generala import (
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
        (GeneralaCategory.ESCALERA, [1, 2, 3, 4, 5], 1, 25),
        (GeneralaCategory.ESCALERA, [2, 3, 4, 5, 6], 3, 20),
        (GeneralaCategory.FULL, [2, 2, 3, 3, 3], 1, 35),
        (GeneralaCategory.FULL, [2, 2, 2, 3, 3], 2, 30),
        (GeneralaCategory.POKER, [4, 4, 4, 4, 1], 1, 45),
        (GeneralaCategory.POKER, [4, 4, 4, 4, 1], 2, 40),
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


# Edge case tests - these should raise exceptions for proper input validation
def test_score_category_invalid_dice_should_raise():
    """Test that scoring with invalid dice raises exceptions"""
    
    # Empty dice list should raise
    with pytest.raises(ValueError):
        GeneralaRules.score_category(GeneralaCategory.ONES, [], 1)
    
    # Wrong number of dice should raise
    with pytest.raises(ValueError):
        GeneralaRules.score_category(GeneralaCategory.ONES, [1, 1, 1], 1)
    
    with pytest.raises(ValueError):
        GeneralaRules.score_category(GeneralaCategory.ONES, [1, 1, 1, 1, 1, 1], 1)
    
    # Dice with invalid values should raise
    with pytest.raises(ValueError):
        GeneralaRules.score_category(GeneralaCategory.ONES, [0, 1, 2, 3, 4], 1)
    
    with pytest.raises(ValueError):
        GeneralaRules.score_category(GeneralaCategory.ONES, [1, 2, 3, 4, 7], 1)


def test_score_category_invalid_roll_number_should_raise():
    """Test that invalid roll numbers raise exceptions"""
    dice = [1, 2, 3, 4, 5]
    
    # Roll number <= 0 should raise
    with pytest.raises(ValueError):
        GeneralaRules.score_category(GeneralaCategory.ESCALERA, dice, 0)
    
    with pytest.raises(ValueError):
        GeneralaRules.score_category(GeneralaCategory.ESCALERA, dice, -1)
    
    # Roll number > MAX_ROLLS should raise
    with pytest.raises(ValueError):
        GeneralaRules.score_category(GeneralaCategory.ESCALERA, dice, 4)


def test_game_invalid_players_should_raise():
    """Test that invalid player configurations raise exceptions"""
    
    # Empty player list should raise
    with pytest.raises(ValueError):
        GeneralaGame([])
    
    # None player names should raise
    with pytest.raises(ValueError):
        GeneralaGame([None, "player2"])
    
    # Empty string player names should raise  
    with pytest.raises(ValueError):
        GeneralaGame(["", "player2"])


def test_scoring_after_start_turn_is_allowed():
    """Test that scoring after start_turn is allowed (we've already rolled once)"""
    game = GeneralaGame(["p1"])
    game.start_turn()  # This performs the first roll, roll_number = 1
    
    # Should be able to score after start_turn since we've already rolled
    assert game.can_score() == True
    assert game.roll_number == 1  # Confirms we've completed one roll
    
    # Should succeed without raising an exception
    result = game.score(GeneralaCategory.ONES)
    assert isinstance(result, int)  # Should return a score


def test_roll_dice_invalid_held_should_raise():
    """Test that invalid held dice raise exceptions"""
    
    # Hold more dice than DICE_COUNT should raise
    with pytest.raises(ValueError):
        GeneralaRules.roll_dice([1, 2, 3, 4, 5, 6])
    
    # Hold dice with invalid values should raise
    with pytest.raises(ValueError):
        GeneralaRules.roll_dice([0, 2, 3])
    
    with pytest.raises(ValueError):
        GeneralaRules.roll_dice([1, 7, 3])


# Advanced edge case tests
def test_scoreboard_multiple_categories_total():
    """Test total calculation with multiple categories"""
    sb = GeneralaScoreBoard()
    
    # Add scores to multiple categories
    sb.set_score(GeneralaCategory.ONES, 5)
    sb.set_score(GeneralaCategory.TWOS, 10)
    sb.set_score(GeneralaCategory.ESCALERA, 30)
    sb.set_score(GeneralaCategory.GENERALA, 50)
    
    assert sb.total_score() == 95
    
    # Test with zero scores
    sb.set_score(GeneralaCategory.THREES, 0)
    assert sb.total_score() == 95  # Zero should still count


def test_double_generala_after_regular_generala():
    """Test scoring double generala after already having generala"""
    sb = GeneralaScoreBoard()
    
    # First score a regular generala
    sb.set_score(GeneralaCategory.GENERALA, 50)
    
    # Then score a double generala
    sb.set_score(GeneralaCategory.DOUBLE_GENERALA, 100)
    
    assert sb.total_score() == 150
    assert sb.scores[GeneralaCategory.GENERALA] == 50
    assert sb.scores[GeneralaCategory.DOUBLE_GENERALA] == 100


def test_game_winner_with_ties():
    """Test winner determination with tied scores"""
    def fake_roll(held=None):
        if held is None:
            held = []
        return held + [1] * (GeneralaRules.DICE_COUNT - len(held))

    import pytest
    game = GeneralaGame(["p1", "p2", "p3"])
    game.num_categories = 1  # Single round for testing
    
    # Mock dice rolling
    import unittest.mock
    with unittest.mock.patch.object(GeneralaRules, "roll_dice", fake_roll):
        # Player 1 scores
        game.start_turn()
        game.roll()
        game.score(GeneralaCategory.ONES)  # Score: 5
        
        game.next_player()
        # Player 2 scores same
        game.roll()
        game.score(GeneralaCategory.ONES)  # Score: 5
        
        game.next_player()
        # Player 3 scores different
        game.roll()
        game.score(GeneralaCategory.ONES)  # Score: 5
        
        game.next_player()
        assert game.finished
        
        winners, totals = game.get_winner()
        assert len(winners) == 3  # All tied
        assert totals == [5, 5, 5]


def test_multi_round_game_completion():
    """Test a complete multi-round game"""
    def fake_roll_ones(held=None):
        if held is None:
            held = []
        return held + [1] * (GeneralaRules.DICE_COUNT - len(held))
    
    def fake_roll_twos(held=None):
        if held is None:
            held = []
        return held + [2] * (GeneralaRules.DICE_COUNT - len(held))

    import unittest.mock
    game = GeneralaGame(["p1", "p2"])
    game.num_categories = 2  # Two rounds for testing
    
    with unittest.mock.patch.object(GeneralaRules, "roll_dice", fake_roll_ones):
        # Round 1: Player 1
        game.start_turn()
        game.roll()
        game.score(GeneralaCategory.ONES)  # Score: 5
        assert game.round == 0
        assert game.current_player == 0
        
        game.next_player()
        # Round 1: Player 2 
        assert game.current_player == 1  # Should be player 2
        assert game.round == 0  # Round shouldn't advance yet
        game.roll()
        game.score(GeneralaCategory.ONES)  # Score: 5
        
        game.next_player()
        # Now round should advance and return to player 1
        assert game.round == 1  # Should advance round
        assert game.current_player == 0  # Back to player 1
        
    with unittest.mock.patch.object(GeneralaRules, "roll_dice", fake_roll_twos):
        # Round 2: Player 1
        game.roll()
        game.score(GeneralaCategory.TWOS)  # Score: 10
        
        game.next_player()
        # Round 2: Player 2
        game.roll()
        game.score(GeneralaCategory.TWOS)  # Score: 10
        
        game.next_player()
        assert game.finished  # Game should be complete
        
        winners, totals = game.get_winner()
        assert len(winners) == 2  # Tied
        assert totals == [15, 15]


def test_game_early_win_condition():
    """Test game ending early with first-roll Generala"""
    def fake_roll_generala(held=None):
        if held is None:
            held = []
        return held + [6] * (GeneralaRules.DICE_COUNT - len(held))

    import unittest.mock
    game = GeneralaGame(["p1", "p2"])
    
    with unittest.mock.patch.object(GeneralaRules, "roll_dice", fake_roll_generala):
        game.start_turn()
        # Player 1 gets first-roll Generala - should win immediately
        result = game.score(GeneralaCategory.GENERALA)
        
        assert result == "WIN"
        assert game.finished == True
        assert game.scoreboards[0].scores[GeneralaCategory.GENERALA] == 50
        
        winners, totals = game.get_winner()
        assert winners == ["p1"]
        assert totals[0] == 50


def test_scoring_already_filled_category():
    """Test attempting to score in an already filled category"""
    game = GeneralaGame(["p1"])
    game.start_turn()
    game.dice = [1, 1, 1, 1, 1]  # Set dice manually
    game.roll_number = 2  # Simulate after rolling
    
    # Score ones category
    game.score(GeneralaCategory.ONES)
    
    # Try to score ones again - should raise error from scoreboard
    with pytest.raises(ValueError, match="already scored"):
        game.score(GeneralaCategory.ONES)


def test_roll_with_all_dice_held():
    """Test rolling with all 5 dice held (edge of valid behavior)"""
    # This should be valid - holding all dice and "rolling" 0 new ones
    result = GeneralaRules.roll_dice([1, 2, 3, 4, 5])
    assert result == [1, 2, 3, 4, 5]
    assert len(result) == 5


def test_three_rolls_allowed():
    """Test that players can make exactly 3 rolls total per turn"""
    game = GeneralaGame(["p1"])
    
    # start_turn() performs the first roll
    game.start_turn()
    assert game.roll_number == 1  # First roll completed
    
    # Should be able to make second roll
    game.roll()
    assert game.roll_number == 2  # Second roll completed
    
    # Should be able to make third roll
    game.roll()
    assert game.roll_number == 3  # Third roll completed
    
    # Fourth roll should fail
    with pytest.raises(Exception, match="No rolls left"):
        game.roll()
