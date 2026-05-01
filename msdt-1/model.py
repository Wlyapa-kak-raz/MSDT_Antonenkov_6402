import os

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F



class Linear_QNet(nn.Module):
    """Linear neural network for Q-value prediction."""

    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size).cuda()
        self.linear2 = nn.Linear(hidden_size, output_size).cuda()

    def forward(self, x):
        """Return model prediction for the input tensor."""
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        """Save the model state to a file."""
        model_folder_path = 'D:\SnakeAI'
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    """Trainer for updating the Q-network."""

    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
        for param in self.model.parameters():
            print(param.is_cuda)

    def train_step(self, state, action, reward, next_state, done):
        """Train the model on one step or a batch of steps."""
        state_tensor = torch.tensor(state, dtype=torch.float).cuda()
        next_state_tensor = torch.tensor(next_state, dtype=torch.float).cuda()
        action_tensor = torch.tensor(action, dtype=torch.long).cuda()
        reward_tensor = torch.tensor(reward, dtype=torch.float).cuda()

        if len(state_tensor.shape) == 1:
            state_tensor = torch.unsqueeze(state_tensor, 0).cuda()
            next_state_tensor = torch.unsqueeze(next_state_tensor, 0).cuda()
            action_tensor = torch.unsqueeze(action_tensor, 0).cuda()
            reward_tensor = torch.unsqueeze(reward_tensor, 0).cuda()
            done = (done,)

        prediction = self.model(state_tensor).cuda()
        target = prediction.clone().cuda()

        for idx in range(len(done)):
            q_new = reward_tensor[idx]
            if not done[idx]:
                q_new = reward_tensor[idx] + self.gamma * torch.max(self.model(next_state_tensor[idx])).cuda()
            target[idx][torch.argmax(action_tensor).item()] = q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, prediction)
        loss.backward()

        self.optimizer.step()