import random
import time
from typing import List, Tuple, Optional
import sys
from collections import defaultdict

class TSPTimeWindows:
    def __init__(self, n: int, time_windows: List[Tuple[int, int, int]], travel_matrix: List[List[int]], start_time: int = 0):
        """
        Initialize TSP with Time Windows problem - Optimized for large instances
        """
        self.n = n
        self.time_windows = time_windows  # e(i), l(i), d(i) for customers 1..n
        self.travel_matrix = travel_matrix
        self.start_time = start_time
        
        # Precompute useful data structures for speed
        self.customer_by_deadline = sorted(range(1, n + 1), key=lambda x: self.time_windows[x-1][1])
        self.customer_by_urgency = sorted(range(1, n + 1), key=lambda x: (self.time_windows[x-1][1] - self.time_windows[x-1][0]))
        
    def fast_feasibility_check(self, route: List[int]) -> Tuple[int, bool]:
        """
        Fast feasibility check with early termination
        Returns (total_travel_time, is_feasible)
        """
        if not route:
            return 0, True
        
        current_time = self.start_time
        current_location = 0
        total_travel_time = 0
        
        for customer in route:
            # Travel to customer
            travel_time = self.travel_matrix[current_location][customer]
            total_travel_time += travel_time
            current_time += travel_time
            
            # Check time window
            earliest, latest, service_duration = self.time_windows[customer - 1]
            
            # Wait if early
            if current_time < earliest:
                current_time = earliest
            
            # Early termination if too late
            if current_time > latest:
                return float('inf'), False
            
            # Service customer
            current_time += service_duration
            current_location = customer
        
        # Return to depot
        total_travel_time += self.travel_matrix[current_location][0]
        return total_travel_time, True
    
    def construct_solution_nearest_neighbor_with_time(self) -> Optional[List[int]]:
        """
        Fast construction using nearest neighbor with time window awareness
        """
        unvisited = set(range(1, self.n + 1))
        route = []
        current_location = 0
        current_time = self.start_time
        
        while unvisited:
            best_customer = None
            best_score = float('inf')
            
            # Limit candidates to speed up (consider only closest 20 + urgent ones)
            candidates = []
            
            # Add closest customers
            distances = [(self.travel_matrix[current_location][c], c) for c in unvisited]
            distances.sort()
            candidates.extend([c for _, c in distances[:min(20, len(distances))]])
            
            # Add urgent customers (tight time windows)
            for customer in unvisited:
                earliest, latest, _ = self.time_windows[customer - 1]
                if latest - earliest <= 50:  # Tight window
                    candidates.append(customer)
            
            candidates = list(set(candidates))  # Remove duplicates
            
            for customer in candidates:
                travel_time = self.travel_matrix[current_location][customer]
                arrival_time = current_time + travel_time
                earliest, latest, service_duration = self.time_windows[customer - 1]
                
                # Skip if impossible
                if arrival_time > latest:
                    continue
                
                # Score: travel_time + waiting_time + urgency_bonus
                waiting_time = max(0, earliest - arrival_time)
                urgency_bonus = -(latest - max(arrival_time, earliest))  # Prefer urgent
                score = travel_time + waiting_time + urgency_bonus * 0.1
                
                if score < best_score:
                    best_score = score
                    best_customer = customer
            
            if best_customer is None:
                # Fallback: choose any feasible customer
                for customer in unvisited:
                    travel_time = self.travel_matrix[current_location][customer]
                    arrival_time = current_time + travel_time
                    latest = self.time_windows[customer - 1][1]
                    if arrival_time <= latest:
                        best_customer = customer
                        break
            
            if best_customer is None:
                return None  # No feasible solution
            
            route.append(best_customer)
            unvisited.remove(best_customer)
            
            # Update position and time
            travel_time = self.travel_matrix[current_location][best_customer]
            current_time += travel_time
            earliest, latest, service_duration = self.time_windows[best_customer - 1]
            current_time = max(current_time, earliest) + service_duration
            current_location = best_customer
        
        return route
    
    def construct_solution_deadline_insertion(self) -> Optional[List[int]]:
        """
        Fast construction by deadline with limited insertion attempts
        """
        route = []
        
        for customer in self.customer_by_deadline:
            # Try to insert at best position (limit search to speed up)
            best_position = 0
            best_cost = float('inf')
            found_feasible = False
            
            # Limit positions to check for large routes
            max_positions = min(len(route) + 1, 10)
            step = max(1, (len(route) + 1) // max_positions)
            
            positions_to_try = list(range(0, len(route) + 1, step))
            if len(route) not in positions_to_try:
                positions_to_try.append(len(route))
            
            for position in positions_to_try:
                test_route = route[:position] + [customer] + route[position:]
                cost, feasible = self.fast_feasibility_check(test_route)
                
                if feasible and cost < best_cost:
                    best_position = position
                    best_cost = cost
                    found_feasible = True
            
            if not found_feasible:
                return None
            
            route.insert(best_position, customer)
        
        return route
    
    def get_initial_solution(self) -> List[int]:
        """
        Get initial solution with multiple fast heuristics
        """
        solutions = []
        
        # Try nearest neighbor
        sol1 = self.construct_solution_nearest_neighbor_with_time()
        if sol1:
            cost, feasible = self.fast_feasibility_check(sol1)
            if feasible:
                solutions.append((sol1, cost))
        
        # Try deadline insertion
        sol2 = self.construct_solution_deadline_insertion()
        if sol2:
            cost, feasible = self.fast_feasibility_check(sol2)
            if feasible:
                solutions.append((sol2, cost))
        
        # Try random solutions (quick generation)
        for _ in range(3):
            random_route = self.customer_by_deadline[:]
            random.shuffle(random_route)
            cost, feasible = self.fast_feasibility_check(random_route)
            if feasible:
                solutions.append((random_route, cost))
        
        if not solutions:
            # Fallback
            return self.customer_by_deadline[:]
        
        # Return best solution
        return min(solutions, key=lambda x: x[1])[0]
    
    def fast_2opt(self, route: List[int], max_attempts: int = 1000) -> Tuple[List[int], int]:
        """
        Fast 2-opt with limited attempts and early stopping
        """
        current_route = route[:]
        current_cost, feasible = self.fast_feasibility_check(current_route)
        
        if not feasible:
            return current_route, current_cost
        
        improved = True
        attempts = 0
        
        while improved and attempts < max_attempts:
            improved = False
            attempts += 1
            
            # Randomize order of attempts for better exploration
            indices = list(range(len(current_route)))
            random.shuffle(indices)
            
            for i in indices[:min(50, len(indices))]:  # Limit attempts
                for j in range(i + 2, min(i + 20, len(current_route))):  # Local window
                    # Quick 2-opt swap
                    new_route = current_route[:]
                    new_route[i:j+1] = reversed(new_route[i:j+1])
                    
                    new_cost, new_feasible = self.fast_feasibility_check(new_route)
                    
                    if new_feasible and new_cost < current_cost:
                        current_route = new_route
                        current_cost = new_cost
                        improved = True
                        break
                
                if improved:
                    break
        
        return current_route, current_cost
    
    def fast_relocate(self, route: List[int], max_attempts: int = 500) -> Tuple[List[int], int]:
        """
        Fast relocation with limited attempts
        """
        current_route = route[:]
        current_cost, feasible = self.fast_feasibility_check(current_route)
        
        if not feasible:
            return current_route, current_cost
        
        improved = True
        attempts = 0
        
        while improved and attempts < max_attempts:
            improved = False
            attempts += 1
            
            # Try relocating customers (limited scope)
            for i in range(len(current_route)):
                customer = current_route[i]
                
                # Try inserting at a few positions around current position
                positions = []
                for offset in [-5, -3, -1, 1, 3, 5]:
                    new_pos = i + offset
                    if 0 <= new_pos <= len(current_route) - 1:
                        positions.append(new_pos)
                
                for j in positions:
                    if i == j:
                        continue
                    
                    new_route = current_route[:]
                    new_route.pop(i)
                    insert_pos = j if j < i else j - 1
                    new_route.insert(insert_pos, customer)
                    
                    new_cost, new_feasible = self.fast_feasibility_check(new_route)
                    
                    if new_feasible and new_cost < current_cost:
                        current_route = new_route
                        current_cost = new_cost
                        improved = True
                        break
                
                if improved:
                    break
        
        return current_route, current_cost
    
    def local_search_optimized(self, time_limit: float = 30.0) -> Tuple[List[int], int]:
        """
        Optimized local search with time limit and adaptive strategies
        """
        start_time = time.time()
        
        # Get initial solution
        current_route = self.get_initial_solution()
        current_cost, feasible = self.fast_feasibility_check(current_route)
        
        if not feasible:
            print("Warning: No feasible initial solution found", file=sys.stderr)
            return current_route, current_cost
        
        best_route = current_route[:]
        best_cost = current_cost
        
        iteration = 0
        
        while time.time() - start_time < time_limit:
            iteration += 1
            
            # Apply 2-opt
            if iteration % 2 == 0:
                new_route, new_cost = self.fast_2opt(current_route, max_attempts=200)
            else:
                new_route, new_cost = self.fast_relocate(current_route, max_attempts=200)
            
            if new_cost < current_cost:
                current_route = new_route
                current_cost = new_cost
                
                if new_cost < best_cost:
                    best_route = new_route[:]
                    best_cost = new_cost
            else:
                # Diversification: small random perturbation
                if iteration % 10 == 0 and len(current_route) > 4:
                    # Swap two random customers
                    i, j = random.sample(range(len(current_route)), 2)
                    current_route[i], current_route[j] = current_route[j], current_route[i]
                    current_cost, _ = self.fast_feasibility_check(current_route)
        
        return best_route, best_cost

def solve_tsp_time_windows():
    """Main function to solve TSP with Time Windows - Optimized Version"""
    # Read input
    n = int(input().strip())
    
    # Read time windows
    time_windows = []
    for i in range(n):
        e, l, d = map(int, input().strip().split())
        time_windows.append((e, l, d))
    
    # Read travel matrix
    travel_matrix = []
    for i in range(n + 1):
        row = list(map(int, input().strip().split()))
        travel_matrix.append(row)
    
    # Create TSP solver
    tsp = TSPTimeWindows(n, time_windows, travel_matrix)
    
    # Solve using optimized local search
    best_route, best_cost = tsp.local_search_optimized()
    
    # Output result
    print(n)
    print(*best_route)
    print(best_cost)

if __name__ == "__main__":
    solve_tsp_time_windows()