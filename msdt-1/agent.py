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
    def __init__(self):
        self.game_count = 0
        self.epsilon = 0  # Randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        # for n,p in self.model.named_parameters():
        #     print(p.device,'',n)
        # self.model.to('cuda')
        # for n,p in self.model.named_parameters():
        #     print(p.device,'',n)
        # TODO: model,trainer

    # state (11 Values)
    #[ danger straight, danger right, danger left,
    #
    # direction left, direction right,
    # direction up, direction down
    #
    # food left,food right,
    # food up, food down]
    def get_state(self, game):
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
            # Danger Straight
            (direction_up and game.is_collision(point_up))
            or (direction_down and game.is_collision(point_down))
            or (direction_left and game.is_collision(point_left))
            or (direction_right and game.is_collision(point_right)),

            # Danger right
            (direction_up and game.is_collision(point_right))
            or (direction_down and game.is_collision(point_left))
            or (direction_up and game.is_collision(point_up))
            or (direction_down and game.is_collision(point_down)),

            #Danger Left
            (direction_up and game.is_collision(point_right))
            or (direction_down and game.is_collision(point_left))
            or (direction_right and game.is_collision(point_up))
            or (direction_left and game.is_collision(point_down)),

            # Move Direction
            direction_left,
            direction_right,
            direction_up,
            direction_down,

            #Food Location
            game.food.x < game.head.x,  # food is in left
            game.food.x > game.head.x,  # food is in right
            game.food.y < game.head.y,  # food is up
            game.food.y > game.head.y   # food is down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # popleft if memory exceed

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff explotation / exploitation
        self.epsilon = 80 - self.game_count
        final_move = [0, 0, 0]

        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state_tensor = torch.tensor(state, dtype=torch.float).cuda()
            prediction = self.model(state_tensor).cuda()  # prediction by model
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()

    while True:
        # Get Old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        #remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # Train long memory,plot result
            game.reset()
            agent.game_count += 1
            agent.train_long_memory()

            if score > reward:  # new High score
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