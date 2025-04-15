from generala import GeneralaRules, GeneralaScoreBoard, GeneralaAction, GeneralaCategory
from typing import List

# Placeholder functions for CLI interaction


def print_scoreboard(scoreboards: list, player_names: list) -> None:
    # Dynamically determine column widths
    cat_width = (
        max(len(cat.value.capitalize()) for cat in scoreboards[0].scores.keys()) + 2
    )
    score_width = 9
    total_width = (
        cat_width
        + 2
        + (score_width + 2) * len(scoreboards)
        + (len(scoreboards) - 1) * 1
    )
    print(f"\n🎲 {'─' * (total_width - 4)} Scoreboard {'─' * (total_width - 4)} 🎲")
    # Header
    header = f"┌{'─' * (cat_width + 2)}"
    for _ in scoreboards:
        header += f"┬{'─' * (score_width + 2)}"
    header += "┐"
    print(header)
    # Player names row
    row = f"│ {'Category'.ljust(cat_width)} "
    for name in player_names:
        row += f"│ {name.center(score_width)} "
    row += "│"
    print(row)
    # Separator
    sep = f"├{'─' * (cat_width + 2)}"
    for _ in scoreboards:
        sep += f"┼{'─' * (score_width + 2)}"
    sep += "┤"
    print(sep)
    # Score rows
    for cat in scoreboards[0].scores.keys():
        row = f"│ {cat.value.capitalize().ljust(cat_width)} "
        for sb in scoreboards:
            score = sb.scores[cat]
            score_str = str(score) if score is not None else "-"
            row += f"│ {score_str.center(score_width)} "
        row += "│"
        print(row)
    # Footer
    footer = f"└{'─' * (cat_width + 2)}"
    for _ in scoreboards:
        footer += f"┴{'─' * (score_width + 2)}"
    footer += "┘"
    print(footer)
    # Total scores
    total_row = f"🏆 Total score:"
    for sb in scoreboards:
        total_row += f" {sb.total_score()}"
    print(total_row + "\n")


def prompt_dice_to_hold(dice: List[int], roll_number: int) -> List[int]:
    # TODO: Implement user prompt for dice to hold
    print(f"Roll {roll_number}: {dice}")
    hold_input = input(
        "Enter dice to hold (comma separated, e.g. 1,3,5), or press Enter to hold none: "
    )
    if not hold_input.strip():
        return []
    try:
        indices = [int(i) - 1 for i in hold_input.split(",") if i.strip().isdigit()]
        return [dice[i] for i in indices if 0 <= i < len(dice)]
    except Exception:
        print("Invalid input. Holding none.")
        return []


def prompt_category(
    scoreboard: GeneralaScoreBoard, dice: List[int]
) -> GeneralaCategory:
    print("Current dice:", " ".join(f"[{d}]" for d in dice))
    print_scoreboard([scoreboard], ["Player"])
    available = [cat for cat, score in scoreboard.scores.items() if score is None]
    print("Available categories:")
    for i, cat in enumerate(available):
        print(f"{i+1}. {cat.value.capitalize()}")
    choice = input("Choose a category by number: ")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            return available[idx]
    except Exception:
        pass
    print("Invalid choice. Choosing first available.")
    return available[0]


def prompt_action(roll_number: int, max_rolls: int) -> "GeneralaAction | str":
    print(f"\n✨ Choose an action (Roll {roll_number}/{max_rolls}):")
    actions = [GeneralaAction.ROLL, GeneralaAction.HOLD, "show_score"]
    if roll_number >= max_rolls:
        actions = [
            a for a in actions if a not in (GeneralaAction.ROLL, GeneralaAction.HOLD)
        ]
    actions.append("score")
    emoji_map = {
        GeneralaAction.ROLL: "🎲",
        GeneralaAction.HOLD: "✋",
        "show_score": "📊",
        "score": "✅",
    }
    for i, action in enumerate(actions):
        if action == "show_score":
            print(f"{i+1}. {emoji_map['show_score']} Show Scoreboard")
        elif action == "score":
            print(f"{i+1}. {emoji_map['score']} Score (end turn)")
        elif hasattr(action, "value"):
            print(f"{i+1}. {emoji_map[action]} {action.value.capitalize()}")
        else:
            print(f"{i+1}. {str(action)}")
    choice = input("Action number: ")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(actions):
            selected = actions[idx]
            if isinstance(selected, (GeneralaAction, str)):
                return selected
    except Exception:
        pass
    print(
        f"Invalid choice. Defaulting to {actions[0].value if hasattr(actions[0], 'value') else str(actions[0])}."
    )
    if isinstance(actions[0], (GeneralaAction, str)):
        return actions[0]
    else:
        return str(actions[0])


def play_generala_cli() -> None:
    print("Welcome to Generala! 🎲")
    player_names = [
        input("Enter name for Player 1: "),
        input("Enter name for Player 2: "),
    ]
    scoreboards = [GeneralaScoreBoard(), GeneralaScoreBoard()]
    num_categories = len(GeneralaRules.CATEGORIES)
    for round_num in range(num_categories):
        print_scoreboard(scoreboards, player_names)
        for player_idx, player_name in enumerate(player_names):
            print(
                f"\n🌟 {player_name}'s turn (Round {round_num+1}/{num_categories}) 🌟"
            )
            dice = GeneralaRules.roll_dice()
            held = []
            roll_number = 1
            while roll_number <= GeneralaRules.MAX_ROLLS:
                print(f"\n🎲 Current dice: ", " ".join(f"[{d}]" for d in dice))
                action = prompt_action(roll_number, GeneralaRules.MAX_ROLLS)
                if action == GeneralaAction.ROLL:
                    if roll_number == GeneralaRules.MAX_ROLLS:
                        print("No rolls left.")
                        continue
                    held = prompt_dice_to_hold(dice, roll_number)
                    dice = GeneralaRules.roll_dice(held)
                    roll_number += 1
                elif action == GeneralaAction.HOLD:
                    held = prompt_dice_to_hold(dice, roll_number)
                    dice = GeneralaRules.roll_dice(held)
                    roll_number += 1
                elif action == "show_score":
                    print_scoreboard(scoreboards, player_names)
                elif action == "score":
                    category = prompt_category(scoreboards[player_idx], dice)
                    score = GeneralaRules.score_category(category, dice, roll_number)
                    if score == "WIN":
                        print("🏆 Generala served! You win!")
                        scoreboards[player_idx].set_score(category, 50)
                        break
                    if isinstance(score, int):
                        scoreboards[player_idx].set_score(category, score)
                        print(f"✅ Scored {score} in {category.value}\n")
                        break
                    else:
                        print(f"Invalid score returned: {score}\n")
            else:
                category = prompt_category(scoreboards[player_idx], dice)
                score = GeneralaRules.score_category(category, dice, roll_number)
                if isinstance(score, int):
                    scoreboards[player_idx].set_score(category, score)
                    print(f"✅ Scored {score} in {category.value}\n")
                else:
                    print(f"Invalid score returned: {score}\n")
    print("\n🎉 Final Scoreboards:")
    print_scoreboard(scoreboards, player_names)
    scores = [sb.total_score() for sb in scoreboards]
    if scores[0] > scores[1]:
        print(f"🏆 {player_names[0]} wins!")
    elif scores[1] > scores[0]:
        print(f"🏆 {player_names[1]} wins!")
    else:
        print("🤝 It's a tie!")


if __name__ == "__main__":
    play_generala_cli()
