# Minimal DQN-like scorer using a tiny MLP to score actions given state.
# For simplicity we only train a single-step scorer that learns to prefer
# the closest cylinder (approximating SSTF). This is a teaching scaffold.
import numpy as np
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
except Exception as e:
    torch = None

class TinyQ:
    def __init__(self, state_dim: int, num_actions: int, lr: float = 1e-3):
        if torch is None:
            raise ImportError("PyTorch not available. Install torch to use DQN.")
        self.model = nn.Sequential(
            nn.Linear(state_dim, 32),
            nn.ReLU(),
            nn.Linear(32, num_actions),
        )
        self.opt = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

    def predict(self, x: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            t = torch.tensor(x, dtype=torch.float32)
            out = self.model(t).numpy()
        return out

    def train_step(self, x: np.ndarray, y: np.ndarray):
        t_x = torch.tensor(x, dtype=torch.float32)
        t_y = torch.tensor(y, dtype=torch.float32)
        self.opt.zero_grad()
        out = self.model(t_x)
        loss = self.loss_fn(out, t_y)
        loss.backward()
        self.opt.step()
        return float(loss.item())
