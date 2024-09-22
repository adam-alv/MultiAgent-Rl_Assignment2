import numpy as np
import random
WALL = 1
EMPTY = 0
VOID = 3
BOX = 2
PLAYER = 4
ACTION = ["UP", "DOWN", "LEFT", "RIGHT"]
ACTION_TO_DIRECTION = {
    'UP': (-1, 0),
    'DOWN': (1, 0),
    'LEFT': (0, -1),
    'RIGHT': (0, 1)
}

GRID = [
    [1, 1, 1, 1, 3, 3],
    [1, 0, 0, 1, 3, 3],
    [1, 0, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1],
    [1, 1, 1, 1, 3, 3]
]

DISCOUNT = 0.90
THETA = 1e-3
PENALTY = -1
GOAL_REWARD = 0
GOAL_POS = (3, 1)
init_state = ((1, 2), (4, 3))

NUMBER_OF_EPISODES = 10000

def is_free(pos):
    if GRID[pos[0]][pos[1]] != WALL:
        return True
    else:
        return False


def reward(state):
    _, box_position = state
    if box_position[0] == GOAL_POS[0] and box_position[1] == GOAL_POS[1]:
        return GOAL_REWARD
    else:
        return PENALTY


def transition(state, action):
    agent_pos, box_pos = state
    move = ACTION_TO_DIRECTION[action]
    next_agent_pos = (agent_pos[0] + move[0], agent_pos[1] + move[1])
    if GRID[next_agent_pos[0]][next_agent_pos[1]] == WALL:
        return state, reward(state)
    if next_agent_pos == box_pos:
        next_box_pos = (next_agent_pos[0] + move[0], next_agent_pos[1] + move[1])
        if is_free(next_box_pos):
            new_box_position = next_box_pos
            new_state = (next_agent_pos, new_box_position)
            return new_state, reward(new_state)
        else:
            return state, reward(state)
    else:
        new_state = (next_agent_pos, box_pos)
        return new_state, reward(new_state)


def box_stuck(state):
    x, y = state
    if (GRID[x - 1][y] == WALL and GRID[x][y - 1] == WALL) or \
            (GRID[x + 1][y] == WALL and GRID[x][y - 1] == WALL) or \
            (GRID[x - 1][y] == WALL and GRID[x][y + 1] == WALL) or \
            (GRID[x + 1][y] == WALL and GRID[x][y + 1] == WALL):
        return True
    return False

def terminal(state):
    _, box_pos = state
    if box_pos == GOAL_POS:
        return True
    if box_stuck(box_pos):
        return True
    return False

def is_terminal(state):
    _, box_pos = state
    if box_pos == GOAL_POS:
        return True
    # if box_stuck(box_pos):
    #     return True
    return False

def monte_carlo(grid, numberOfEpisodes):
    S = []
    sumReturn = {}
    numVisits = {}
    valFunc = {}
    policy = {}
    agent_space = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if
                   (grid[i][j] != WALL and grid[i][j] != VOID)]
    box_positions_space = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if
                           (grid[i][j] != WALL and grid[i][j] != VOID)]
    for agent_pos in agent_space:
        for box_pos in box_positions_space:
            if agent_pos != box_pos:
                S.append((agent_pos, box_pos))
                sumReturn[(agent_pos, box_pos)] = 0
                numVisits[(agent_pos, box_pos)] = 0
                valFunc[(agent_pos, box_pos)] = 0
    state_number = len(S)
    for episode in range(numberOfEpisodes):
        visitedStates = []
        rewardVisitedStates = []
        current_state = S[random.randint(0, state_number-1)]
        visitedStates.append(current_state)

        while True:
            randomAction = ACTION[random.randint(0, len(ACTION)-1)]
            current_state, current_reward = transition(current_state, randomAction)
            rewardVisitedStates.append(current_reward)
            if not terminal(current_state):
                visitedStates.append(current_state)
            else:
                break
        numVisitedState = len(visitedStates)
        Gt = 0
        for indexCurrentState in range(numVisitedState-1, -1, -1):
            statetmp = visitedStates[indexCurrentState]
            rewardtmp = rewardVisitedStates[indexCurrentState]
            Gt = Gt * DISCOUNT + rewardtmp
            if statetmp not in visitedStates[0: indexCurrentState]:
                numVisits[statetmp] = numVisits[statetmp] + 1
                sumReturn[statetmp] = sumReturn[statetmp] + Gt
    for place in S:
        if numVisits[place] != 0:
            valFunc[place] = sumReturn[place]/numVisits[place]

    for agent_pos in agent_space:
        for box_pos in box_positions_space:
            if agent_pos != box_pos:
                state = (agent_pos, box_pos)
                if terminal(state):  # Skip terminal states
                    continue

                best_action = None
                best_value = float('-inf')

                for action in ACTION:
                    next_state, _ = transition(state, action)
                    if next_state in valFunc:
                        next_value = valFunc[next_state]
                        if next_value > best_value:
                            best_value = next_value
                            best_action = action

                policy[state] = best_action
    return valFunc, policy


# def value_iteration(grid, initial_state, goal_positions):
#     theta = THETA
#     discount = DISCOUNT
#     V = {}
#     policy = {}
#     n = 0
#     agent_space = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if
#                    (grid[i][j] != WALL and grid[i][j] != VOID)]
#     box_positions_space = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if
#                            (grid[i][j] != WALL and grid[i][j] != VOID)]
#     for agent_pos in agent_space:
#         for box_pos in box_positions_space:
#             if agent_pos != box_pos:
#                 V[(agent_pos, box_pos)] = 0
#
#     while True:
#         n += 1
#         delta = 0
#         for state in V.keys():
#             if is_terminal(state):
#                 continue
#             v = V[state]
#             max_value = float('-inf')
#
#             for action in ACTION:
#                 next_state, reward = transition(state, action)
#                 value = reward + discount * V[next_state]
#                 if value > max_value:
#                     max_value = value
#             V[state] = max_value
#             delta = max(delta, abs(v - V[state]))
#         if delta < theta:
#             print(f"Value iteration converges at {n} \n")
#             break
#
#     for state in V.keys():
#         if is_terminal(state):
#             continue
#         best_action = None
#         max_value = float('-inf')
#         for action in ACTION:
#             next_state, reward = transition(state, action)
#             value = reward + DISCOUNT * V[next_state]
#             if value > max_value:
#                 max_value = value
#                 best_action = action
#         policy[state] = best_action
#     return policy, V


#policy, V = value_iteration(GRID, init_state, GOAL_POS)
V, policy = monte_carlo(GRID, NUMBER_OF_EPISODES)

print("Optimal Policy:")
for state, action in policy.items():
    print(f"State {state}: Take action {action}")

print("\nValue Function:")
for state, value in V.items():
    print(f"State {state}: Value {value}")


def simulate_actions(policy, initial_state):
    state = initial_state
    steps = 0
    print(f"Initial State: Human {state[0]}, Box {state[1]}")

    while not is_terminal(state):
        action = policy.get(state)
        if not action:
            print("No valid action found. Ending simulation.")
            break
        next_state, _ = transition(state, action)
        print(f"Step {steps + 1}: Human moves {action}, New Human Pos: {next_state[0]}, New Box Pos: {next_state[1]}")
        state = next_state
        steps += 1
        if is_terminal(state):
            print(f"Terminal State reached in {steps} steps: Human {state[0]}, Box {state[1]}")
            break


simulate_actions(policy, init_state)