from ortools.sat.python import cp_model

def read_input():
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
    return n, e, l, d, t

def solve_delivery_route():
    N, e, l, d, t = read_input()
    t0 = 0  # Starting time at warehouse
    M = 10**6  # Big-M for timing constraints

    # Create the model
    model = cp_model.CpModel()

    # Define next[i] variables
    # next[0] ranges from 1 to N, next[1..N] ranges from 1 to N+1
    next_vars = [model.NewIntVar(1, N, 'next_0')]
    for i in range(1, N + 1):
        next_vars.append(model.NewIntVar(1, N + 1, f'next_{i}'))

    # Define arc variables: arc[i][j] is true if next[i] = j
    arc = {}
    for i in range(N + 1):
        possible_next = range(1, N + 1) if i == 0 else range(1, N + 2)
        arc[i] = {}
        for j in possible_next:
            arc[i][j] = model.NewBoolVar(f'arc_{i}_{j}')
            model.Add(next_vars[i] == j).OnlyEnforceIf(arc[i][j])
            model.Add(next_vars[i] != j).OnlyEnforceIf(arc[i][j].Not())

    # Add dummy arc from N+1 back to 0
    arc[N + 1] = {0: model.NewBoolVar('arc_{N+1}_0')}
    model.Add(arc[N + 1][0] == 1)  # Force this arc to be used

    # Circuit constraint: prepare arcs for AddCircuit
    arcs = []
    for i in range(N + 1):
        possible_next = range(1, N + 1) if i == 0 else range(1, N + 2)
        for j in possible_next:
            arcs.append((i, j, arc[i][j]))
    arcs.append((N + 1, 0, arc[N + 1][0]))  # Dummy arc

    model.AddCircuit(arcs)

    # Time variables for customers
    T = [model.NewIntVar(e[i], l[i], f'T_{i}') for i in range(1, N + 1)]

    # Timing constraints
    for j in range(1, N + 1):
        # From warehouse to customer j
        model.Add(T[j - 1] >= t0 + t[0][j]).OnlyEnforceIf(arc[0][j])
        # From customer i to customer j
        for i in range(1, N + 1):
            if j <= N and i != j:
                model.Add(T[j - 1] >= T[i - 1] + d[i] + t[i][j]).OnlyEnforceIf(arc[i][j])
            # No timing constraint needed for next[i] = N+1 (end)

    # Objective: Minimize total travel time
    travel_time = []
    for i in range(N + 1):
        for j in range(1, N + 1):  # Exclude N+1 in objective
            if i != j:
                travel_time.append(t[i][j] * arc[i][j])
    model.Minimize(sum(travel_time))

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Extract the route\
        print("Optimal solution", solver.ObjectiveValue())
        route = []
        current = 0
        while True:
            next_node = solver.Value(next_vars[current])
            if next_node == N + 1:
                break
            route.append(next_node)
            current = next_node
        # Output
        print(N)
        print(' '.join(map(str, route)))
    else:
        print("No feasible solution found.")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    solve_delivery_route()