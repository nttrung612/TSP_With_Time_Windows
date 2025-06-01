import random
import sys

def generate_feasible_tsp_tw(n, max_service_time=50, max_travel_time=100, time_window_slack=30, seed=None):
    """
    Generates a feasible TSP with Time Windows instance.
    Ensures at least one feasible route exists.

    Args:
        n (int): Number of customers (excluding depot).
        max_service_time (int): Maximum service time for a customer.
        max_travel_time (int): Maximum travel time between any two locations.
        time_window_slack (int): Slack to create wider time windows around feasible arrival times.
        seed (int, optional): Seed for random number generation.
    
    Returns:
        tuple: (e, l, d, t, feasible_route_nodes)
            e: list of earliest start times (index 0 for depot)
            l: list of latest start times (index 0 for depot)
            d: list of service durations (index 0 for depot)
            t: 2D list (matrix) of travel times
            feasible_route_nodes: list of nodes in the generated feasible route (excluding depot)
    """
    if seed is not None:
        random.seed(seed)

    customer_nodes = list(range(1, n + 1))
    random.shuffle(customer_nodes)

    t = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        for j in range(i + 1, n + 1):
            travel = random.randint(10, max_travel_time)
            t[i][j] = t[j][i] = travel

    d = [0] + [random.randint(5, max_service_time) for _ in range(n)]

    feasible_route_with_depot = [0] + customer_nodes 

    arrival_time = [0] * (n + 1)
    current_time = 0
    departure_time_at_prev = 0 # Time of departure from previous node

    for k in range(len(feasible_route_with_depot) - 1):
        u = feasible_route_with_depot[k]
        v = feasible_route_with_depot[k+1]
        
        current_time = departure_time_at_prev + t[u][v]
        arrival_time[v] = current_time
        
        departure_time_at_prev = arrival_time[v] + d[v]


    e = [0] * (n + 1) # Earliest start service time
    l = [0] * (n + 1) # Latest start service time

    e[0] = 0
    l[0] = departure_time_at_prev + time_window_slack

    for node_idx in customer_nodes:
        feasible_arrival = arrival_time[node_idx]
        
        e[node_idx] = max(0, feasible_arrival - random.randint(0, time_window_slack // 2))
        l_candidate = feasible_arrival + random.randint(0, time_window_slack)
        l[node_idx] = max(l_candidate, e[node_idx]) # Ensure l_i >= e_i

        # Sanity check: ensure l_i >= e_i
        if l[node_idx] < e[node_idx]:
            l[node_idx] = e[node_idx]

    return e, l, d, t, customer_nodes

def save_to_file(filename, n, e, l, d, t):
    with open(filename, "w") as f:
        f.write(str(n) + "\n")
        for i in range(1, n + 1):
            f.write(f"{e[i]} {l[i]} {d[i]}\n")
        for i in range(n + 1):
            f.write(" ".join(map(str, t[i])) + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python this_script_name.py <N_customers> [output_filename] [seed]")
        print("Example: python this_script_name.py 5 input_generated.txt 123")
        sys.exit(1)

    n_customers = int(sys.argv[1])
    output_file = "input.txt"
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    seed_value = None
    if len(sys.argv) > 3:
        seed_value = int(sys.argv[3])

    e_list, l_list, d_list, t_matrix, feasible_perm = generate_feasible_tsp_tw(
        n_customers,
        max_service_time=30,
        max_travel_time=60,
        time_window_slack=40,
        seed=seed_value
    )
    
    save_to_file(output_file, n_customers, e_list, l_list, d_list, t_matrix)
    print(f"Generated TSPTW instance with {n_customers} customers saved to {output_file}")
    print(f"A feasible permutation (excluding depot): {feasible_perm}")