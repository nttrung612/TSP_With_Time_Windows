with open("input.txt") as f:
    lines = f.readlines()
n = int(lines[0])
e, l, d = [0], [0], [0]
for i in range(1, n + 1):
    e1, l1, d1 = map(int, lines[i].split())
    e.append(e1)
    l.append(l1)
    d.append(d1)
t = [list(map(int, lines[i].split())) for i in range(n + 1, 2*n + 2)]

import random
import time

def init_feasible_solution(n, e, l, d, t):
    path = [0]
    cur_time = 0
    visited = [False] * (n + 1)
    visited[0] = True

    while len(path) < n + 1:
        next_node = -1
        for j in range(1, n + 1):
            if not visited[j] and cur_time + t[path[-1]][j] <= l[j]:
                if next_node == -1 or e[j] < e[next_node]:
                    next_node = j
        if next_node == -1:
            break
        visited[next_node] = True
        path.append(next_node)
        cur_time += t[path[-2]][next_node]
        cur_time = max(cur_time, e[next_node]) + d[next_node]

    return path

def calculate_cost(path, t):
    cost = 0
    for i in range(len(path) - 1):
        cost += t[path[i]][path[i + 1]]
    return cost
def is_feasible(path, e, l, d, t):
    cur_time = 0
    for i in range(len(path) - 1):
        cur_time += t[path[i]][path[i + 1]]
        if cur_time > l[path[i + 1]]:
            return False
        cur_time = max(cur_time, e[path[i + 1]]) + d[path[i + 1]]
    return True
def local_search(path, t, e, l, d):
    best_path = path[:]
    best_cost = calculate_cost(best_path, t)
    improved = True

    while improved:
        improved = False
        for i in range(1, len(best_path) - 1):
            for j in range(i + 1, len(best_path)):
                new_path = best_path[:]
                new_path[i], new_path[j] = new_path[j], new_path[i]
                if is_feasible(new_path, e, l, d, t):
                    new_cost = calculate_cost(new_path, t)
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_path = new_path
                        improved = True
    return best_path
def simulated_annealing(n, e, l, d, t, initial_path):
    current_path = initial_path[:]
    current_cost = calculate_cost(current_path, t)
    best_path = current_path[:]
    best_cost = current_cost

    temperature = 1000
    cooling_rate = 0.995
    start_time = time.time()

    while time.time() - start_time < 30:
        i, j = random.sample(range(1, n + 1), 2)
        new_path = current_path[:]
        new_path[i], new_path[j] = new_path[j], new_path[i]

        if is_feasible(new_path, e, l, d, t):
            new_cost = calculate_cost(new_path, t)
            if new_cost < current_cost or random.random() < (temperature / (temperature + 1)):
                current_path = new_path
                current_cost = new_cost
                if current_cost < best_cost:
                    best_path = current_path[:]
                    best_cost = current_cost

        temperature *= cooling_rate

    return best_path, best_cost
# best_path, best_cost = simulated_annealing(n, e, l, d, t, complete_candidate)
# print(best_cost)
# print(n)
# print(" ".join(map(str, best_path[1:])))


complete_candidate = init_feasible_solution(n, e, l, d, t)
print(is_feasible(complete_candidate, e, l, d, t))
best_path = local_search(complete_candidate, t, e, l, d)
best_cost = calculate_cost(best_path, t)
print(best_cost)
print(n)
print(" ".join(map(str, best_path[1:])))
    # for _ in range(max_iterations):
    #     i, j = random.sample(range(1, len(best_path)), 2)
    #     if i > j:
    #         i, j = j, i
    #     new_path = best_path[:]
    #     # new_path[i:j] = reversed(new_path[i:j])
    #     random.shuffle(new_path[i:j])
        
    #     if is_feasible(new_path):
    #         new_cost = calculate_cost(new_path)
    #         if new_cost < best_cost:
    #             best_cost = new_cost
    #             best_path = new_path