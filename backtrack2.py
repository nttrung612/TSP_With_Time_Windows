import time
import sys

with open("input.txt", "r") as file:
    lines = file.readlines()

n = int(lines[0].strip())
client = [(0, 0, 0)]
for i in range(1, n + 1):
    client.append(list(map(int, lines[i].strip().split())))
t = [list(map(int, line.strip().split())) for line in lines[n+1:2*n+2]]

new_client = sorted(
    [(i, e, l, d) for i, (e, l, d) in enumerate(client)],
    key=lambda x: (x[1], x[2], x[3])
)

new_t = []
for row in t:
    sorted_row = sorted(
        [(j, time) for j, time in enumerate(row)],
        key=lambda x: x[1]
    )

def check(j, cur_time, vis, prev_node):
    if vis[j]:
        return False
    if cur_time + t[prev_node][j] > client[j][1]:
        return False
    return True

def backtrack(i, f, vis, cur_time, path, best_ans, best_path, start_time):
    if time.time() - start_time > 20:
        print("Time limit exceeded")
        sys.exit(0)
    if i == n:
        if best_ans[0] > f:
            best_ans[0] = f
            best_path[:] = path[:]
        return
    
    prev_node = path[-1] if path else 0
    for j in range(1, n + 1):
        node = new_client[j][0]
        if check(node, cur_time, vis, prev_node):
            vis[node] = True
            f += t[prev_node][node]
            cur_time += t[prev_node][node]
            new_cur_time = max(cur_time, client[node][0]) + client[node][2]
            path.append(node)
            backtrack(i + 1, f, vis, new_cur_time, path, best_ans, best_path, start_time)
            vis[node] = False
            f -= t[prev_node][node]
            cur_time -= t[prev_node][node]
            path.pop()

best_ans = [float('inf')]
best_path = []
vis = [False] * (n + 1)
start_time = time.time()
backtrack(0, 0, vis, 0, [], best_ans, best_path, start_time)
# print(best_ans[0])
print(n)
print(" ".join(map(str, best_path)))