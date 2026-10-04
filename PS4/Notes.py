# Corrected PS4-style grid setup
# 0 = free space, 1 = blocked cell

grid = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 1, 1, 0],
]

init = [0, 0]
goal = [len(grid) - 1, len(grid[0]) - 1]
cost = 1

delta = [
    [-1, 0],  # go up
    [0, -1],  # go left
    [1, 0],   # go down
    [0, 1],   # go right
]


delta = [
    [-1, 0],  # up
    [0, -1],  # left
    [1, 0],   # down
    [0, 1],   # right
]




def compute_value(grid, goal, cost):
    rows = len(grid)
    cols = len(grid[0])

    value = [[99 for _ in range(cols)] for _ in range(rows)]
    change = True

    while change:
        change = False

        for x in range(rows):
            for y in range(cols):
                if grid[x][y] == 1:
                    continue

                if [x, y] == goal:
                    if value[x][y] > 0:
                        value[x][y] = 0
                        change = True
                    continue

                for a in range(len(delta)):
                    x2 = x + delta[a][0]
                    y2 = y + delta[a][1]

                    if 0 <= x2 < rows and 0 <= y2 < cols and grid[x2][y2] != 1:
                        v2 = value[x2][y2] + cost
                        if v2 < value[x][y]:
                            change = True
                            value[x][y] = v2

    return value



heuristic = compute_value(grid, goal, cost)



def A_star(grid, init, goal, cost):
    open_list = [[0 + heuristic[init[0]][init[1]], 0, init[0], init[1]]]
    closed_list = [[False for _ in range(len(grid[0]))] for _ in range(len(grid))]
    closed_list[init[0]][init[1]] = True

    while open_list:
        open_list.sort()
        open_list.reverse()
        f, g, x, y = open_list.pop()

        if [x, y] == goal:
            return g

        for a in range(len(delta)):
            x2 = x + delta[a][0]
            y2 = y + delta[a][1]
            if 0 <= x2 < len(grid) and 0 <= y2 < len(grid[0]) and not closed_list[x2][y2] and grid[x2][y2] == 0:
                g2 = g + cost
                f2 = g2 + heuristic[x2][y2]
                open_list.append([f2, g2, x2, y2])
                closed_list[x2][y2] = True

    return None


movements = ["^", "<", "v", ">"]

def print_optimum_policy(grid, value):
    policy = [[" " for _ in range(len(grid[0]))] for _ in range(len(grid))]

    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if grid[x][y] == 1:
                policy[x][y] = " "
                continue

            if [x, y] == goal:
                policy[x][y] = "*"
                continue

            min_value = value[x][y]
            best_move = " "
            for a in range(len(delta)):
                x2 = x + delta[a][0]
                y2 = y + delta[a][1]
                if 0 <= x2 < len(grid) and 0 <= y2 < len(grid[0]) and value[x2][y2] < min_value:
                    min_value = value[x2][y2]
                    best_move = movements[a]
            policy[x][y] = best_move

    for row in policy:
        print(row)








if __name__ == "__main__":
    print("Grid:")
    for row in grid:
        print(row)
    print(f"init = {init}")
    print(f"goal = {goal}")
    print(f"cost = {cost}")
    value = compute_value(grid, goal, cost)
    print("Value grid:")
    for row in value:
        print(row)

    result = A_star(grid, init, goal, cost)
    print(f"A* result: {result}")

    print("_______________")
    print("Optimum policy:")
    print_optimum_policy(grid, value)

    print("Planning Descrite State Space, A Star and Dynamic Programming")
