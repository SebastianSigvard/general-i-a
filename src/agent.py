import torch
import torch.nn as nn
import torch.nn.functional as F
from generala import GeneralaGame, GeneralaAction, GeneralaCategory, GeneralaRules
from typing import List, Optional


class GeneralaQNetwork(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, hidden_layers: list = [128, 128]):
        super().__init__()
        layers = []
        input_dim = state_dim
        for hidden_dim in hidden_layers:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        layers.append(nn.Linear(input_dim, action_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class GeneralaQAgent:
    HOLD_ACTIONS = 32  # 2^5 possible hold combinations for 5 dice

    def __init__(self, state_dim: int, action_dim: int, device: str = "cpu", hidden_layers: list = [128, 128]):
        self.model = GeneralaQNetwork(state_dim, action_dim, hidden_layers)
        self.device = device
        self.model.to(device)
        self.action_dim = action_dim

    @staticmethod
    def state_to_tensor(game: GeneralaGame) -> torch.Tensor:
        # Example state encoding: dice (5), held (5), roll_number (1-hot, 3), categories filled (11)
        dice = game.dice + [0] * (GeneralaRules.DICE_COUNT - len(game.dice))
        held = game.held + [0] * (GeneralaRules.DICE_COUNT - len(game.held))
        # One-hot encode the roll number (1st, 2nd, 3rd roll)
        roll_onehot = [0, 0, 0]
        roll_idx = min(max(game.roll_number - 1, 0), 2)
        roll_onehot[roll_idx] = 1
        categories = [
            1 if v is not None else 0
            for v in game.scoreboards[game.current_player].scores.values()
        ]
        state = dice + held + roll_onehot + categories
        return torch.tensor(state, dtype=torch.float32)

    @staticmethod
    def all_hold_masks():
        # Returns a list of all possible hold masks (one-hot, length 5)
        return [
            [(i >> j) & 1 for j in range(GeneralaRules.DICE_COUNT)]
            for i in range(GeneralaQAgent.HOLD_ACTIONS)
        ]

    @staticmethod
    def decode_hold_action(game: GeneralaGame, hold_action_idx: int) -> List[int]:
        # Given a hold action index (1-32), return the dice to hold
        mask = GeneralaQAgent.all_hold_masks()[hold_action_idx - 1]  # 0 is ROLL
        return [d for d, m in zip(game.dice, mask) if m]

    @staticmethod
    def get_action_mask(game: GeneralaGame) -> List[int]:
        # Action order: [ROLL, HOLD_00000, HOLD_00001, ..., HOLD_11111, SCORE...]
        mask = []
        # ROLL: only if rolls left
        mask.append(int(game.roll_number <= GeneralaRules.MAX_ROLLS))
        # HOLD actions: only if roll_number < MAX_ROLLS (i.e., before the 3rd roll)
        mask.extend(
            [int(game.roll_number < GeneralaRules.MAX_ROLLS)]
            * GeneralaQAgent.HOLD_ACTIONS
        )
        # SCORE: one for each category, only if not already filled
        available = [
            score is None
            for score in game.scoreboards[game.current_player].scores.values()
        ]
        mask.extend(available)
        return mask

    def act(self, game: GeneralaGame, epsilon: float = 0.0) -> int:
        state = self.state_to_tensor(game).to(self.device)
        mask = torch.tensor(
            self.get_action_mask(game), dtype=torch.bool, device=self.device
        )
        q_values = self.model(state)
        q_values[~mask] = -float("inf")  # Mask out invalid actions
        if torch.rand(1).item() < epsilon:
            valid_indices = mask.nonzero(as_tuple=True)[0]
            return valid_indices[torch.randint(len(valid_indices), (1,))].item()
        else:
            return torch.argmax(q_values).item()
