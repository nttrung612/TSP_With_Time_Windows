import random
import sys

def generate_feasible_tsp_tw(n, max_service=400, max_travel=500, slack=100, seed=None):
    if seed is not None:
        random.seed(seed)

    nodes = list(range(1, n + 1))
    random.shuffle(nodes)

    t = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(i + 1, n + 1):
            travel = random.randint(1, max_travel)
            t[i][j] = t[j][i] = travel

    d = [0] + [random.randint(1, max_service) for _ in range(n)]

    # Assign feasible arrival times based on route
    arrival_time = [0] * (n + 1)
    time_now = 0
    route = [0] + nodes  # start from depot (0)
    for i in range(1, len(route)):
        prev = route[i - 1]
        curr = route[i]
        time_now += t[prev][curr]
        time_now = max(time_now, arrival_time[prev]) + d[prev]
        arrival_time[curr] = time_now

    # build feasible time windows based on those arrival times
    e = [0] * (n + 1)
    l = [0] * (n + 1)
    e[0] = 0
    l[0] = arrival_time[route[-1]] + slack  # depot latest time is final arrival

    for i in range(1, n + 1):
        a = arrival_time[i]
        start = max(0, a - random.randint(0, slack // 2))
        end = a + random.randint(0, slack)
        e[i] = start
        l[i] = end

    return e, l, d, t, route

def save_to_file(filename, n, e, l, d, t):
    with open(filename, "w") as f:
        f.write(str(n) + "\n")
        for i in range(1, n + 1):
            f.write(f"{e[i]} {l[i]} {d[i]}\n")
        for row in t:
            f.write(" ".join(str(x) for x in row) + "\n")

if len(sys.argv) < 2:
    print("Usage: python gen_test.py <n>")
    sys.exit(1)

n = int(sys.argv[1])
e, l, d, t, feasible_route = generate_feasible_tsp_tw(n)
save_to_file("input.txt", n, e, l, d, t)