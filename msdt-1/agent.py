import random
from collections import deque

import numpy as np
import torch

from snake_gameai import BLOCK_SIZE, SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    """Agent that trains the neural network to play Snake."""

    def __init__(self):
        self.game_count = 0
        self.epsilon = 0  # Randomness
        self.gamma = 0.9  # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        """Return the current game state as an array of input values."""
        head = game.snake[0]

        point_left = Point(head.x - BLOCK_SIZE, head.y)
        point_right = Point(head.x + BLOCK_SIZE, head.y)
        point_up = Point(head.x, head.y - BLOCK_SIZE)
        point_down = Point(head.x, head.y + BLOCK_SIZE)

        direction_left = game.direction == Direction.LEFT
        direction_right = game.direction == Direction.RIGHT
        direction_up = game.direction == Direction.UP
        direction_down = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (direction_up and game.is_collision(point_up))
            or (direction_down and game.is_collision(point_down))
            or (direction_left and game.is_collision(point_left))
            or (direction_right and game.is_collision(point_right)),

            # Danger right
            (direction_up and game.is_collision(point_right))
            or (direction_down and game.is_collision(point_left))
            or (direction_up and game.is_collision(point_up))
            or (direction_down and game.is_collision(point_down)),

            # Danger left
            (direction_up and game.is_collision(point_right))
            or (direction_down and game.is_collision(point_left))
            or (direction_right and game.is_collision(point_up))
            or (direction_left and game.is_collision(point_down)),

            # Move direction
            direction_left,
            direction_right,
            direction_up,
            direction_down,

            # Food location
            game.food.x < game.head.x,  # Food is on the left
            game.food.x > game.head.x,  # Food is on the right
            game.food.y < game.head.y,  # Food is above
            game.food.y > game.head.y   # Food is below
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        """Save one game step in memory."""
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        """Train the model using a batch of previous game steps."""
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        """Train the model using the latest game step."""
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        """Choose the next move using exploration or model prediction."""
        self.epsilon = 80 - self.game_count
        final_move = [0, 0, 0]

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state_tensor = torch.tensor(state, dtype=torch.float).cuda()
            prediction = self.model(state_tensor).cuda()
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    """Run the training loop."""
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()

    while True:
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)

        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.game_count += 1
            agent.train_long_memory()

            if score > reward:  # New high score
                reward = score
                agent.model.save()

            print('Game:', agent.game_count, 'Score:', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.game_count
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == "__main__":
    train()