from generala import (
    GeneralaScoreBoard,
    GeneralaAction,
    GeneralaCategory,
    GeneralaGame,
    GeneralaRules,
)
from typing import List
import sys
from agent import GeneralaQAgent

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
    game = GeneralaGame(player_names)
    game.start_turn()
    while not game.finished:
        print_scoreboard(game.scoreboards, game.player_names)
        player_name = game.player_names[game.current_player]
        print(
            f"\n🌟 {player_name}'s turn (Round {game.round+1}/{game.num_categories}) 🌟"
        )
        while True:
            print(f"\n🎲 Current dice: ", " ".join(f"[{d}]" for d in game.dice))
            action = prompt_action(
                game.roll_number,
                GeneralaRules.MAX_ROLLS,
            )
            if action == GeneralaAction.ROLL:
                if game.roll_number >= GeneralaRules.MAX_ROLLS:
                    print("No rolls left.")
                    continue
                held = prompt_dice_to_hold(game.dice, game.roll_number)
                game.roll(held)
            elif action == GeneralaAction.HOLD:
                held = prompt_dice_to_hold(game.dice, game.roll_number)
                game.roll(held)
            elif action == "show_score":
                print_scoreboard(game.scoreboards, game.player_names)
            elif action == "score":
                available = [
                    cat
                    for cat, score in game.scoreboards[
                        game.current_player
                    ].scores.items()
                    if score is None
                ]
                print("Available categories:")
                for i, cat in enumerate(available):
                    print(f"{i+1}. {cat.value.capitalize()}")
                choice = input("Choose a category by number: ")
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(available):
                        category = available[idx]
                    else:
                        category = available[0]
                except Exception:
                    category = available[0]
                result = game.score(category)
                if result == "WIN":
                    print("🏆 Generala served! You win!")
                elif isinstance(result, int):
                    print(f"✅ Scored {result} in {category.value}\n")
                else:
                    print(f"Invalid score returned: {result}\n")
                break
        game.next_player()
    print("\n🎉 Final Scoreboards:")
    print_scoreboard(game.scoreboards, game.player_names)
    winners, totals = game.get_winner()
    if len(winners) == 1:
        print(f"🏆 {winners[0]} wins!")
    else:
        print("🤝 It's a tie!")


def play_generala_cli_vs_agent(checkpoint_path: str = None) -> None:
    import torch

    print("Welcome to Generala! 🎲")
    human_name = input("Enter your name: ")
    agent_name = "QAgent"
    player_names = [human_name, agent_name]
    game = GeneralaGame(player_names)
    game.start_turn()
    # Setup agent
    state_dim = (
        5 + 5 + 3 + len(game.scoreboards[0].scores)
    )  # dice, held, roll_onehot(3), categories
    num_categories = len(game.scoreboards[0].scores)
    action_dim = (
        1 + GeneralaQAgent.HOLD_ACTIONS + num_categories
    )  # ROLL + HOLDs + SCOREs
    agent = GeneralaQAgent(state_dim, action_dim)
    if checkpoint_path:
        try:
            checkpoint = torch.load(checkpoint_path, map_location=agent.device)
            agent.model.load_state_dict(checkpoint)
            print(f"[INFO] Loaded QAgent checkpoint from {checkpoint_path}")
        except Exception as e:
            print(f"[WARNING] Failed to load checkpoint: {e}")
    agent_actions_log = []
    while not game.finished:
        print_scoreboard(game.scoreboards, game.player_names)
        player_name = game.player_names[game.current_player]
        print(
            f"\n🌟 {player_name}'s turn (Round {game.round+1}/{game.num_categories}) 🌟"
        )
        is_agent = player_name == agent_name
        while True:
            print(f"\n🎲 Current dice: ", " ".join(f"[{d}]" for d in game.dice))
            if is_agent:
                action_idx = agent.act(game, epsilon=1.0)  # Force random for debug
                mask = agent.get_action_mask(game)
                if action_idx == 0:
                    action = GeneralaAction.ROLL
                elif 1 <= action_idx <= 32:
                    action = GeneralaAction.HOLD
                else:
                    action = "score"
                print(
                    f"🤖 QAgent chooses: {action if isinstance(action, str) else action.value}"
                )
                # Log the action for debugging
                agent_actions_log.append(
                    {
                        "round": game.round + 1,
                        "roll_number": game.roll_number,
                        "dice": list(game.dice),
                        "action_idx": action_idx,
                        "action": action if isinstance(action, str) else action.value,
                    }
                )
            else:
                action = prompt_action(
                    game.roll_number,
                    GeneralaRules.MAX_ROLLS,
                )
            if action == GeneralaAction.ROLL:
                if game.roll_number >= GeneralaRules.MAX_ROLLS:
                    print("No rolls left.")
                    if is_agent:
                        # Force agent to score if it tries to roll with no rolls left
                        action = "score"
                    else:
                        continue
                if action == GeneralaAction.ROLL:
                    if is_agent:
                        held = []  # Agent: roll all dice
                    else:
                        held = prompt_dice_to_hold(game.dice, game.roll_number)
                    game.roll(held)
                    continue
            # Handle agent HOLD actions (1-32) ONLY if agent chose a hold action
            if (
                is_agent
                and isinstance(action_idx, int)
                and 1 <= action_idx <= 32
                and action == GeneralaAction.HOLD
            ):
                held = agent.decode_hold_action(game, action_idx)
                print(f"🤖 QAgent holds: {held}")
                game.roll(held)
                continue
            if action == GeneralaAction.HOLD:
                if is_agent:
                    held = []  # Should not be used, but fallback
                else:
                    held = prompt_dice_to_hold(game.dice, game.roll_number)
                game.roll(held)
                continue
            if action == "show_score":
                print_scoreboard(game.scoreboards, game.player_names)
                if is_agent:
                    break  # Agent never chooses this
                continue
            if action == "score":
                available = [
                    cat
                    for cat, score in game.scoreboards[
                        game.current_player
                    ].scores.items()
                    if score is None
                ]
                if is_agent:
                    # Agent: pick category with highest Q value among available
                    mask = agent.get_action_mask(game)
                    q_values = (
                        agent.model(agent.state_to_tensor(game)).detach().tolist()
                    )
                    best = None
                    best_val = -float("inf")
                    for i, cat in enumerate(available):
                        idx = 2 + list(
                            game.scoreboards[game.current_player].scores.keys()
                        ).index(cat)
                        if mask[idx] and q_values[idx] > best_val:
                            best = cat
                            best_val = q_values[idx]
                    category = best if best is not None else available[0]
                    print(f"🤖 QAgent scores in: {category.value}")
                else:
                    print("Available categories:")
                    for i, cat in enumerate(available):
                        print(f"{i+1}. {cat.value.capitalize()}")
                    choice = input("Choose a category by number: ")
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(available):
                            category = available[idx]
                        else:
                            category = available[0]
                    except Exception:
                        category = available[0]
                result = game.score(category)
                if result == "WIN":
                    print("🏆 Generala served! You win!")
                elif isinstance(result, int):
                    print(f"✅ Scored {result} in {category.value}\n")
                else:
                    print(f"Invalid score returned: {result}\n")
                break
        game.next_player()
    print("\n🎉 Final Scoreboards:")
    print_scoreboard(game.scoreboards, game.player_names)
    winners, totals = game.get_winner()
    if len(winners) == 1:
        print(f"🏆 {winners[0]} wins!")
    else:
        print("🤝 It's a tie!")
    # Log all agent actions at the end
    print("\n[QAgent Actions Log]")
    for entry in agent_actions_log:
        print(
            f"Round {entry['round']} | Roll {entry['roll_number']} | Dice: {entry['dice']} | ActionIdx: {entry['action_idx']} | Action: {entry['action']}"
        )


def main():
    import sys

    print("1. Play Human vs Human")
    print("2. Play Human vs QAgent")
    choice = input("Choose game mode: ")
    checkpoint_path = None
    if choice.strip() == "2":
        if len(sys.argv) > 1:
            checkpoint_path = sys.argv[1]
        else:
            use_ckpt = input("Load QAgent checkpoint? (y/n): ").strip().lower()
            if use_ckpt == "y":
                checkpoint_path = input("Enter checkpoint path: ").strip()
        play_generala_cli_vs_agent(checkpoint_path)
    else:
        play_generala_cli()


if __name__ == "__main__":
    main()
