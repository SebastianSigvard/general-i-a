import torch
import torch.optim as optim
import torch.nn as nn
import random
from collections import deque
from src.generala import GeneralaGame, GeneralaCategory, GeneralaRules
from src.agent import GeneralaQAgent
import matplotlib.pyplot as plt
import argparse


# Parse hidden layers from string
def parse_hidden_layers(s):
    # Parse comma-separated string to list of ints
    return [int(x) for x in s.split(",") if x.strip()]


def soft_update(target, source, tau):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(tau * param.data + (1.0 - tau) * target_param.data)


def get_reward(game, player_idx, prev_score):
    # Reward: difference in score after turn
    score = game.scoreboards[player_idx].total_score()
    return score - prev_score


def evaluate_model(agent, device, eval_episodes=10):
    total_scores = []
    for _ in range(eval_episodes):
        game = GeneralaGame(["A", "B"])
        game.start_turn()
        state = agent.state_to_tensor(game).to(device)
        while not game.finished:
            # Greedy action (epsilon=0)
            action = agent.act(game, epsilon=0.0)
            if action == 0:
                held = []
                game.roll(held)
            elif 1 <= action <= 32:
                held = agent.decode_hold_action(game, action)
                game.roll(held)
            else:
                available = [
                    cat
                    for cat, score in game.scoreboards[
                        game.current_player
                    ].scores.items()
                    if score is None
                ]
                idx = action - (1 + GeneralaQAgent.HOLD_ACTIONS)
                category = available[idx] if 0 <= idx < len(available) else available[0]
                game.score(category)
                game.next_player()
            state = agent.state_to_tensor(game).to(device)
        score = sum(sb.total_score() for sb in game.scoreboards) / len(game.scoreboards)
        total_scores.append(score)
    avg_score = sum(total_scores) / len(total_scores)
    print(f"[Eval] Average final score over {eval_episodes} episodes: {avg_score:.2f}")
    return avg_score


def main():
    parser = argparse.ArgumentParser(description="Train Generala QAgent with configurable hyperparameters.")
    parser.add_argument('--episodes', type=int, default=20000)
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--gamma', type=float, default=0.99)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--eps-start', type=float, default=1.0)
    parser.add_argument('--eps-end', type=float, default=0.05)
    parser.add_argument('--eps-decay', type=float, default=0.9995)
    parser.add_argument('--memory-size', type=int, default=10000)
    parser.add_argument('--target-update', type=int, default=10)
    parser.add_argument('--tau', type=float, default=0.005)
    parser.add_argument('--hidden-layers', type=str, default="128,128", help="Comma-separated hidden layer sizes, e.g. 128,128 or 256,256,128")
    parser.add_argument('--tag', type=str, default="", help="Optional tag for output files")
    args = parser.parse_args()

    EPISODES = args.episodes
    BATCH_SIZE = args.batch_size
    GAMMA = args.gamma
    LR = args.lr
    EPS_START = args.eps_start
    EPS_END = args.eps_end
    EPS_DECAY = args.eps_decay
    MEMORY_SIZE = args.memory_size
    TARGET_UPDATE = args.target_update
    TAU = args.tau
    HIDDEN_LAYERS = parse_hidden_layers(args.hidden_layers)
    TAG = args.tag

    def get_epsilon(episode: int) -> float:
        return EPS_END + (EPS_START - EPS_END) * (EPS_DECAY**episode)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dummy_game = GeneralaGame(["A", "B"])
    state_dim = 5 + 5 + 3 + len(dummy_game.scoreboards[0].scores)
    action_dim = 1 + GeneralaQAgent.HOLD_ACTIONS + len(dummy_game.scoreboards[0].scores)
    agent = GeneralaQAgent(state_dim, action_dim, device=device, hidden_layers=HIDDEN_LAYERS)
    target_agent = GeneralaQAgent(state_dim, action_dim, device=device, hidden_layers=HIDDEN_LAYERS)
    target_agent.model.load_state_dict(agent.model.state_dict())
    optimizer = optim.Adam(agent.model.parameters(), lr=LR)
    memory = deque(maxlen=MEMORY_SIZE)
    loss_fn = nn.MSELoss()
    epsilon = EPS_START

    eval_scores = []  # track mean evaluation scores
    eval_episodes = []  # track episode indices for eval

    for episode in range(1, EPISODES + 1):
        game = GeneralaGame(["A", "B"])
        game.start_turn()
        done = False
        player = 0
        prev_scores = [0, 0]
        state = agent.state_to_tensor(game).to(device)
        episode_transitions = []
        step = 0
        while not game.finished:
            mask = agent.get_action_mask(game)
            action = agent.act(game, epsilon)
            prev_score = game.scoreboards[game.current_player].total_score()
            # Debug: print state, mask, action
            if episode <= 3:
                print(
                    f"[Ep{episode} Step{step}] Player {game.current_player} | Roll {game.roll_number} | Action: {action} | Mask: {mask}"
                )
            # Step in environment
            if action == 0:
                held = []
                game.roll(held)
            elif 1 <= action <= 32:
                held = agent.decode_hold_action(game, action)
                game.roll(held)
            else:
                available = [
                    cat
                    for cat, score in game.scoreboards[
                        game.current_player
                    ].scores.items()
                    if score is None
                ]
                idx = action - (1 + GeneralaQAgent.HOLD_ACTIONS)
                if 0 <= idx < len(available):
                    category = available[idx]
                else:
                    category = available[0]
                # Calculate reward: normalized score for this category
                score = GeneralaRules.score_category(
                    category, game.dice, game.roll_number
                )
                reward = (
                    score if isinstance(score, int) else 0
                ) / 50.0  # Normalize max ~1
                game.score(category)
                next_state = agent.state_to_tensor(game).to(device)
                episode_transitions.append(
                    (state.cpu(), action, reward, next_state.cpu(), False, player)
                )
                game.next_player()
                state = agent.state_to_tensor(game).to(device)
                player = game.current_player
                step += 1
                continue
            next_state = agent.state_to_tensor(game).to(device)
            # No reward for non-scoring steps
            episode_transitions.append(
                (state.cpu(), action, 0.0, next_state.cpu(), False, player)
            )
            state = next_state
            player = game.current_player
            step += 1
        # Mark last transition as terminal and give final normalized total score as reward
        if episode_transitions:
            last = episode_transitions[-1]
            final_score = (
                game.scoreboards[last[5]].total_score() / 500.0
            )  # Normalize (max possible ~500)
            episode_transitions[-1] = (
                last[0],
                last[1],
                final_score,
                torch.zeros_like(last[0]),
                True,
                last[5],
            )
        # Add to memory
        for t in episode_transitions:
            memory.append(t[:5])
        # Print rewards for debug
        if episode <= 3:
            print(f"[Ep{episode}] Rewards: {[t[2] for t in episode_transitions]}")
        # Training step
        if len(memory) >= BATCH_SIZE:
            batch = random.sample(memory, BATCH_SIZE)
            states, actions, rewards, next_states, dones = zip(*batch)
            states = torch.stack(states).to(device)
            actions = torch.tensor(actions, dtype=torch.long, device=device).unsqueeze(
                1
            )
            rewards = torch.tensor(
                rewards, dtype=torch.float32, device=device
            ).unsqueeze(1)
            next_states = torch.stack(next_states).to(device)
            dones = torch.tensor(dones, dtype=torch.bool, device=device).unsqueeze(1)
            q_values = agent.model(states).gather(1, actions)
            q_values = torch.clamp(q_values, -100, 100)
            with torch.no_grad():
                # Double DQN: use main network to select action, target network to evaluate
                next_actions = agent.model(next_states).argmax(1, keepdim=True)
                next_q = target_agent.model(next_states).gather(1, next_actions)
                target = rewards + GAMMA * next_q * (~dones)
                # Reinstate Q–value clamping to prevent saturation:
                target = torch.clamp(target, -100, 100)
            loss = loss_fn(q_values, target)
            optimizer.zero_grad()
            loss.backward()
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(agent.model.parameters(), max_norm=1.0)
            optimizer.step()
            # Debug: print loss and mean Q
            if episode % 50 == 0:
                print(
                    f"[Train] Ep{episode} Loss: {loss.item():.4f} | MeanQ: {q_values.mean().item():.2f}"
                )
            if episode % 200 == 0:
                # Print Q-values for a random state
                idx = random.randint(0, len(memory) - 1)
                s = memory[idx][0].to(device)
                qvals = agent.model(s).detach().cpu().numpy()
                print(f"[Debug] Ep{episode} Sample Q-values: {qvals}")
        # Update target network using soft update
        if episode % TARGET_UPDATE == 0:
            soft_update(target_agent.model, agent.model, TAU)
        epsilon = get_epsilon(episode)  # Replace epsilon update with scheduled epsilon
        if episode % BATCH_SIZE == 0:
            print(
                f"Episode {episode}, epsilon={epsilon:.3f}, mean score: {sum([sb.total_score() for sb in game.scoreboards])/len(game.scoreboards):.2f}"
            )
        # Periodically run evaluation in greedy mode
        if episode % 500 == 0:
            avg_eval = evaluate_model(agent, device, eval_episodes=10)
            eval_scores.append(avg_eval)
            eval_episodes.append(episode)
    # Plot evaluation score progression after training
    hp_str = f"ep{EPISODES}_bs{BATCH_SIZE}_g{GAMMA}_lr{LR}_eps{EPS_START}-{EPS_END}-{EPS_DECAY}_mem{MEMORY_SIZE}_tu{TARGET_UPDATE}_tau{TAU}_hl{'-'.join(map(str,HIDDEN_LAYERS))}{('_'+TAG) if TAG else ''}"
    plt.plot(eval_episodes, eval_scores)
    plt.xlabel("Episode")
    plt.ylabel("Average Evaluation Score")
    plt.title("Evaluation Score Progress")
    plt.savefig(f"eval_score_progress_{hp_str}.png")
    plt.show()
    torch.save(agent.model.state_dict(), f"qagent_generala_{hp_str}.pth")
    print(f"Training complete. Model saved as qagent_generala_{hp_str}.pth and plot as eval_score_progress_{hp_str}.png")


if __name__ == "__main__":
    main()
