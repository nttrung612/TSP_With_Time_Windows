import time
import sys

with open("input.txt", "r") as file:
    lines = file.readlines()

n = int(lines[0].strip())
client = [0]
for i in range(1, n + 1):
    client.append(list(map(int, lines[i].strip().split())))
t = [list(map(int, line.strip().split())) for line in lines[n+1:2*n+2]]

def check(j, cur_time, vis, prev_node):
    if vis[j]:
        return False
    if cur_time + t[prev_node][j] > client[j][1]:
        return False
    return True

def backtrack(i, f, vis, cur_time, path, best_ans, best_path, start_time):
    if time.time() - start_time > 10:
        print("Time limit exceeded")
        sys.exit(0)
    if i == n:
        if best_ans[0] > f + t[path[-1]][0]:
            best_ans[0] = f + t[path[-1]][0]
            best_path[:] = path[:]
        return
    prev_node = path[-1] if path else 0
    for j in range(1, n + 1):
        if check(j, cur_time, vis, prev_node):
            vis[j] = True
            f += t[prev_node][j]
            cur_time += t[prev_node][j]
            new_cur_time = max(cur_time, client[j][0]) + client[j][2]
            path.append(j)
            backtrack(i + 1, f, vis, new_cur_time, path, best_ans, best_path, start_time)
            vis[j] = False
            f -= t[prev_node][j]
            cur_time -= t[prev_node][j]
            path.pop()

best_ans = [float('inf')]
best_path = []
vis = [False] * (n + 1)
start_time = time.time()
backtrack(0, 0, vis, 0, [], best_ans, best_path, start_time)
print(best_ans[0])
print(n)
print(" ".join(map(str, best_path)))